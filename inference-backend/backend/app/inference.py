from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms

from .config import LESION_ARTIFACT_DIR, PHASE3_ARTIFACT_DIR
from .lesion import LesionEvidenceService, load_lesion_evidence_model
from .phase3 import Phase3Artifacts, load_phase3_artifacts


LEVELS = (
    "无明显 DR",
    "轻度非增殖性 DR（轻度 NPDR）",
    "中度非增殖性 DR（中度 NPDR）",
    "重度非增殖性 DR（重度 NPDR）",
    "增殖性 DR（PDR）",
)
MODEL_VERSION = "resnet18-imagenet-aptos-v1"
TECHNICAL_CHECK_VERSION = "basic-technical-quality-v1-demo"
CONSENSUS_VERSION = "dm-consensus-v1-demo"
CONSENSUS_V2_VERSION = "dm-consensus-v2-evidence-gated-demo"

# These are deliberately simple competition-demo thresholds. They are not a
# clinically validated image-quality model, OOD detector, or treatment rule.
TECHNICAL_THRESHOLDS = {
    "minimum_short_edge_px": 224,
    "brightness_range": [20, 235],
    "minimum_contrast_std": 12,
}
CONSENSUS_THRESHOLDS = {
    "minimum_top1_confidence": 0.60,
    "minimum_top1_top2_margin": 0.20,
    "maximum_entropy": 1.20,
}


def crop_black_border(image: Image.Image, threshold: int = 10) -> Image.Image:
    grayscale = np.asarray(image.convert("L"))
    mask = grayscale > threshold
    if not mask.any():
        return image
    rows, columns = np.where(mask)
    return image.crop((int(columns.min()), int(rows.min()), int(columns.max()) + 1, int(rows.max()) + 1))


def basic_technical_check(image: Image.Image) -> dict[str, Any]:
    """Return transparent, non-clinical technical image checks and evidence."""
    grayscale = np.asarray(image.convert("L"), dtype=np.float32)
    width, height = image.size
    brightness = float(grayscale.mean())
    contrast = float(grayscale.std())
    short_edge = min(width, height)

    size_ok = short_edge >= TECHNICAL_THRESHOLDS["minimum_short_edge_px"]
    brightness_low, brightness_high = TECHNICAL_THRESHOLDS["brightness_range"]
    brightness_ok = brightness_low <= brightness <= brightness_high
    contrast_ok = contrast >= TECHNICAL_THRESHOLDS["minimum_contrast_std"]
    passed = size_ok and brightness_ok and contrast_ok

    evidence = [
        {
            "id": "image_dimensions",
            "label": "图像尺寸",
            "status": "pass" if size_ok else "fail",
            "observed": {"width_px": width, "height_px": height, "short_edge_px": short_edge},
            "threshold": {"minimum_short_edge_px": TECHNICAL_THRESHOLDS["minimum_short_edge_px"]},
            "message": "图像短边满足基础输入尺寸要求。" if size_ok else "图像短边低于 224 像素。",
        },
        {
            "id": "brightness",
            "label": "平均亮度",
            "status": "pass" if brightness_ok else "fail",
            "observed": {"mean_grayscale": round(brightness, 2)},
            "threshold": {"minimum": brightness_low, "maximum": brightness_high},
            "message": "平均亮度位于演示范围内。" if brightness_ok else "图像过暗或过亮。",
        },
        {
            "id": "contrast",
            "label": "灰度对比度",
            "status": "pass" if contrast_ok else "fail",
            "observed": {"grayscale_std": round(contrast, 2)},
            "threshold": {"minimum_grayscale_std": TECHNICAL_THRESHOLDS["minimum_contrast_std"]},
            "message": "灰度对比度满足演示范围。" if contrast_ok else "图像对比度不足。",
        },
    ]
    failures = [item["message"] for item in evidence if item["status"] == "fail"]
    return {
        "status": "pass" if passed else "review_required",
        "score": round(float(sum((size_ok, brightness_ok, contrast_ok)) / 3), 6),
        "message": "基础技术检查通过（非临床图像质量模型）。" if passed else "；".join(failures),
        "version": TECHNICAL_CHECK_VERSION,
        "clinically_validated": False,
        "thresholds": TECHNICAL_THRESHOLDS,
        "width": width,
        "height": height,
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "evidence": evidence,
    }


def dm_consensus_v1(
    probabilities: list[float],
    technical_check: dict[str, Any],
) -> dict[str, Any]:
    """Apply demonstrative quality and uncertainty gates to one prediction.

    The thresholds are for a competition demo only. This function does not
    establish clinical validity and does not replace mandatory clinician review.
    """
    probs = np.asarray(probabilities, dtype=np.float64).reshape(-1)
    if probs.size < 2 or not np.isfinite(probs).all() or (probs < 0).any() or probs.sum() <= 0:
        raise ValueError("DM-Consensus 需要至少两个有效的非负类别概率。")
    probs = probs / probs.sum()

    ranked_indices = np.argsort(probs)[::-1]
    top1 = float(probs[ranked_indices[0]])
    top2 = float(probs[ranked_indices[1]])
    margin = top1 - top2
    entropy = float(-(probs * np.log(probs + 1e-12)).sum())
    normalized_entropy = entropy / float(np.log(probs.size))
    quality_passed = technical_check.get("status") == "pass"

    confidence_passed = top1 >= CONSENSUS_THRESHOLDS["minimum_top1_confidence"]
    margin_passed = margin >= CONSENSUS_THRESHOLDS["minimum_top1_top2_margin"]
    entropy_passed = entropy <= CONSENSUS_THRESHOLDS["maximum_entropy"]

    if not quality_passed:
        status = "reject"
        reason_code = "technical_quality_gate_failed"
        reason = "基础技术质量检查未通过；请重新采集图像并由人工复核。"
    elif not confidence_passed:
        status = "review"
        reason_code = "top1_confidence_below_demo_threshold"
        reason = "模型最高类别概率低于 60% 演示阈值，建议人工复核。"
    elif not margin_passed:
        status = "review"
        reason_code = "top1_top2_margin_below_demo_threshold"
        reason = "最高与次高类别概率差距较小，等级不确定性较高，建议人工复核。"
    elif not entropy_passed:
        status = "review"
        reason_code = "entropy_above_demo_threshold"
        reason = "五级概率分布熵较高，模型不确定性较高，建议人工复核。"
    else:
        status = "accept"
        reason_code = "all_demo_gates_passed"
        reason = "基础技术检查和 DM-Consensus v1 演示阈值均通过；仍必须由专业人员复核。"

    evidence = [
        {
            "id": "technical_quality_gate",
            "label": "基础技术质量门控",
            "status": "pass" if quality_passed else "reject",
            "observed": {"technical_status": technical_check.get("status"), "technical_score": technical_check.get("score")},
            "threshold": {"required_status": "pass"},
            "message": "基础技术质量检查通过。" if quality_passed else "基础技术质量检查未通过。",
        },
        {
            "id": "top1_confidence",
            "label": "Top-1 置信度",
            "status": "pass" if confidence_passed else "review",
            "observed": {"value": round(top1, 6), "top1_grade": int(ranked_indices[0])},
            "threshold": {"minimum": CONSENSUS_THRESHOLDS["minimum_top1_confidence"]},
            "message": "最高类别概率满足演示阈值。" if confidence_passed else "最高类别概率低于演示阈值。",
        },
        {
            "id": "top1_top2_margin",
            "label": "Top-1 / Top-2 差距",
            "status": "pass" if margin_passed else "review",
            "observed": {"value": round(margin, 6), "top2_grade": int(ranked_indices[1])},
            "threshold": {"minimum": CONSENSUS_THRESHOLDS["minimum_top1_top2_margin"]},
            "message": "最高与次高类别差距满足演示阈值。" if margin_passed else "最高与次高类别差距低于演示阈值。",
        },
        {
            "id": "prediction_entropy",
            "label": "五级预测熵",
            "status": "pass" if entropy_passed else "review",
            "observed": {"value": round(entropy, 6), "normalized_value": round(normalized_entropy, 6)},
            "threshold": {"maximum": CONSENSUS_THRESHOLDS["maximum_entropy"]},
            "message": "预测熵位于演示范围。" if entropy_passed else "预测熵高于演示阈值。",
        },
    ]
    return {
        "status": status,
        "reason_code": reason_code,
        "reason": reason,
        "top1_confidence": round(top1, 6),
        "top2_confidence": round(top2, 6),
        "margin": round(margin, 6),
        "entropy": round(entropy, 6),
        "normalized_entropy": round(normalized_entropy, 6),
        "thresholds": CONSENSUS_THRESHOLDS,
        "evidence": evidence,
        "version": CONSENSUS_VERSION,
        "clinically_validated": False,
    }


def dm_consensus_v2(
    base_consensus: dict[str, Any],
    phase3_result: dict[str, Any],
    lesion_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Add internal uncertainty and genuine-lesion readiness to consensus.

    This is intentionally a review gate.  A missing lesion model can never be
    silently treated as positive lesion evidence or as a reason to auto-pass.
    Internal reference distance remains distinct from externally validated OOD.
    """
    phase3_available = phase3_result.get("status") == "available"
    lesion_available = lesion_evidence.get("status") == "available"
    conformal = phase3_result.get("conformal_prediction", {})
    anomaly = phase3_result.get("reference_anomaly_screen", {})
    set_size = int(conformal.get("prediction_set_size", 0))
    if base_consensus["status"] == "reject":
        status = "reject"
        reason_code = "base_technical_quality_gate_failed"
        reason = base_consensus["reason"]
    elif not lesion_available:
        status = "review"
        reason_code = "lesion_evidence_unavailable"
        reason = "病灶证据模型尚未通过真实标注训练与独立测试验证；系统不会将缺失证据当作通过，建议人工复核。"
    elif phase3_available and anomaly.get("status") == "review_reference_outlier":
        status = "review"
        reason_code = "reference_feature_outlier"
        reason = "输入特征相对内部 APTOS 参考分布不典型，建议人工复核。"
    elif phase3_available and set_size != 1:
        status = "review"
        reason_code = "conformal_prediction_set_not_singleton"
        reason = "Conformal 预测集合不是单一等级，等级不确定性较高，建议人工复核。"
    elif base_consensus["status"] != "accept":
        status = "review"
        reason_code = f"base_{base_consensus['reason_code']}"
        reason = base_consensus["reason"]
    elif phase3_available:
        status = "accept"
        reason_code = "all_phase2_and_phase3_demo_gates_passed"
        reason = "基础门控、已加载的内部不确定性工件与真实病灶模型均未触发复核规则；仍必须由专业人员复核。"
    else:
        status = "accept"
        reason_code = "base_gates_and_real_lesion_evidence_available"
        reason = "基础门控与真实病灶模型均已完成；内部校准/Conformal 工件未就绪，仍必须由专业人员复核。"

    evidence = [
        {
            "id": "phase2_base_consensus",
            "label": "Phase 2 基础共识",
            "status": base_consensus["status"],
            "observed": {"status": base_consensus["status"], "reason_code": base_consensus["reason_code"]},
            "threshold": {"required_status_for_accept": "accept"},
            "message": base_consensus["reason"],
        },
        {
            "id": "lesion_evidence",
            "label": "病灶空间证据",
            "status": "pass" if lesion_available else "review",
            "observed": {
                "status": lesion_evidence.get("status"),
                "model_version": lesion_evidence.get("model_version"),
                "classes": lesion_evidence.get("classes", []),
            },
            "threshold": {"required_status_for_accept": "available"},
            "message": lesion_evidence.get("reason", "病灶模型状态未知。"),
        },
    ]
    if phase3_available:
        evidence.extend(
            [
                {
                    "id": "reference_anomaly_screen",
                    "label": "内部参考特征筛查（不是正式 OOD）",
                    "status": "review" if anomaly.get("status") == "review_reference_outlier" else "pass",
                    "observed": {"distance": anomaly.get("distance")},
                    "threshold": {"maximum": anomaly.get("threshold")},
                    "message": anomaly.get("message", "内部参考筛查已加载。"),
                },
                {
                    "id": "conformal_prediction_set",
                    "label": "Conformal 预测集合",
                    "status": "pass" if set_size == 1 else "review",
                    "observed": {
                        "grades": conformal.get("prediction_set_grades", []),
                        "set_size": set_size,
                        "target_coverage": conformal.get("target_coverage"),
                    },
                    "threshold": {"required_set_size_for_accept": 1},
                    "message": "预测集合为单一等级。" if set_size == 1 else "预测集合包含多个或零个等级。",
                },
            ]
        )
    return {
        "status": status,
        "reason_code": reason_code,
        "reason": reason,
        "top1_confidence": base_consensus["top1_confidence"],
        "top2_confidence": base_consensus["top2_confidence"],
        "margin": base_consensus["margin"],
        "entropy": base_consensus["entropy"],
        "normalized_entropy": base_consensus["normalized_entropy"],
        "calibrated_top1_confidence": (
            round(float(max(phase3_result["temperature_calibration"]["calibrated_probabilities"])), 6)
            if phase3_available
            else None
        ),
        "thresholds": base_consensus["thresholds"],
        "base_consensus": base_consensus,
        "evidence": evidence,
        "version": CONSENSUS_V2_VERSION,
        "clinically_validated": False,
        "lesion_evidence_status": lesion_evidence.get("status"),
        "limitations": [
            *phase3_result.get("limitations", []),
            "病灶空间证据只会在有真实标注训练、独立测试和可验证权重时参与共识。",
        ],
    }


def build_evidence_chain(
    probabilities: list[float],
    predicted_grade: int,
    technical_check: dict[str, Any],
    consensus: dict[str, Any],
    phase3_result: dict[str, Any],
    lesion_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Build a persisted, human-readable chain of the demo's actual evidence."""
    return {
        "version": "dr-evidence-chain-v1-demo",
        "clinically_validated": False,
        "scope_notice": "本证据链仅说明竞赛演示中实际执行的规则，不能用于临床诊断或治疗决策。",
        "stages": [
            {
                "id": "technical_quality",
                "label": "基础技术质量检查",
                "status": technical_check["status"],
                "summary": technical_check["message"],
                "evidence": technical_check["evidence"],
            },
            {
                "id": "five_class_model",
                "label": "ResNet18 五级 DR 分类",
                "status": "informational",
                "summary": "输出为 Softmax 类别概率；概率不是临床可靠性。",
                "model_version": MODEL_VERSION,
                "predicted_grade": predicted_grade,
                "probabilities": [round(float(value), 6) for value in probabilities],
            },
            {
                "id": "lesion_evidence",
                "label": "病灶空间证据",
                "status": lesion_evidence.get("status", "not_available"),
                "summary": lesion_evidence.get("reason", "病灶模型状态未知。"),
                "evidence": lesion_evidence,
            },
            {
                "id": consensus["version"].replace("-", "_"),
                "label": "DM-Consensus 2.0" if consensus["version"] == CONSENSUS_V2_VERSION else "DM-Consensus v1",
                "status": consensus["status"],
                "summary": consensus["reason"],
                "evidence": consensus["evidence"],
            },
        ],
        "phase_3": phase3_result,
        "phase_3_not_implemented": (
            []
            if lesion_evidence.get("status") == "available"
            else [{"module": "病灶检测", "status": "not_available", "phase": "Phase 3"}]
        ),
    }


class DRInferenceService:
    def __init__(self, model_path: Path) -> None:
        if not model_path.is_file():
            raise FileNotFoundError(
                f"找不到模型权重：{model_path}。请先运行训练脚本，或设置 DR_MODEL_PATH。"
            )
        self.device = torch.device("cpu")
        self.model = models.resnet18(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, len(LEVELS))
        state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
        self.model.to(self.device).eval()
        self.phase3_artifacts: Phase3Artifacts = load_phase3_artifacts(PHASE3_ARTIFACT_DIR, model_path)
        self.lesion_evidence: LesionEvidenceService = load_lesion_evidence_model(LESION_ARTIFACT_DIR)
        self.preprocess = transforms.Compose(
            [
                transforms.Resize(round(224 * 1.15)),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ]
        )

    def _forward_with_features(self, model_input: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Return ResNet18 logits and the feature vector immediately before fc."""
        features = self.model.conv1(model_input)
        features = self.model.bn1(features)
        features = self.model.relu(features)
        features = self.model.maxpool(features)
        features = self.model.layer1(features)
        features = self.model.layer2(features)
        features = self.model.layer3(features)
        features = self.model.layer4(features)
        features = self.model.avgpool(features)
        features = torch.flatten(features, 1)
        return self.model.fc(features), features

    def analyze(self, image_path: Path) -> dict[str, Any]:
        """Analyse a persisted image used by the local case-record workflow."""
        with Image.open(image_path) as source_image:
            image = source_image.convert("RGB").copy()
        return self.analyze_image(image)

    def analyze_bytes(self, image_bytes: bytes) -> dict[str, Any]:
        """Analyse an uploaded image without writing it to permanent storage."""
        try:
            with Image.open(BytesIO(image_bytes)) as source_image:
                image = source_image.convert("RGB").copy()
        except (OSError, ValueError) as error:
            raise ValueError("上传文件不是可读取的图像。") from error
        return self.analyze_image(image)

    def analyze_image(self, image: Image.Image) -> dict[str, Any]:
        """Run the trained five-class model and the non-clinical demo gates."""
        technical_check = basic_technical_check(image)
        model_input = self.preprocess(crop_black_border(image)).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            logits, features = self._forward_with_features(model_input)
            probabilities = torch.softmax(logits, dim=1)[0].cpu().tolist()

        predicted_grade = int(np.argmax(probabilities))
        confidence = float(probabilities[predicted_grade])
        base_consensus = dm_consensus_v1(probabilities, technical_check)
        phase3_result = self.phase3_artifacts.evaluate(
            logits[0].cpu().numpy(), features[0].cpu().numpy()
        )
        lesion_evidence = self.lesion_evidence.analyze(image)
        consensus = dm_consensus_v2(base_consensus, phase3_result, lesion_evidence)
        evidence = build_evidence_chain(
            probabilities, predicted_grade, technical_check, consensus, phase3_result, lesion_evidence
        )

        return {
            "predicted_grade": predicted_grade,
            "predicted_label": LEVELS[predicted_grade],
            "confidence": round(confidence, 6),
            "probabilities": [
                {"grade": grade, "label": LEVELS[grade], "probability": round(float(value), 6)}
                for grade, value in enumerate(probabilities)
            ],
            "technical_check": technical_check,
            "consensus": consensus,
            "evidence": evidence,
            "phase3": phase3_result,
            "lesion_evidence": lesion_evidence,
            "needs_review": consensus["status"] != "accept",
            "decision_reason": consensus["reason"],
            "model_version": MODEL_VERSION,
        }
