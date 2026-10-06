"""Transparent Phase 4 clinical-context and missing-modality handling.

This module records the small set of optional clinical fields supplied by the
user.  It deliberately does not calculate a risk score or alter the DR model:
there is no longitudinal outcome-labelled dataset in this project to validate
such a model.
"""

from __future__ import annotations

from typing import Any


def _field(name: str, label: str, value: float | int | None, unit: str) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "value": value,
        "unit": unit,
        "status": "available" if value is not None else "missing",
        "used_by_current_dr_model": False,
    }


def build_clinical_context(
    age: int | None,
    hba1c: float | None,
    diabetes_years: float | None,
) -> dict[str, Any]:
    """Represent available and missing optional modalities without imputation."""
    fields = [
        _field("age", "年龄", age, "years"),
        _field("hba1c", "HbA1c", hba1c, "%"),
        _field("diabetes_years", "糖尿病病程", diabetes_years, "years"),
    ]
    available = [field["name"] for field in fields if field["status"] == "available"]
    missing = [field["name"] for field in fields if field["status"] == "missing"]
    return {
        "version": "clinical-context-v1",
        "status": "metadata_only",
        "fields": fields,
        "available_modalities": ["fundus_image", *available],
        "missing_modalities": missing,
        "missing_data_handling": "不填补、不推断；缺失字段保持缺失，并且不改变当前图像模型输出。",
        "used_by_current_dr_model": False,
        "long_term_risk": {
            "status": "not_available",
            "reason": "当前项目没有带随访结局的训练/验证数据，不能训练或展示长期风险模型。",
        },
    }
