from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .clinical import build_clinical_context
from .config import DATABASE_PATH, EXPERIMENT_REPORT_PATH, MAX_UPLOAD_BYTES, MODEL_PATH, UPLOAD_DIR, prepare_storage
from .db import (
    create_analysis,
    create_task,
    initialize_database,
    list_analyses,
    list_patient_archives,
    list_tasks,
    update_review,
    update_task_status,
)
from .inference import (
    CONSENSUS_V2_VERSION,
    CONSENSUS_VERSION,
    DRInferenceService,
    LEVELS,
    MODEL_VERSION,
    TECHNICAL_CHECK_VERSION,
)
from .workflow import build_capture_quality_result, build_workflow_context, initial_task_drafts


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


class ReviewPayload(BaseModel):
    status: Literal["confirmed", "adjusted", "rejected", "accepted", "modified", "returned"]
    final_grade: int | None = Field(default=None, ge=0, le=4)
    doctor_note: str | None = Field(default=None, max_length=1000)
    doctor_name: str | None = Field(default=None, max_length=80)
    modification_reason: str | None = Field(default=None, max_length=500)
    sign_off: bool = False


class CareTaskPayload(BaseModel):
    task_type: Literal["recapture", "doctor_review", "follow_up", "specialist_review"]
    priority: Literal["routine", "review", "safety_review"] = "routine"
    summary: str = Field(min_length=1, max_length=300)
    reason: str | None = Field(default=None, max_length=500)


class CareTaskStatusPayload(BaseModel):
    status: Literal["open", "in_progress", "completed", "cancelled"]


class PredictionResult(BaseModel):
    predicted_grade: int = Field(ge=0, le=4)
    predicted_label: str
    confidence: float = Field(ge=0, le=1)
    probabilities: list[dict[str, Any]]
    technical_check: dict[str, Any]
    consensus: dict[str, Any]
    evidence: dict[str, Any]
    phase3: dict[str, Any]
    lesion_evidence: dict[str, Any]
    needs_review: bool
    decision_reason: str
    model_version: str


class PredictionEnvelope(BaseModel):
    success: bool
    result: PredictionResult
    notice: str


class AnalysisResult(PredictionResult):
    id: int
    patient_name: str
    age: int | None
    eye: Literal["left", "right"]
    hba1c: float | None
    diabetes_years: float | None
    review_status: Literal["pending", "confirmed", "adjusted", "rejected", "accepted", "modified", "returned"]
    final_grade: int | None
    doctor_note: str | None
    doctor_name: str | None
    modification_reason: str | None
    signed_at: str | None
    created_at: str
    reviewed_at: str | None
    image_url: str
    clinical_context: dict[str, Any]
    case_code: str
    captured_at: str
    device_model: str
    field_of_view: str
    image_sha256: str
    workflow_context: dict[str, Any]
    capture_quality: dict[str, Any]
    device_status: str
    tasks: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    model_path: str
    model_ready: bool
    model_version: str
    consensus_version: str
    conditional_consensus_version: str
    technical_check_version: str


@lru_cache
def inference_service() -> DRInferenceService:
    return DRInferenceService(MODEL_PATH)


prepare_storage()
initialize_database(DATABASE_PATH)

app = FastAPI(
    title="DR 智能筛查演示 API",
    version="0.3.0",
    description="仅供竞赛演示与研究，不能用于临床诊断或治疗决策。",
)
app.add_middleware(
    CORSMiddleware,
    # 仅允许本机浏览器端口访问；前端项目的开发端口可能不同。
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(?::\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


async def read_validated_image(image: UploadFile) -> bytes:
    """Validate an upload shared by stateless inference and case persistence."""
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="只支持 JPG、PNG 或 WebP 图片。")
    content = await image.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空。")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="图片不能超过 20 MB。")
    return content


def run_inference(image_bytes: bytes) -> dict[str, Any]:
    try:
        return inference_service().analyze_bytes(image_bytes)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=f"模型暂不可用：{error}") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/health", response_model=HealthResponse)
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "model_path": str(MODEL_PATH),
        "model_ready": MODEL_PATH.is_file(),
        "model_version": MODEL_VERSION,
        "consensus_version": CONSENSUS_VERSION,
        "conditional_consensus_version": CONSENSUS_V2_VERSION,
        "technical_check_version": TECHNICAL_CHECK_VERSION,
    }


@app.get("/api/meta")
def metadata() -> dict[str, object]:
    return {
        "grades": [{"grade": grade, "label": label} for grade, label in enumerate(LEVELS)],
        "notice": "当前为研究与竞赛演示版本，AI 结果必须经专业人员复核。",
        "implemented_modules": [
            "ResNet18 五级 DR 分类",
            "基础技术质量检查",
            "DM-Consensus v1",
            "DM-Consensus 2.0（内部实验工件可用时）",
            "病灶分割训练/验证/推理接口（权重就绪前不输出病灶结果）",
            "SQLite 病例与复核记录",
            "临床字段结构化保存（不参与当前模型）",
            "Phase 5 实验报告接口",
            "病例—眼别—时间元数据与本地安全任务审计",
        ],
        "phase_3_status": {
            "temperature_scaling": "内部实验工件可用时启用",
            "conformal_prediction": "内部实验工件可用时启用",
            "reference_anomaly_screen": "内部 APTOS 参考筛查，不是外部验证的正式 OOD 检测",
            "lesion_evidence": "训练与推理管线已就绪；当前没有通过真实标注训练和独立测试验证的权重，因此明确不可用",
        },
        "phase_3_not_implemented": ["当前部署中的病灶模型权重与真实外部 OOD 评估"],
        # Kept for Phase 1 API consumers.
        "unsupported_modules": [
            "病灶检测",
            "外部验证的正式 OOD 检测",
            "临床多模态融合",
            "长期风险模型",
            "OCT/DME 模块",
            "FHIR 服务、CQL 规则引擎和 GraphRAG",
            "端侧 ONNX/QNN 量化部署",
        ],
    }


@app.get("/api/experiments")
def experiments() -> dict[str, Any]:
    """Expose only persisted experiment measurements for the local competition UI."""
    if not EXPERIMENT_REPORT_PATH.is_file():
        return {
            "status": "not_available",
            "reason": "尚未生成 Phase 5 实验报告。请运行 src/phase5_build_report.py。",
        }
    try:
        with EXPERIMENT_REPORT_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        return {"status": "not_available", "reason": f"无法读取实验报告：{error}"}


@app.post("/api/ai/predict", response_model=PredictionEnvelope)
async def predict_ai(image: UploadFile = File(...)) -> dict[str, object]:
    """Return one research-model prediction without creating a patient or case record."""
    prediction = run_inference(await read_validated_image(image))
    return {
        "success": True,
        "result": prediction,
        "notice": "仅供竞赛与研究演示，不能用于临床诊断或治疗决策。",
    }


@app.get("/api/analyses", response_model=list[AnalysisResult])
def analyses(limit: int = 30) -> list[dict[str, Any]]:
    return list_analyses(DATABASE_PATH, limit)


@app.get("/api/patients")
def patient_archives(limit: int = 100) -> list[dict[str, Any]]:
    """List local demo patient archives with left/right-eye examination timelines."""
    return list_patient_archives(DATABASE_PATH, limit)


@app.post("/api/analyses", status_code=status.HTTP_201_CREATED, response_model=AnalysisResult)
async def create_new_analysis(
    patient_name: str = Form(..., min_length=1, max_length=80),
    patient_confirmed: bool = Form(False),
    case_code: str | None = Form(default=None, max_length=80),
    age: int | None = Form(default=None, ge=0, le=120),
    eye: Literal["left", "right"] = Form(...),
    hba1c: float | None = Form(default=None, ge=0, le=30),
    diabetes_years: float | None = Form(default=None, ge=0, le=100),
    captured_at: datetime | None = Form(default=None),
    device_model: str | None = Form(default=None, max_length=120),
    device_status: Literal["registered", "unknown"] = Form(default="registered"),
    field_of_view: str | None = Form(default=None, max_length=80),
    image: UploadFile = File(...),
) -> dict[str, Any]:
    if not patient_confirmed:
        raise HTTPException(status_code=422, detail="请先确认患者档案后再提交筛查。")
    content = await read_validated_image(image)

    suffix = Path(image.filename or "image.png").suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        suffix = ".png"
    saved_filename = f"{uuid4().hex}{suffix}"
    saved_path = UPLOAD_DIR / saved_filename
    saved_path.write_bytes(content)

    try:
        prediction = run_inference(content)
    except HTTPException:
        saved_path.unlink(missing_ok=True)
        raise
    except Exception as error:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"无法读取或分析该图片：{error}") from error

    captured_at_value = (captured_at or datetime.now(timezone.utc)).isoformat()
    normalized_case_code = case_code.strip() if case_code and case_code.strip() else f"demo-{saved_filename[:8]}"
    normalized_device_model = device_model.strip() if device_model and device_model.strip() else None
    normalized_field_of_view = field_of_view.strip() if field_of_view and field_of_view.strip() else None
    image_sha256 = hashlib.sha256(content).hexdigest()
    clinical_context = build_clinical_context(age, hba1c, diabetes_years)
    workflow_context = build_workflow_context(
        case_code=normalized_case_code,
        eye=eye,
        captured_at=captured_at_value,
        device_model=normalized_device_model,
        field_of_view=normalized_field_of_view,
        image_sha256=image_sha256,
        clinical_context=clinical_context,
    )
    capture_quality = build_capture_quality_result(
        prediction["technical_check"],
        device_status=device_status,
        device_model=normalized_device_model,
    )
    workflow_context["capture_quality"] = capture_quality

    return create_analysis(
        DATABASE_PATH,
        {
            "patient_name": patient_name.strip(),
            "age": age,
            "eye": eye,
            "hba1c": hba1c,
            "diabetes_years": diabetes_years,
            "clinical_context": clinical_context,
            "case_code": normalized_case_code,
            "captured_at": captured_at_value,
            "device_model": normalized_device_model,
            "field_of_view": normalized_field_of_view,
            "image_sha256": image_sha256,
            "workflow_context": workflow_context,
            "capture_quality": capture_quality,
            "device_status": device_status,
            "initial_task_drafts": initial_task_drafts(
                prediction["technical_check"], prediction["consensus"], capture_quality
            ),
            "image_filename": saved_filename,
            **prediction,
        },
    )


@app.post("/api/analyses/{analysis_id}/review", response_model=AnalysisResult)
def review_analysis(analysis_id: int, payload: ReviewPayload) -> dict[str, Any]:
    if payload.status in {"adjusted", "modified"} and payload.final_grade is None:
        raise HTTPException(status_code=422, detail="修正结果时必须提供最终等级。")
    if payload.status in {"adjusted", "modified"} and not (payload.modification_reason or "").strip():
        raise HTTPException(status_code=422, detail="修正结果时必须填写修改原因。")
    if payload.sign_off and not (payload.doctor_name or "").strip():
        raise HTTPException(status_code=422, detail="签发前必须填写医生姓名。")
    updated = update_review(
        DATABASE_PATH,
        analysis_id,
        payload.status,
        payload.final_grade,
        payload.doctor_note.strip() if payload.doctor_note else None,
        payload.doctor_name.strip() if payload.doctor_name else None,
        payload.modification_reason.strip() if payload.modification_reason else None,
        payload.sign_off,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="未找到该分析记录。")
    return updated


@app.get("/api/analyses/{analysis_id}/tasks")
def analysis_tasks(analysis_id: int) -> list[dict[str, Any]]:
    tasks = list_tasks(DATABASE_PATH, analysis_id)
    if tasks is None:
        raise HTTPException(status_code=404, detail="未找到该分析记录。")
    return tasks


@app.post("/api/analyses/{analysis_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_analysis_task(analysis_id: int, payload: CareTaskPayload) -> dict[str, Any]:
    task = create_task(
        DATABASE_PATH,
        analysis_id,
        {
            "task_type": payload.task_type,
            "priority": payload.priority,
            "summary": payload.summary.strip(),
            "reason": payload.reason.strip() if payload.reason and payload.reason.strip() else "由医生/评审在演示中创建。",
        },
    )
    if not task:
        raise HTTPException(status_code=404, detail="未找到该分析记录。")
    return task


@app.post("/api/tasks/{task_id}/status")
def change_task_status(task_id: int, payload: CareTaskStatusPayload) -> dict[str, Any]:
    task = update_task_status(DATABASE_PATH, task_id, payload.status)
    if not task:
        raise HTTPException(status_code=404, detail="未找到该任务。")
    return task
