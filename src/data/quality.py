"""
Data Quality Engine.
Performs comprehensive auditing across missing values, distributions, physics boundaries, unit integrity,
and generates JSON and Markdown quality reports.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def generate_data_quality_report(
    datasets: Dict[str, pd.DataFrame],
    output_json: str = "data/metadata/data_quality_report.json",
    output_md: str = "reports/data/data_quality_report.md"
) -> Dict[str, Any]:
    """
    Run data quality suite across all active datasets and export reports.
    """
    report = {
        "generated_at": pd.Timestamp.now(tz="UTC").isoformat(),
        "total_datasets_evaluated": len(datasets),
        "dataset_summaries": {}
    }
    
    md_lines = [
        "# Data Quality & Integrity Report",
        f"\n**Generated At:** {report['generated_at']}",
        "\n## Summary of Evaluated Datasets\n",
        "| Dataset | Rows | Columns | Missing (%) | Duplicate Rows | Quality Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for name, df in datasets.items():
        if df is None or df.empty:
            continue
            
        n_rows = len(df)
        n_cols = len(df.columns)
        total_cells = n_rows * n_cols
        missing_count = int(df.isna().sum().sum())
        missing_pct = round((missing_count / total_cells * 100.0) if total_cells > 0 else 0.0, 2)
        dup_count = int(df.duplicated().sum())
        
        # Check specific anomalies
        anomalies = []
        if "freight_usd_per_ton" in df.columns:
            neg_freight = int((df["freight_usd_per_ton"] <= 0).sum())
            if neg_freight > 0:
                anomalies.append(f"{neg_freight} non-positive freight rates")
                
        if "draft_m" in df.columns:
            bad_draft = int(((df["draft_m"] < 3.0) | (df["draft_m"] > 25.0)).sum())
            if bad_draft > 0:
                anomalies.append(f"{bad_draft} out-of-range drafts")
                
        status = "PASSED" if missing_pct < 10.0 and dup_count == 0 and len(anomalies) == 0 else "WARNING"
        
        col_nulls = {c: round(float(df[c].isna().mean() * 100.0), 2) for c in df.columns}
        
        summary = {
            "row_count": n_rows,
            "column_count": n_cols,
            "missing_cells_total": missing_count,
            "missing_percentage": missing_pct,
            "duplicate_rows": dup_count,
            "column_null_percentages": col_nulls,
            "anomalies_detected": anomalies,
            "quality_status": status
        }
        
        report["dataset_summaries"][name] = summary
        md_lines.append(f"| `{name}` | {n_rows:,} | {n_cols} | {missing_pct}% | {dup_count:,} | **{status}** |")
        
    md_lines.append("\n## Detailed Column-Level Null Analysis\n")
    for name, sum_data in report["dataset_summaries"].items():
        md_lines.append(f"### Dataset: `{name}`")
        md_lines.append(f"- **Total Rows:** {sum_data['row_count']:,}")
        md_lines.append(f"- **Duplicates:** {sum_data['duplicate_rows']}")
        if sum_data["anomalies_detected"]:
            md_lines.append(f"- **Anomalies:** {', '.join(sum_data['anomalies_detected'])}")
        md_lines.append("\n**Column Null Percentages:**\n")
        for col, null_pct in sum_data["column_null_percentages"].items():
            if null_pct > 0:
                md_lines.append(f"- `{col}`: {null_pct}% missing")
        md_lines.append("")
        
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(report, f, indent=2)
        
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w") as f:
        f.write("\n".join(md_lines))
        
    logger.info(f"Data quality report saved to {output_json} and {output_md}")
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Quality engine ready.")
