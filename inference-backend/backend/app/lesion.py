"""Honest runtime loading for genuinely trained lesion evidence models."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from .lesion_model import LesionSegmentationNet


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rle(binary_mask: np.ndarray) -> list[int]:
    """Run-length encode a real binary prediction mask in row-major order."""
    flattened = binary_mask.astype(np.uint8).reshape(-1)
    if not flattened.any():
        return []
    padded = np.concatenate(([0], flattened, [0]))
    changes = np.flatnonzero(padded[1:] != padded[:-1]) + 1
    runs = changes.reshape(-1, 2)
    result: list[int] = []
    for start, end in runs:
        result.extend((int(start - 1), int(end - start)))
    return result


@dataclass(frozen=True)
class LesionEvidenceService:
    """A loaded model only when its real-label provenance can be verified."""

    ready: bool
    reason: str
    model: LesionSegmentationNet | None = None
    classes: tuple[dict[str, str], ...] = ()
    image_size: int | None = None
    threshold: float | None = None
    model_version: str | None = None
    test_metrics: dict[str, Any] | None = None

    @classmethod
    def unavailable(cls, reason: str) -> "LesionEvidenceService":
        return cls(ready=False, reason=reason)

    def status(self) -> dict[str, Any]:
        if not self.ready:
            return {
                "status": "not_available",
                "reason": self.reason,
                "model_ready": False,
                "clinically_validated": False,
                "required_for_readiness": [
                    "有来源与许可记录的真实病灶像素级标注",
                    "严格分开的训练、验证和测试清单",
                    "已训练权重、配置、独立测试指标与清单 SHA-256",
                ],
            }
        return {
            "status": "available",
            "reason": "已加载有真实像素标注来源与独立测试工件的病灶分割模型。",
            "model_ready": True,
            "model_version": self.model_version,
            "classes": list(self.classes),
            "threshold": self.threshold,
            "test_metrics": self.test_metrics,
            "clinically_validated": False,
        }

    def analyze(self, image: Image.Image) -> dict[str, Any]:
        if not self.ready or self.model is None or self.image_size is None or self.threshold is None:
            return self.status()
        transform = transforms.Compose(
            [
                transforms.Resize((self.image_size, self.image_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ]
        )
        with torch.inference_mode():
            logits = self.model(transform(image.convert("RGB")).unsqueeze(0))
            probabilities = torch.sigmoid(logits)[0].cpu().numpy()
        predictions: list[dict[str, Any]] = []
        for class_config, probability_map in zip(self.classes, probabilities):
            binary_mask = probability_map >= self.threshold
            predictions.append(
                {
                    "class_id": class_config["id"],
                    "label": class_config["label"],
                    "status": "model_prediction",
                    "mean_probability": round(float(probability_map.mean()), 6),
                    "foreground_pixel_count": int(binary_mask.sum()),
                    "foreground_fraction": round(float(binary_mask.mean()), 6),
                    "mask_encoding": "rle_row_major",
                    "mask_shape": [int(binary_mask.shape[0]), int(binary_mask.shape[1])],
                    "mask_rle": _rle(binary_mask),
                }
            )
        return {
            **self.status(),
            "status": "available",
            "evidence_type": "actual_model_predicted_segmentation_masks",
            "message": "以下为加载的病灶分割模型实际输出的掩膜编码，不是 CAM、占位框或生成热力图。",
            "predictions": predictions,
        }


def load_lesion_evidence_model(artifact_dir: Path) -> LesionEvidenceService:
    """Reject incomplete or unproven artifacts instead of fabricating evidence."""
    paths = {
        "weights": artifact_dir / "best_model.pt",
        "config": artifact_dir / "model_config.json",
        "metrics": artifact_dir / "metrics.json",
    }
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        return LesionEvidenceService.unavailable(
            f"病灶模型未就绪：缺少 {', '.join(missing)} 工件。当前不会生成病灶框、掩膜或热力图。"
        )
    try:
        config = json.loads(paths["config"].read_text(encoding="utf-8"))
        metrics = json.loads(paths["metrics"].read_text(encoding="utf-8"))
        classes = config.get("classes")
        if (
            config.get("architecture") != LesionSegmentationNet.architecture
            or config.get("task") != "multi_label_semantic_segmentation"
            or config.get("trained_with_real_annotations") is not True
            or not isinstance(classes, list)
            or not classes
            or metrics.get("test_evaluation", {}).get("status") != "completed"
            or metrics.get("manifest_sha256") != config.get("manifest_sha256")
            or config.get("weights_sha256") != _sha256(paths["weights"])
        ):
            return LesionEvidenceService.unavailable(
                "病灶工件缺少可验证的真实标注、独立测试或权重来源信息；不会作为证据加载。"
            )
        normalised_classes = tuple(
            {"id": str(item["id"]), "label": str(item["label"])} for item in classes
        )
        image_size = int(config["image_size"])
        threshold = float(config["probability_threshold"])
        if image_size < 64 or not 0 < threshold < 1:
            raise ValueError("图像尺寸或掩膜阈值不合法。")
        model = LesionSegmentationNet(len(normalised_classes), int(config.get("base_channels", 24)))
        model.load_state_dict(torch.load(paths["weights"], map_location="cpu", weights_only=True))
        model.eval()
        return LesionEvidenceService(
            ready=True,
            reason="工件已通过运行时来源校验。",
            model=model,
            classes=normalised_classes,
            image_size=image_size,
            threshold=threshold,
            model_version=str(config.get("model_version", "lesion-evidence-v1")),
            test_metrics=metrics.get("test_evaluation"),
        )
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError, RuntimeError) as error:
        return LesionEvidenceService.unavailable(f"无法验证或加载病灶工件：{error}")
