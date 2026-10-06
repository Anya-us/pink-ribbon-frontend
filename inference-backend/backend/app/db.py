from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def _add_missing_phase2_columns(connection: sqlite3.Connection) -> None:
    """Upgrade a Phase 1 analyses database without discarding historical rows."""
    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(analyses)").fetchall()
    }
    migrations = {
        "consensus_json": "ALTER TABLE analyses ADD COLUMN consensus_json TEXT",
        "evidence_json": "ALTER TABLE analyses ADD COLUMN evidence_json TEXT",
        "clinical_context_json": "ALTER TABLE analyses ADD COLUMN clinical_context_json TEXT",
        "case_code": "ALTER TABLE analyses ADD COLUMN case_code TEXT",
        "captured_at": "ALTER TABLE analyses ADD COLUMN captured_at TEXT",
        "device_model": "ALTER TABLE analyses ADD COLUMN device_model TEXT",
        "field_of_view": "ALTER TABLE analyses ADD COLUMN field_of_view TEXT",
        "image_sha256": "ALTER TABLE analyses ADD COLUMN image_sha256 TEXT",
        "workflow_context_json": "ALTER TABLE analyses ADD COLUMN workflow_context_json TEXT",
        "capture_quality_json": "ALTER TABLE analyses ADD COLUMN capture_quality_json TEXT",
        "device_status": "ALTER TABLE analyses ADD COLUMN device_status TEXT",
        "doctor_name": "ALTER TABLE analyses ADD COLUMN doctor_name TEXT",
        "modification_reason": "ALTER TABLE analyses ADD COLUMN modification_reason TEXT",
        "signed_at": "ALTER TABLE analyses ADD COLUMN signed_at TEXT",
    }
    for column, statement in migrations.items():
        if column not in existing_columns:
            connection.execute(statement)


def initialize_database(database_path: Path) -> None:
    connection = connect(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                age INTEGER,
                eye TEXT NOT NULL,
                hba1c REAL,
                diabetes_years REAL,
                image_filename TEXT NOT NULL,
                predicted_grade INTEGER,
                predicted_label TEXT,
                confidence REAL,
                needs_review INTEGER NOT NULL,
                decision_reason TEXT NOT NULL,
                probabilities_json TEXT NOT NULL,
                technical_check_json TEXT NOT NULL,
                consensus_json TEXT,
                evidence_json TEXT,
                clinical_context_json TEXT,
                case_code TEXT,
                captured_at TEXT,
                device_model TEXT,
                field_of_view TEXT,
                image_sha256 TEXT,
                workflow_context_json TEXT,
                capture_quality_json TEXT,
                device_status TEXT,
                model_version TEXT NOT NULL,
                review_status TEXT NOT NULL DEFAULT 'pending',
                final_grade INTEGER,
                doctor_note TEXT,
                doctor_name TEXT,
                modification_reason TEXT,
                signed_at TEXT,
                created_at TEXT NOT NULL,
                reviewed_at TEXT
            )
            """
        )
        _add_missing_phase2_columns(connection)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS care_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                task_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                summary TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                event_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE INDEX IF NOT EXISTS idx_care_tasks_analysis ON care_tasks(analysis_id, status)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_analysis ON audit_events(analysis_id, created_at)")
        connection.commit()
    finally:
        connection.close()


def _load_json(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _legacy_consensus() -> dict[str, Any]:
    return {
        "status": "not_available",
        "reason": "该记录创建于 DM-Consensus v1 之前，无法回溯生成共识结论。",
        "version": "not_available",
        "clinically_validated": False,
        "evidence": [],
    }


def _legacy_evidence() -> dict[str, Any]:
    return {
        "version": "not_available",
        "clinically_validated": False,
        "scope_notice": "该历史记录创建于 Phase 2 结构化证据链之前。",
        "stages": [],
        "phase_3_not_implemented": [],
    }


def _legacy_phase3() -> dict[str, Any]:
    return {
        "status": "unavailable",
        "reason": "该记录创建于 Phase 3 内部实验工件之前。",
        "clinically_validated": False,
        "phase": "Phase 3",
    }


def _legacy_lesion_evidence() -> dict[str, Any]:
    return {
        "status": "not_available",
        "reason": "该记录创建于病灶证据训练/推理接口之前，不能回溯生成病灶结果。",
        "model_ready": False,
        "clinically_validated": False,
    }


def _legacy_clinical_context() -> dict[str, Any]:
    return {
        "status": "legacy_unavailable",
        "reason": "该记录创建于 Phase 4 临床信息结构化保存之前。",
        "used_by_current_dr_model": False,
        "long_term_risk": {"status": "not_available"},
    }


def _legacy_workflow_context() -> dict[str, Any]:
    return {
        "version": "not_available",
        "status": "legacy_unavailable",
        "notice": "该记录创建于病例—眼别—时间与任务审计字段之前。",
    }


def _legacy_capture_quality() -> dict[str, Any]:
    return {
        "status": "not_available",
        "label": "未登记",
        "reason": "该历史记录没有结构化采集质控结果。",
        "next_action": "由演示人员补充采集记录后再进行解读。",
        "is_demo_rule": True,
    }


def _task_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def _tasks_for_analysis(connection: sqlite3.Connection, analysis_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM care_tasks WHERE analysis_id = ? ORDER BY id DESC", (analysis_id,)
    ).fetchall()
    return [_task_row_to_dict(row) for row in rows]


def _add_audit_event(
    connection: sqlite3.Connection,
    *,
    analysis_id: int,
    event_type: str,
    actor_type: str,
    payload: dict[str, Any],
    created_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_events (analysis_id, event_type, actor_type, event_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (analysis_id, event_type, actor_type, json.dumps(payload, ensure_ascii=False), created_at),
    )


def _add_task(
    connection: sqlite3.Connection,
    *,
    analysis_id: int,
    task_type: str,
    priority: str,
    summary: str,
    reason: str,
    created_at: str,
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO care_tasks (
            analysis_id, task_type, priority, summary, reason, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, 'open', ?, ?)
        """,
        (analysis_id, task_type, priority, summary, reason, created_at, created_at),
    )
    row = connection.execute("SELECT * FROM care_tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _task_row_to_dict(row)


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["needs_review"] = bool(result["needs_review"])
    result["probabilities"] = _load_json(result.pop("probabilities_json"), [])
    result["technical_check"] = _load_json(result.pop("technical_check_json"), {})
    result["consensus"] = _load_json(result.pop("consensus_json", None), _legacy_consensus())
    result["evidence"] = _load_json(result.pop("evidence_json", None), _legacy_evidence())
    result["phase3"] = result["evidence"].get("phase_3", _legacy_phase3())
    lesion_stage = next(
        (
            stage.get("evidence")
            for stage in result["evidence"].get("stages", [])
            if stage.get("id") == "lesion_evidence"
        ),
        None,
    )
    result["lesion_evidence"] = lesion_stage if isinstance(lesion_stage, dict) else _legacy_lesion_evidence()
    result["clinical_context"] = _load_json(
        result.pop("clinical_context_json", None), _legacy_clinical_context()
    )
    result["workflow_context"] = _load_json(
        result.pop("workflow_context_json", None), _legacy_workflow_context()
    )
    result["capture_quality"] = _load_json(
        result.pop("capture_quality_json", None), _legacy_capture_quality()
    )
    result["device_status"] = result.get("device_status") or "not_provided"
    result["doctor_name"] = result.get("doctor_name") or None
    result["modification_reason"] = result.get("modification_reason") or None
    result["signed_at"] = result.get("signed_at") or None
    result["case_code"] = result.get("case_code") or "not_provided"
    result["captured_at"] = result.get("captured_at") or result.get("created_at")
    result["device_model"] = result.get("device_model") or "not_provided"
    result["field_of_view"] = result.get("field_of_view") or "not_provided"
    result["image_sha256"] = result.get("image_sha256") or "not_available"
    result["image_url"] = f"/uploads/{result.pop('image_filename')}"
    return result


def create_analysis(database_path: Path, record: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    connection = connect(database_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO analyses (
                patient_name, age, eye, hba1c, diabetes_years, image_filename,
                predicted_grade, predicted_label, confidence, needs_review,
                decision_reason, probabilities_json, technical_check_json,
                consensus_json, evidence_json, clinical_context_json,
                case_code, captured_at, device_model, field_of_view, image_sha256, workflow_context_json,
                capture_quality_json, device_status, model_version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["patient_name"],
                record["age"],
                record["eye"],
                record["hba1c"],
                record["diabetes_years"],
                record["image_filename"],
                record["predicted_grade"],
                record["predicted_label"],
                record["confidence"],
                int(record["needs_review"]),
                record["decision_reason"],
                json.dumps(record["probabilities"], ensure_ascii=False),
                json.dumps(record["technical_check"], ensure_ascii=False),
                json.dumps(record["consensus"], ensure_ascii=False),
                json.dumps(record["evidence"], ensure_ascii=False),
                json.dumps(record.get("clinical_context", _legacy_clinical_context()), ensure_ascii=False),
                record.get("case_code"),
                record.get("captured_at", now),
                record.get("device_model"),
                record.get("field_of_view"),
                record.get("image_sha256"),
                json.dumps(record.get("workflow_context", _legacy_workflow_context()), ensure_ascii=False),
                json.dumps(record.get("capture_quality", _legacy_capture_quality()), ensure_ascii=False),
                record.get("device_status", "not_provided"),
                record["model_version"],
                now,
            ),
        )
        analysis_id = int(cursor.lastrowid)
        for draft in record.get("initial_task_drafts", []):
            _add_task(connection, analysis_id=analysis_id, created_at=now, **draft)
        _add_audit_event(
            connection,
            analysis_id=analysis_id,
            event_type="analysis_created",
            actor_type="system",
            payload={
                "model_version": record["model_version"],
                "case_code": record.get("case_code") or "not_provided",
                "captured_at": record.get("captured_at", now),
                "image_sha256": record.get("image_sha256", "not_available"),
            },
            created_at=now,
        )
        row = connection.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        connection.commit()
        result = _row_to_dict(row)
        result["tasks"] = _tasks_for_analysis(connection, analysis_id)
        return result
    finally:
        connection.close()


def list_analyses(database_path: Path, limit: int = 30) -> list[dict[str, Any]]:
    safe_limit = min(max(limit, 1), 100)
    connection = connect(database_path)
    try:
        rows = connection.execute(
            "SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (safe_limit,)
        ).fetchall()
        results = [_row_to_dict(row) for row in rows]
        for result in results:
            result["tasks"] = _tasks_for_analysis(connection, int(result["id"]))
        return results
    finally:
        connection.close()


def list_patient_archives(database_path: Path, limit: int = 100) -> list[dict[str, Any]]:
    """Return a compact, de-identified patient archive with separate eye timelines.

    This is intentionally a local demonstration view over saved screening records,
    not a hospital master-patient-index service.
    """
    safe_limit = min(max(limit, 1), 200)
    connection = connect(database_path)
    try:
        rows = connection.execute(
            "SELECT * FROM analyses ORDER BY captured_at DESC, id DESC LIMIT ?", (safe_limit,)
        ).fetchall()
        archives: dict[str, dict[str, Any]] = {}
        for row in rows:
            record = _row_to_dict(row)
            stable_case_code = record["case_code"] if record["case_code"] != "not_provided" else None
            patient_key = stable_case_code or f"name:{record['patient_name']}"
            archive = archives.setdefault(
                patient_key,
                {
                    "patient_key": patient_key,
                    "patient_name": record["patient_name"],
                    "case_code": stable_case_code or "未提供病例代号",
                    "age": record["age"],
                    "exam_count": 0,
                    "latest_exam_at": record["captured_at"],
                    "eyes": {"left": [], "right": []},
                },
            )
            archive["exam_count"] += 1
            archive["eyes"][record["eye"]].append(
                {
                    "analysis_id": record["id"],
                    "captured_at": record["captured_at"],
                    "predicted_label": record["predicted_label"],
                    "predicted_grade": record["predicted_grade"],
                    "capture_quality": record["capture_quality"],
                    "review_status": record["review_status"],
                    "signed_at": record["signed_at"],
                }
            )
        return list(archives.values())
    finally:
        connection.close()


def list_tasks(database_path: Path, analysis_id: int) -> list[dict[str, Any]] | None:
    connection = connect(database_path)
    try:
        exists = connection.execute("SELECT 1 FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not exists:
            return None
        return _tasks_for_analysis(connection, analysis_id)
    finally:
        connection.close()


def create_task(database_path: Path, analysis_id: int, task: dict[str, str]) -> dict[str, Any] | None:
    now = datetime.now(timezone.utc).isoformat()
    connection = connect(database_path)
    try:
        exists = connection.execute("SELECT 1 FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not exists:
            return None
        created = _add_task(connection, analysis_id=analysis_id, created_at=now, **task)
        _add_audit_event(
            connection,
            analysis_id=analysis_id,
            event_type="care_task_created",
            actor_type="reviewer_demo",
            payload={"task_id": created["id"], **task},
            created_at=now,
        )
        connection.commit()
        return created
    finally:
        connection.close()


def update_task_status(database_path: Path, task_id: int, task_status: str) -> dict[str, Any] | None:
    now = datetime.now(timezone.utc).isoformat()
    connection = connect(database_path)
    try:
        row = connection.execute("SELECT * FROM care_tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            return None
        completed_at = now if task_status in {"completed", "cancelled"} else None
        connection.execute(
            "UPDATE care_tasks SET status = ?, updated_at = ?, completed_at = ? WHERE id = ?",
            (task_status, now, completed_at, task_id),
        )
        updated = connection.execute("SELECT * FROM care_tasks WHERE id = ?", (task_id,)).fetchone()
        _add_audit_event(
            connection,
            analysis_id=int(row["analysis_id"]),
            event_type="care_task_status_changed",
            actor_type="reviewer_demo",
            payload={"task_id": task_id, "previous_status": row["status"], "status": task_status},
            created_at=now,
        )
        connection.commit()
        return _task_row_to_dict(updated)
    finally:
        connection.close()


def update_review(
    database_path: Path,
    analysis_id: int,
    status: str,
    final_grade: int | None,
    doctor_note: str | None,
    doctor_name: str | None = None,
    modification_reason: str | None = None,
    sign_off: bool = False,
) -> dict[str, Any] | None:
    reviewed_at = datetime.now(timezone.utc).isoformat()
    connection = connect(database_path)
    try:
        connection.execute(
            """
            UPDATE analyses
            SET review_status = ?, final_grade = ?, doctor_note = ?, doctor_name = ?,
                modification_reason = ?, reviewed_at = ?, signed_at = CASE WHEN ? THEN ? ELSE signed_at END
            WHERE id = ?
            """,
            (
                status,
                final_grade,
                doctor_note,
                doctor_name,
                modification_reason,
                reviewed_at,
                int(sign_off),
                reviewed_at,
                analysis_id,
            ),
        )
        connection.execute(
            """
            UPDATE care_tasks
            SET status = 'completed', updated_at = ?, completed_at = ?
            WHERE analysis_id = ? AND task_type = 'doctor_review' AND status IN ('open', 'in_progress')
            """,
            (reviewed_at, reviewed_at, analysis_id),
        )
        row = connection.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if row:
            _add_audit_event(
                connection,
                analysis_id=analysis_id,
                event_type="review_saved",
                actor_type="reviewer_demo",
                payload={
                    "status": status,
                    "final_grade": final_grade,
                    "doctor_name": doctor_name or "not_provided",
                    "doctor_note_present": bool(doctor_note),
                    "modification_reason_present": bool(modification_reason),
                    "signed": sign_off,
                },
                created_at=reviewed_at,
            )
        connection.commit()
        if not row:
            return None
        result = _row_to_dict(row)
        result["tasks"] = _tasks_for_analysis(connection, analysis_id)
        return result
    finally:
        connection.close()
