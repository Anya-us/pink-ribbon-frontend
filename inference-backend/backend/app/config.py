from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
MODEL_PATH = Path(
    os.getenv(
        "DR_MODEL_PATH",
        # This strict-split weight matches the bundled Phase 3 uncertainty
        # artifacts. It remains a research-only competition demonstration.
        PROJECT_ROOT / "artifacts" / "resnet18_strict" / "best_model.pt",
    )
)
PHASE3_ARTIFACT_DIR = Path(
    os.getenv(
        "DR_PHASE3_ARTIFACT_DIR",
        PROJECT_ROOT / "artifacts" / "phase7_strict_v1",
    )
)
LESION_ARTIFACT_DIR = Path(
    os.getenv(
        "DR_LESION_ARTIFACT_DIR",
        PROJECT_ROOT / "artifacts" / "lesion_evidence",
    )
)
EXTERNAL_OOD_ARTIFACT_PATH = Path(
    os.getenv(
        "DR_EXTERNAL_OOD_ARTIFACT_PATH",
        PROJECT_ROOT / "artifacts" / "external_ood" / "external_ood_evaluation.json",
    )
)
EXPERIMENT_REPORT_PATH = PROJECT_ROOT / "artifacts" / "phase5_report" / "experiment_report.json"
STORAGE_DIR = BACKEND_ROOT / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
DATABASE_PATH = STORAGE_DIR / "dr_platform.sqlite3"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def prepare_storage() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
