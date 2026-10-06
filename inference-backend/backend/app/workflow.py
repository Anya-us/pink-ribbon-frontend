"""Auditable local workflow context for the competition demonstration.

This module deliberately keeps its role narrow.  It organises the patient-eye-
time record and creates safety review tasks, but it is not a FHIR server, CQL
engine, clinical scheduling service, or autonomous referral system.
"""

from __future__ import annotations

from typing import Any


WORKFLOW_VERSION = "dr-workflow-v1-demo"


def build_capture_quality_result(
    technical_check: dict[str, Any], *, device_status: str, device_model: str | None
) -> dict[str, Any]:
    """Translate transparent input checks into a capture-stage quality outcome.

    These rules are deliberately labelled as demonstration rules.  They do not
    substitute for a validated ophthalmic image-quality model or a device
    verification programme.
    """
    if device_status == "unknown" or not device_model:
        return {
            "status": "device_unknown",
            "label": "设备未知",
            "reason": "未登记或未确认采集设备，不能确认是否处于已知设备域。",
            "next_action": "补录设备型号与采集信息，并由医生确认后再审核 AI 草稿。",
            "is_demo_rule": True,
        }

    if technical_check.get("status") == "pass":
        return {
            "status": "pass",
            "label": "质控通过",
            "reason": "图像尺寸、亮度和对比度均满足本演示版基础输入门控。",
            "next_action": "可进入 AI 草稿与医生审核；AI 输出仍不构成临床诊断。",
            "is_demo_rule": True,
        }

    score = float(technical_check.get("score", 0))
    if score <= (1 / 3):
        return {
            "status": "severe_ungradable",
            "label": "严重不可判读",
            "reason": technical_check.get("message", "图像基础技术质量严重不足。"),
            "next_action": "停止将该图用作可判读筛查结论；建议重新采集并转人工处理。",
            "is_demo_rule": True,
        }

    return {
        "status": "recapture_required",
        "label": "需重拍",
        "reason": technical_check.get("message", "图像基础技术质量未通过。"),
        "next_action": "按提示调整曝光、对焦或视野后重拍；当前 AI 仅保留为不可签发草稿。",
        "is_demo_rule": True,
    }


def build_workflow_context(
    *,
    case_code: str | None,
    eye: str,
    captured_at: str,
    device_model: str | None,
    field_of_view: str | None,
    image_sha256: str,
    clinical_context: dict[str, Any],
) -> dict[str, Any]:
    """Record only supplied metadata and explicit unavailable modalities."""
    return {
        "version": WORKFLOW_VERSION,
        "status": "research_demo",
        "patient_eye_time": {
            "case_code": case_code or "not_provided",
            "eye": eye,
            "captured_at": captured_at,
            "image_sha256": image_sha256,
        },
        "device": {
            "model": device_model or "not_provided",
            "field_of_view": field_of_view or "not_provided",
            "validated_device_domain": "not_available",
        },
        "modalities": [
            {"name": "fundus_cfp", "status": "available", "used_by_current_model": True},
            {"name": "oct", "status": "not_available", "used_by_current_model": False},
            {"name": "uwf", "status": "not_available", "used_by_current_model": False},
            {
                "name": "clinical_fields",
                "status": clinical_context.get("status", "not_available"),
                "used_by_current_model": False,
            },
            {"name": "longitudinal_follow_up", "status": "not_available", "used_by_current_model": False},
        ],
        "output_boundaries": {
            "current_dr_screening": "research_demo_with_mandatory_professional_review",
            "lesion_evidence": "not_available_without_lesion_annotations",
            "oct_dme": "not_available_without_oct_module_and_validation",
            "longitudinal_risk": "not_available_without_outcome_labelled_follow_up_data",
            "clinical_rules": "not_available_without_versioned_cql_rule_pack_and_validation",
        },
        "notice": "本地竞赛演示仅记录病例和安全工作流；不构成 FHIR、CQL、自动转诊或临床诊疗服务。",
    }


def initial_task_drafts(
    technical_check: dict[str, Any],
    consensus: dict[str, Any],
    capture_quality: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Create non-clinical safety tasks; no referral recommendation is inferred."""
    capture_status = (capture_quality or {}).get("status")
    if capture_status in {"recapture_required", "severe_ungradable"} or technical_check.get("status") != "pass":
        return [
            {
                "task_type": "recapture",
                "priority": "safety_review",
                "summary": "采集质控未通过：请在专业人员确认后考虑重采。",
                "reason": (capture_quality or {}).get("reason", technical_check.get("message", "技术质量未通过")),
            },
            {
                "task_type": "doctor_review",
                "priority": "safety_review",
                "summary": "需要专业人员审核本次不可判读/低质量输入。",
                "reason": consensus.get("reason", "共识门控要求复核"),
            },
        ]
    if capture_status == "device_unknown":
        return [
            {
                "task_type": "doctor_review",
                "priority": "safety_review",
                "summary": "采集设备未确认：AI 草稿需要医生审核，不能直接签发。",
                "reason": (capture_quality or {}).get("reason", "采集设备未知"),
            }
        ]
    return [
        {
            "task_type": "doctor_review",
            "priority": "review" if consensus.get("status") != "accept" else "routine",
            "summary": "AI 筛查草稿等待专业人员复核与签发。",
            "reason": consensus.get("reason", "医生复核为必经流程"),
        }
    ]
