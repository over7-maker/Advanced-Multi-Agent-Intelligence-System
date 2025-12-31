"""
Data Analysis Tools
Implementations for data analysis: Polars, DuckDB, Great Expectations
"""

import logging
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from . import AgentTool

logger = logging.getLogger(__name__)


class PolarsTool(AgentTool):
    """Polars fast DataFrame library"""
    
    def __init__(self):
        super().__init__(
            name="polars",
            description="Fast DataFrame library (5-10x faster than Pandas)"
        )
        self.category = "data_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["read_csv", "read_json", "query", "aggregate"], "description": "Operation to perform"},
                "data": {"type": "string", "description": "Data source (file path or JSON string)"},
                "query": {"type": "string", "description": "SQL-like query (for query operation)"}
            },
            "required": ["operation"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Polars operation"""
        try:
            try:
                import polars as pl
            except ImportError:
                return {"success": False, "error": "Polars not installed. Install with: pip install polars"}
            
            operation = params.get("operation")
            data = params.get("data")
            
            if operation == "read_csv":
                if not data:
                    return {"success": False, "error": "Data parameter required for read_csv"}
                df = pl.read_csv(data)
                return {
                    "success": True,
                    "result": {
                        "operation": operation,
                        "rows": df.height,
                        "columns": df.width,
                        "column_names": df.columns,
                        "schema": {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
                    }
                }
            
            elif operation == "read_json":
                if not data:
                    return {"success": False, "error": "Data parameter required for read_json"}
                df = pl.read_json(data)
                return {
                    "success": True,
                    "result": {
                        "operation": operation,
                        "rows": df.height,
                        "columns": df.width,
                        "column_names": df.columns
                    }
                }
            
            elif operation == "query":
                # For query, we'd need a DataFrame already loaded
                return {"success": False, "error": "Query operation requires pre-loaded DataFrame"}
            
            elif operation == "aggregate":
                if not data:
                    return {"success": False, "error": "Data parameter required for aggregate"}
                df = pl.read_csv(data) if data.endswith('.csv') else pl.read_json(data)
                summary = df.describe()
                return {
                    "success": True,
                    "result": {
                        "operation": operation,
                        "summary": summary.to_dicts()
                    }
                }
            
            return {"success": False, "error": f"Unknown operation: {operation}"}
        except Exception as e:
            logger.error(f"Polars operation failed: {e}")
            return {"success": False, "error": str(e)}


class DuckDBTool(AgentTool):
    """DuckDB in-process OLAP database"""
    
    def __init__(self):
        super().__init__(
            name="duckdb",
            description="In-process OLAP database"
        )
        self.category = "data_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute"},
                "data_source": {"type": "string", "description": "CSV file path or data to load"}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DuckDB query"""
        try:
            try:
                import duckdb
            except ImportError:
                return {"success": False, "error": "DuckDB not installed. Install with: pip install duckdb"}
            
            query = params.get("query")
            data_source = params.get("data_source")
            
            conn = duckdb.connect()
            
            # Load data if provided
            if data_source:
                if data_source.endswith('.csv'):
                    conn.execute(f"CREATE TABLE data AS SELECT * FROM read_csv_auto('{data_source}')")
                else:
                    return {"success": False, "error": "Only CSV files supported for data_source"}
            
            # Execute query
            result = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description] if hasattr(conn, 'description') else []
            
            conn.close()
            
            return {
                "success": True,
                "result": {
                    "query": query,
                    "rows": [dict(zip(columns, row)) for row in result] if columns else [list(row) for row in result],
                    "count": len(result)
                }
            }
        except Exception as e:
            logger.error(f"DuckDB query failed: {e}")
            return {"success": False, "error": str(e)}


class GreatExpectationsTool(AgentTool):
    """Great Expectations data quality validation"""
    
    def __init__(self):
        super().__init__(
            name="great_expectations",
            description="Data quality validation framework"
        )
        self.category = "data_analysis"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_source": {"type": "string", "description": "Data source path"},
                "expectations": {"type": "array", "description": "List of expectations to check"}
            },
            "required": ["data_source"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Great Expectations validation"""
        try:
            try:
                import great_expectations as ge
            except ImportError:
                return {"success": False, "error": "Great Expectations not installed. Install with: pip install great-expectations"}
            
            data_source = params.get("data_source")
            expectations = params.get("expectations", [])
            
            # Load data
            if data_source.endswith('.csv'):
                df = ge.read_csv(data_source)
            elif data_source.endswith('.json'):
                df = ge.read_json(data_source)
            else:
                return {"success": False, "error": "Only CSV and JSON files supported"}
            
            # Run expectations
            results = []
            for expectation in expectations:
                try:
                    if expectation.get("type") == "expect_column_to_exist":
                        result = df.expect_column_to_exist(expectation.get("column"))
                    elif expectation.get("type") == "expect_column_values_to_not_be_null":
                        result = df.expect_column_values_to_not_be_null(expectation.get("column"))
                    elif expectation.get("type") == "expect_column_values_to_be_between":
                        result = df.expect_column_values_to_be_between(
                            expectation.get("column"),
                            min_value=expectation.get("min_value"),
                            max_value=expectation.get("max_value")
                        )
                    else:
                        results.append({"expectation": expectation, "status": "not_implemented"})
                        continue
                    
                    results.append({
                        "expectation": expectation,
                        "success": result.get("success", False),
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "expectation": expectation,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "result": {
                    "data_source": data_source,
                    "expectations": results,
                    "passed": sum(1 for r in results if r.get("success", False)),
                    "failed": sum(1 for r in results if not r.get("success", False))
                }
            }
        except Exception as e:
            logger.error(f"Great Expectations validation failed: {e}")
            return {"success": False, "error": str(e)}

