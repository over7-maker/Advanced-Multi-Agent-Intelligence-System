import logging
import pandas as pd
import io
import json
from typing import Any, Dict, List, Optional

from amas.agents.base.intelligence_agent import IntelligenceAgent
from amas.core.unified_orchestrator_v2 import UnifiedOrchestratorV2, OrchestratorTask
from amas.core.message_bus import MessageBus

logger = logging.getLogger(__name__)

class DataAgent(IntelligenceAgent):
    """
    A specialized agent for data analysis, processing, and visualization.

    This agent can handle structured data (like CSV or JSON), perform statistical analysis,
    generate insights, and create visualizations.
    """

    def __init__(
        self,
        agent_id: str,
        config: Dict[str, Any],
        orchestrator: UnifiedOrchestratorV2,
        message_bus: MessageBus,
    ):
        super().__init__(agent_id, config, orchestrator, message_bus)
        self.name = config.get("name", "Data Agent")
        self.capabilities = config.get("capabilities", ["data_analysis", "data_visualization", "data_processing"])
        logger.info(f"DataAgent {self.agent_id} initialized with capabilities: {self.capabilities}")

    async def execute_task(self, task: OrchestratorTask) -> Dict[str, Any]:
        """
        Executes a data-related task.
        Expected task parameters: {"data_task_type": "analyze|visualize|process", "details": {...}}
        """
        data_task_type = task.parameters.get("data_task_type")
        details = task.parameters.get("details", {})

        if not data_task_type:
            raise ValueError("DataAgent requires a 'data_task_type' in task parameters.")

        try:
            if data_task_type == "analyze":
                result = await self._analyze_data(details)
            elif data_task_type == "visualize":
                result = await self._visualize_data(details)
            elif data_task_type == "process":
                result = await self._process_data(details)
            else:
                raise ValueError(f"Unknown data_task_type: {data_task_type}")
            
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"DataAgent {self.agent_id} failed to execute task {task.id}: {e}")
            return {"success": False, "error": str(e)}

    async def _analyze_data(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes data using pandas and the Universal AI Manager for insights.
        """
        data_source = details.get("data_source") # Can be a path to a file or raw data string
        query = details.get("query")

        if not data_source or not query:
            raise ValueError("Data analysis requires 'data_source' and 'query'.")

        try:
            if isinstance(data_source, str) and (data_source.endswith(".csv") or data_source.endswith(".json")):
                df = pd.read_csv(data_source) if data_source.endswith(".csv") else pd.read_json(data_source)
            else:
                df = pd.read_csv(io.StringIO(data_source))

            # Basic data summary
            summary = df.describe().to_json()
            info_buffer = io.StringIO()
            df.info(buf=info_buffer)
            info = info_buffer.getvalue()

            llm_prompt = f"""
Analyze the following dataset and provide insights based on the query.

Dataset Summary:
{summary}

Dataset Info:
{info}

Query: {query}

Provide a detailed analysis and any relevant findings.
"""
            response = await self._call_ai_manager(
                prompt=llm_prompt, max_tokens=1500, temperature=0.7, task_type="data_analysis"
            )

            if response["success"]:
                return {"analysis": response["content"], "dataframe_summary": summary, "dataframe_info": info}
            else:
                raise Exception(f"AI manager failed for data analysis: {response['error']}")

        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            raise

    async def _visualize_data(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates data visualizations using the Universal AI Manager to create code for a library like Matplotlib or Plotly.
        """
        data_source = details.get("data_source")
        chart_type = details.get("chart_type")
        x_axis = details.get("x_axis")
        y_axis = details.get("y_axis")

        if not all([data_source, chart_type, x_axis, y_axis]):
            raise ValueError("Data visualization requires 'data_source', 'chart_type', 'x_axis', and 'y_axis'.")

        try:
            if isinstance(data_source, str) and (data_source.endswith(".csv") or data_source.endswith(".json")):
                df = pd.read_csv(data_source) if data_source.endswith(".csv") else pd.read_json(data_source)
            else:
                df = pd.read_csv(io.StringIO(data_source))

            sample_data = df.head().to_json()

            llm_prompt = f"""
Generate Python code using Matplotlib to create a {chart_type} visualization.

Dataset Sample:
{sample_data}

Columns: {df.columns.tolist()}
X-axis: {x_axis}
Y-axis: {y_axis}

Provide only the Python code for generating the plot, enclosed in triple backticks.
Assume the data is loaded into a pandas DataFrame named `df`.
"""
            response = await self._call_ai_manager(
                prompt=llm_prompt, max_tokens=1000, temperature=0.5, task_type="visualization_generation"
            )

            if response["success"]:
                code = response["content"].strip()
                if code.startswith("```") and code.endswith("```"):
                    code = code.split("\n", 1)[1].rsplit("\n", 1)[0]
                
                # Placeholder for executing the generated code to create an image
                # In a real system, this would save a file and return its path or binary data
                logger.info(f"Generated visualization code:\n{code}")
                return {"visualization_code": code, "image_path": "path/to/simulated_chart.png"}
            else:
                raise Exception(f"AI manager failed to generate visualization code: {response['error']}")

        except Exception as e:
            logger.error(f"Data visualization failed: {e}")
            raise

    async def _process_data(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes data based on a series of specified steps using pandas.
        """
        data_source = details.get("data_source")
        processing_steps = details.get("processing_steps") # List of processing instructions

        if not data_source or not processing_steps:
            raise ValueError("Data processing requires 'data_source' and 'processing_steps'.")

        try:
            if isinstance(data_source, str) and (data_source.endswith(".csv") or data_source.endswith(".json")):
                df = pd.read_csv(data_source) if data_source.endswith(".csv") else pd.read_json(data_source)
            else:
                df = pd.read_csv(io.StringIO(data_source))

            # This is a simplified approach. A more robust solution would use the AI manager
            # to convert natural language steps into executable pandas operations.
            for step in processing_steps:
                logger.info(f"Applying processing step: {step}")
                # Example simple processing steps
                if "drop column" in step:
                    col_to_drop = step.split("drop column")[-1].strip()
                    if col_to_drop in df.columns:
                        df = df.drop(columns=[col_to_drop])
                elif "fill missing with" in step:
                    parts = step.split("fill missing with")
                    col = parts[0].strip()
                    value = parts[1].strip()
                    if col in df.columns:
                        df[col] = df[col].fillna(value)
            
            processed_data = df.to_csv(index=False)
            return {"processed_data": processed_data, "shape": df.shape}

        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise

