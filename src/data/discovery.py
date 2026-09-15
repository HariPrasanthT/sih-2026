"""
Data Discovery and Schema Inspection Engine.
Scans raw data directories, inspects structure, columns, types, nulls, candidate targets, and produces schema_report.json.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def inspect_csv_file(file_path: str, max_sample_rows: int = 5000) -> Dict[str, Any]:
    """Inspect CSV file schema and quality metrics."""
    try:
        # Read header and sample
        df_sample = pd.read_csv(file_path, nrows=max_sample_rows, low_memory=False)
        # Approximate row count if large
        file_size = os.path.getsize(file_path)
        
        row_count = len(df_sample)
        if file_size < 50 * 1024 * 1024:  # under 50MB, read full row count
            try:
                row_count = sum(1 for _ in open(file_path, 'rb')) - 1
            except Exception:
                pass
        
        cols = list(df_sample.columns)
        null_pcts = {col: round(float(df_sample[col].isna().mean() * 100), 2) for col in cols}
        dtypes = {col: str(df_sample[col].dtype) for col in cols}
        
        date_cols = [c for c in cols if any(k in c.lower() for k in ["date", "time", "year", "month", "day", "timestamp"])]
        id_cols = [c for c in cols if any(k in c.lower() for k in ["id", "imo", "mmsi", "code", "vessel", "port"])]
        geo_cols = [c for c in cols if any(k in c.lower() for k in ["lat", "lon", "port", "country", "origin", "dest"])]
        target_candidates = [c for c in cols if any(k in c.lower() for k in ["freight", "rate", "usd", "price", "tariff", "transit", "delay", "time"])]
        
        return {
            "format": "csv",
            "file_size_bytes": file_size,
            "estimated_rows": row_count,
            "column_count": len(cols),
            "columns": cols,
            "data_types": dtypes,
            "null_percentages": null_pcts,
            "date_columns": date_cols,
            "candidate_id_columns": id_cols,
            "geographic_columns": geo_cols,
            "target_candidate_columns": target_candidates,
            "sample_head": df_sample.head(3).to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Error inspecting CSV {file_path}: {e}")
        return {"error": str(e), "format": "csv", "file_size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0}


def inspect_excel_file(file_path: str) -> Dict[str, Any]:
    """Inspect Excel file schema, sheets, and columns."""
    try:
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        sheets_info = {}
        total_rows = 0
        all_cols = []
        
        for sheet in sheet_names[:10]:  # inspect up to 10 sheets
            try:
                df = xl.parse(sheet, nrows=500)
                cols = [str(c) for c in df.columns]
                all_cols.extend(cols)
                sheets_info[sheet] = {
                    "row_count_sample": len(df),
                    "column_count": len(cols),
                    "columns": cols,
                    "null_percentages": {c: round(float(df[c].isna().mean() * 100), 2) for c in cols if c in df}
                }
                total_rows += len(df)
            except Exception as se:
                sheets_info[sheet] = {"error": str(se)}
        
        all_cols = list(set(all_cols))
        date_cols = [c for c in all_cols if any(k in c.lower() for k in ["date", "time", "year", "month", "day"])]
        geo_cols = [c for c in all_cols if any(k in c.lower() for k in ["port", "country", "origin", "dest", "india"])]
        target_candidates = [c for c in all_cols if any(k in c.lower() for k in ["freight", "rate", "price", "usd", "cost"])]
        
        return {
            "format": "excel",
            "file_size_bytes": os.path.getsize(file_path),
            "sheet_count": len(sheet_names),
            "sheet_names": sheet_names,
            "sheets": sheets_info,
            "date_columns": date_cols,
            "geographic_columns": geo_cols,
            "target_candidate_columns": target_candidates,
        }
    except Exception as e:
        logger.error(f"Error inspecting Excel {file_path}: {e}")
        return {"error": str(e), "format": "excel", "file_size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0}


def inspect_parquet_file(file_path: str) -> Dict[str, Any]:
    """Inspect Parquet file schema."""
    try:
        df = pd.read_parquet(file_path)
        cols = list(df.columns)
        return {
            "format": "parquet",
            "file_size_bytes": os.path.getsize(file_path),
            "row_count": len(df),
            "column_count": len(cols),
            "columns": cols,
            "data_types": {col: str(df[col].dtype) for col in cols},
            "null_percentages": {col: round(float(df[col].isna().mean() * 100), 2) for col in cols},
            "sample_head": df.head(3).to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e), "format": "parquet", "file_size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0}


def discover_all_datasets(search_roots: Optional[List[str]] = None, output_report_path: str = "data/metadata/schema_report.json") -> Dict[str, Any]:
    """
    Scan search roots and build a complete schema report.
    """
    if search_roots is None:
        search_roots = [
            "data/raw",
            "cargo traffic data",
            "carago traffic data",
            "Commodity Coal Prices",
            "Global Daily Port Activity and Trade Estimates",
            "Global Supply Chain Disruption & Resilience",
            "Maritime Port Performance Dataset",
            "WORLD BANK COMMODITY DATA",
            "FREIGHT FORECAST DATA",
            "CMO-April-2026-Data-Supplement"
        ]
    
    report: Dict[str, Any] = {
        "timestamp": pd.Timestamp.now(tz="UTC").isoformat(),
        "discovered_files_count": 0,
        "files": {},
        "summary": {
            "csv_count": 0,
            "excel_count": 0,
            "parquet_count": 0,
            "pdf_or_other_count": 0,
            "identified_india_sources": [],
            "identified_market_sources": [],
            "identified_freight_targets": []
        }
    }
    
    for root_dir in search_roots:
        if not os.path.exists(root_dir):
            continue
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path).replace("\\", "/")
                ext = os.path.splitext(file)[1].lower()
                
                info: Dict[str, Any] = {}
                if ext == ".csv":
                    info = inspect_csv_file(file_path)
                    report["summary"]["csv_count"] += 1
                elif ext in [".xlsx", ".xls"]:
                    info = inspect_excel_file(file_path)
                    report["summary"]["excel_count"] += 1
                elif ext == ".parquet":
                    info = inspect_parquet_file(file_path)
                    report["summary"]["parquet_count"] += 1
                else:
                    info = {
                        "format": ext.replace(".", ""),
                        "file_size_bytes": os.path.getsize(file_path)
                    }
                    report["summary"]["pdf_or_other_count"] += 1
                
                info["file_path"] = rel_path
                info["file_name"] = file
                
                # Check geographic relevance
                if any(p in rel_path.upper() for p in ["PARADIP", "VISHAKHAPATNAM", "VISAKHAPATNAM", "CHENNAI", "KAMARAJAR", "HALDIA", "KOLKATA", "INDIA"]):
                    report["summary"]["identified_india_sources"].append(rel_path)
                
                if any(m in rel_path.upper() for m in ["COMMODITY", "COAL", "WORLD BANK", "PINK SHEET"]):
                    report["summary"]["identified_market_sources"].append(rel_path)
                
                report["files"][rel_path] = info
                report["discovered_files_count"] += 1
                
    # Deduplicate summary lists
    report["summary"]["identified_india_sources"] = list(set(report["summary"]["identified_india_sources"]))
    report["summary"]["identified_market_sources"] = list(set(report["summary"]["identified_market_sources"]))
    
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    with open(output_report_path, "w") as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Discovery complete. Discovered {report['discovered_files_count']} files. Report saved to {output_report_path}")
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    discover_all_datasets()
