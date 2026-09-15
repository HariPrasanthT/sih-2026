"""
Master Model Training & Evaluation Orchestrator for SIH 26006.
Executes the complete 23-step workflow end-to-end.
"""
import sys
import os

os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["OPENBLAS_NUM_THREADS"] = "4"

import subprocess
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("TRAIN_PIPELINE")


import runpy
import matplotlib
matplotlib.use("Agg")

def run_script(script_path: str):
    """Execute a python script in-process with runpy for instant execution."""
    logger.info(f"Executing: {script_path}")
    start = datetime.now(timezone.utc)
    try:
        runpy.run_path(script_path, run_name="__main__")
    except Exception as e:
        logger.error(f"Error executing {script_path}: {e}")
        raise
    dur = (datetime.now(timezone.utc) - start).total_seconds()
    logger.info(f"Completed {script_path} in {dur:.2f}s\n")


def run_full_pipeline():
    logger.info("=" * 70)
    logger.info("SIH 26006: AI-Driven Freight & Vessel Recommendation Training Pipeline")
    logger.info("=" * 70)
    
    start_time = datetime.now(timezone.utc)
    
    if not os.path.exists("data/splits/train.parquet") or "--all" in sys.argv:
        # STEPS 1-4: Data Ingestion, Discovery, Validation & Normalization
        logger.info("\n--- PHASE 1: DATA INGESTION, DISCOVERY & PREPROCESSING ---")
        run_script("scripts/01_audit_data_and_leakage.py")
        run_script("scripts/01_discover_data.py")
        run_script("scripts/02_download_kaggle.py")
        run_script("scripts/03_validate_data.py")
        run_script("scripts/04_normalize_data.py")
        
        # STEPS 5-6: Features, Master Dataset & Chronological Splitting
        logger.info("\n--- PHASE 2: FEATURE ENGINEERING & DATA SPLITS ---")
        run_script("scripts/05_build_features.py")
        run_script("scripts/06_create_splits.py")
    else:
        logger.info("\n--- PHASES 1 & 2: Master dataset and splits verified at data/splits/. Proceeding to training. ---")
    
    # STEPS 7-12: Model Training & Calibration
    logger.info("\n--- PHASE 3: MODEL TRAINING & CONFORMAL CALIBRATION ---")
    run_script("scripts/07_train_baselines.py")
    run_script("scripts/07_tune_hyperparameters.py")
    run_script("scripts/08_train_freight_models.py")
    run_script("scripts/09_train_transit_model.py")
    run_script("scripts/10_train_ontime_model.py")
    run_script("scripts/11_calibrate_conformal.py")
    run_script("scripts/12_train_regime_model.py")
    
    # STEPS 13-15: Held-Out Evaluation, SHAP, Candidate Store & Pipeline Artifacts
    logger.info("\n--- PHASE 4: FULL EVALUATION, SHAP & MODEL REPORTING ---")
    run_script("scripts/13_evaluate_all.py")
    run_script("scripts/14_build_candidate_store.py")
    run_script("scripts/15_build_pipeline_artifacts.py")
    
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info("=" * 70)
    logger.info(f"SUCCESS: Complete pipeline executed in {duration:.1f}s. All artifacts, models & reports ready.")
    logger.info("=" * 70)


if __name__ == "__main__":
    run_full_pipeline()
