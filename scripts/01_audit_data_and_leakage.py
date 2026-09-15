import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath("."))
"""
Script 01: Master Data Audit, Domain Organization, and Leakage Detection.
Generates:
- reports/missing_values_report.html
- reports/leakage_detection_report.html
- reports/feature_correlation_report.html
- reports/data_quality_report.html
"""
import logging
import pandas as pd
# pyrefly: ignore [missing-import]
from src.data.data_audit import (
    setup_data_domain_directories,
    audit_missing_values,
    audit_temporal_leakage,
    generate_missing_values_report_html,
    generate_leakage_detection_report_html,
    generate_feature_correlation_report_html,
    generate_data_quality_report_html
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def run_audit():
    logging.info("STEP 1: Starting Data Audit and Domain Setup...")
    setup_data_domain_directories()
    
    # Load available master or fallback table
    master_path = "data/processed/master/training_master.parquet"
    if os.path.exists(master_path):
        df = pd.read_parquet(master_path)
    else:
        # Fallback to port congestion or port master
        df = pd.read_parquet("data/processed/ports/port_congestion.parquet")
        
    logging.info(f"Loaded {len(df)} rows for data audit.")
    
    # 1. Missing Values Audit
    missing_results = audit_missing_values(df, "training_master")
    generate_missing_values_report_html(missing_results)
    
    # 2. Leakage Audit
    leakage_results = audit_temporal_leakage(df)
    generate_leakage_detection_report_html(leakage_results)
    
    # 3. Correlation Report
    generate_feature_correlation_report_html(df)
    
    # 4. Overall Data Quality Report
    summary_stats = {
        "total_observations": len(df),
        "total_features": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "leakage_count": sum(1 for r in leakage_results if "FAIL" in r.get("status", ""))
    }
    generate_data_quality_report_html(summary_stats)
    logging.info("STEP 1 COMPLETE: All 4 data audit HTML reports generated successfully.")


if __name__ == "__main__":
    run_audit()
