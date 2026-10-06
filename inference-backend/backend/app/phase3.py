"""Runtime loader for internally evaluated Phase 3 uncertainty artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_CONFORMAL_ALPHA = 0.05


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@dataclass(frozen=True)
class Phase3Artifacts:
    """Validated runtime values, or an honest unavailable state."""

    available: bool
    reason: str
    temperature: float | None = None
    conformal_alpha: float | None = None
    conformal_threshold: float | None = None
    conformal_test_evaluation: dict[str, Any] | None = None
    reference_mean: np.ndarray | None = None
    reference_inverse_variances: np.ndarray | None = None
    reference_distance_threshold: float | None = None
    reference_test_evaluation: dict[str, Any] | None = None
    limitations: tuple[str, ...] = ()

    @classmethod
    def unavailable(cls, reason: str) -> "Phase3Artifacts":
        return cls(available=False, reason=reason)

    def evaluate(self, logits: np.ndarray, features: np.ndarray) -> dict[str, Any]:
        if not self.available:
            return {
                "status": "unavailable",
                "reason": self.reason,
                "clinically_validated": False,
                "phase": "Phase 3",
            }
        assert self.temperature is not None
        assert self.conformal_alpha is not None
        assert self.conformal_threshold is not None
        assert self.reference_mean is not None
        assert self.reference_inverse_variances is not None
        assert self.reference_distance_threshold is not None

        scaled_logits = logits.astype(np.float64) / self.temperature
        shifted_logits = scaled_logits - scaled_logits.max()
        calibrated_probabilities = np.exp(shifted_logits)
        calibrated_probabilities /= calibrated_probabilities.sum()
        prediction_set = np.flatnonzero(calibrated_probabilities >= self.conformal_threshold).astype(int).tolist()
        distance = float(
            np.square(features.astype(np.float64) - self.reference_mean).dot(self.reference_inverse_variances)
        )
        is_reference_outlier = distance > self.reference_distance_threshold
        return {
            "status": "available",
            "clinically_validated": False,
            "temperature_calibration": {
                "method": "single-scalar post-hoc temperature scaling",
                "temperature": round(self.temperature, 6),
                "calibrated_probabilities": [round(float(value), 6) for value in calibrated_probabilities],
            },
            "conformal_prediction": {
                "status": "prediction_set_available",
                "alpha": self.conformal_alpha,
                "target_coverage": round(1 - self.conformal_alpha, 6),
                "probability_inclusion_threshold": round(self.conformal_threshold, 6),
                "prediction_set_grades": prediction_set,
                "prediction_set_size": len(prediction_set),
                "is_singleton": len(prediction_set) == 1,
                "test_evaluation": self.conformal_test_evaluation,
            },
            "reference_anomaly_screen": {
                "status": "review_reference_outlier" if is_reference_outlier else "within_reference",
                "distance": round(distance, 6),
                "threshold": round(self.reference_distance_threshold, 6),
                "strict_test_reference_screen": self.reference_test_evaluation,
                "message": (
                    "特征相对内部 APTOS 校准参考分布不典型，建议人工复核。"
                    if is_reference_outlier
                    else "特征位于内部 APTOS 校准参考阈值内。"
                ),
            },
            "lesion_evidence": {
                "status": "not_available",
                "reason": "当前项目没有病灶位置或分割标注，不能生成可信的病灶证据。",
                "required_for_training": ["病灶框/点标注或像素级分割掩膜", "独立验证集", "病灶级评价指标"],
            },
            "limitations": list(self.limitations),
        }


def load_phase3_artifacts(artifact_dir: Path, model_path: Path) -> Phase3Artifacts:
    """Load only mutually compatible artifacts for the deployed weight file."""
    artifact_paths = {
        "manifest": artifact_dir / "strict_split_manifest.json",
        "temperature": artifact_dir / "temperature_calibration.json",
        "conformal": artifact_dir / "conformal_calibration.json",
        "ood": artifact_dir / "ood_reference.json",
        "reference": artifact_dir / "ood_feature_reference.npz",
    }
    missing = [name for name, path in artifact_paths.items() if not path.is_file()]
    if missing:
        return Phase3Artifacts.unavailable(f"缺少 Phase 3 工件：{', '.join(missing)}。系统继续使用 DM-Consensus v1。")
    try:
        split_manifest = _load_json(artifact_paths["manifest"])
        temperature_artifact = _load_json(artifact_paths["temperature"])
        conformal_artifact = _load_json(artifact_paths["conformal"])
        ood_artifact = _load_json(artifact_paths["ood"])
        expected_model_hash = _sha256(model_path)
        if temperature_artifact.get("model_sha256") != expected_model_hash:
            return Phase3Artifacts.unavailable("Phase 3 温度工件与当前模型权重不匹配。")
        if ood_artifact.get("model_sha256") != expected_model_hash:
            return Phase3Artifacts.unavailable("Phase 3 特征参考工件与当前模型权重不匹配。")
        if split_manifest.get("version") != "strict-dr-split-v2":
            return Phase3Artifacts.unavailable("严格拆分清单版本无效；旧验证集子拆分不会加载到运行时。")
        if temperature_artifact.get("version") != "temperature-scaling-v2-strict":
            return Phase3Artifacts.unavailable("不支持的温度缩放工件版本。")
        if conformal_artifact.get("version") != "split-conformal-v2-strict":
            return Phase3Artifacts.unavailable("不支持的 Conformal 工件版本。")
        if ood_artifact.get("version") != "feature-reference-anomaly-v2-strict":
            return Phase3Artifacts.unavailable("不支持的参考异常筛查工件版本。")

        conformal_result = next(
            (
                item
                for item in conformal_artifact.get("results", [])
                if abs(float(item.get("alpha", -1)) - DEFAULT_CONFORMAL_ALPHA) < 1e-9
            ),
            None,
        )
        if not conformal_result:
            return Phase3Artifacts.unavailable("Conformal 工件没有 alpha=0.05 的运行时配置。")
        temperature = float(temperature_artifact["temperature"])
        threshold = float(conformal_result["probability_inclusion_threshold"])
        reference_distance_threshold = float(ood_artifact["reference_distance_threshold"])
        with np.load(artifact_paths["reference"]) as reference:
            mean = reference["mean"].astype(np.float64)
            inverse_variances = reference["inverse_variances"].astype(np.float64)
        if (
            temperature <= 0
            or not 0 < threshold < 1
            or reference_distance_threshold <= 0
            or mean.ndim != 1
            or mean.shape != inverse_variances.shape
            or not np.isfinite(mean).all()
            or not np.isfinite(inverse_variances).all()
            or (inverse_variances <= 0).any()
        ):
            return Phase3Artifacts.unavailable("Phase 3 工件的数值校验失败。")
        limitations = tuple(
            dict.fromkeys(
                [
                    *temperature_artifact.get("limitations", []),
                    *conformal_artifact.get("limitations", []),
                    *ood_artifact.get("limitations", []),
                ]
            )
        )
        return Phase3Artifacts(
            available=True,
            reason="Phase 3 内部实验工件已加载。",
            temperature=temperature,
            conformal_alpha=DEFAULT_CONFORMAL_ALPHA,
            conformal_threshold=threshold,
            conformal_test_evaluation=conformal_result.get("test_evaluation"),
            reference_mean=mean,
            reference_inverse_variances=inverse_variances,
            reference_distance_threshold=reference_distance_threshold,
            reference_test_evaluation=ood_artifact.get("strict_test_reference_screen"),
            limitations=limitations,
        )
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
        return Phase3Artifacts.unavailable(f"无法加载 Phase 3 工件：{error}")
