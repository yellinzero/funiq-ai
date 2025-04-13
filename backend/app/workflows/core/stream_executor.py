from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from typing import Any, Dict

from loguru import logger
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from prefect.runtime import flow_run, task_run

from providers.operators.core import OperatorFactory

from .executor import WorkflowDebugExecutor, WorkflowExecutorBase, WorkflowVersionExecutor


class TaskFactory:
    """Factory class for creating different types of tasks."""

    @staticmethod
    def _create_base_execution_context(
        executor: "StreamExecutorBase",
        node_key: str,
        node_type: str,
        task_run_id: str,
        is_stream: bool = False,
    ) -> Dict[str, Any]:
        """Create common execution context."""
        return {
            "execution_id": executor.execution_id,
            "flow_run_id": executor.flow_run_id,
            "task_run_id": task_run_id,
            "node_type": node_type,
            "node_key": node_key,
            "version": getattr(executor, "version", None),
            "snapshot_timestamp": getattr(executor, "snapshot_timestamp", None),
            "stream_mode": is_stream,
            **executor.execution_context,
        }

    @staticmethod
    async def task_run(
        input_data: Any,
        node_type: str,
        node_key: str,
        is_stream: bool,
        node_config: Dict[str, Any],
        executor: "StreamExecutorBase",
    ):
        try:
            task_run_id = task_run.get_id()
            operator = OperatorFactory.get_operator_instance(node_type)
            if not operator:
                raise ValueError(f"No operator found for type: {node_type}")

            execution_context = TaskFactory._create_base_execution_context(
                executor=executor, node_key=node_key, node_type=node_type, task_run_id=task_run_id, is_stream=is_stream
            )
            result = await operator.execute(
                input_data=input_data, config=node_config, execution_context=execution_context
            )
            return result
        except Exception as e:
            logger.error(f"Error in task run: {e}")
            raise e

    @staticmethod
    def create_stream_task(
        node_name: str, node_type: str, node_key: str, node_config: Dict[str, Any], executor: "StreamExecutorBase"
    ):
        """Create a streaming task."""

        @task(name=node_name, timeout_seconds=5 * 60, tags=[node_type, "stream"], cache_policy=NO_CACHE)
        async def stream_task(input_data: Any = None):
            result = await TaskFactory.task_run(
                input_data=input_data,
                node_type=node_type,
                node_key=node_key,
                is_stream=True,
                node_config=node_config,
                executor=executor,
            )
            try:
                if isinstance(result, Generator):
                    for chunk in result:
                        yield chunk
                elif isinstance(result, AsyncGenerator):
                    async for chunk in result:
                        yield chunk
                else:
                    yield result
            except Exception as e:
                logger.error(f"Error in stream task: {e}")
                raise e

        return stream_task

    @staticmethod
    def create_normal_task(
        node_name: str, node_type: str, node_key: str, node_config: Dict[str, Any], executor: "StreamExecutorBase"
    ):
        """Create a normal (non-streaming) task."""

        @task(
            name=node_name,
            timeout_seconds=5 * 60,
            tags=[node_type],
        )
        async def normal_task(input_data: Any = None) -> Dict:
            result = await TaskFactory.task_run(
                input_data=input_data,
                node_type=node_type,
                node_key=node_key,
                is_stream=False,
                node_config=node_config,
                executor=executor,
            )

            return result

        return normal_task


class StreamExecutorBase(WorkflowExecutorBase):
    """Base class for stream executors that overrides core execution methods."""

    def _create_task_for_node(self, node: Dict[str, Any]):
        """Create a task for a workflow node based on its type."""
        extended_config = node.get("extended_config", {})
        is_stream = extended_config.get("stream_mode", False) if extended_config else False
        node_name = node.get("name")
        node_type = node.get("node_type")
        node_key = node.get("node_key")
        node_config = node.get("config", {})

        if is_stream:
            return TaskFactory.create_stream_task(
                node_name=node_name, node_type=node_type, node_key=node_key, node_config=node_config, executor=self
            )
        else:
            return TaskFactory.create_normal_task(
                node_name=node_name, node_type=node_type, node_key=node_key, node_config=node_config, executor=self
            )

    def _create_flow(self):
        """Create a streaming flow that executes tasks sequentially."""

        @flow(name=f"{self.workflow_name}_stream")
        async def workflow_stream_flow():
            self.flow_run_id = flow_run.get_id()

            try:
                for level in self.node_levels:
                    for node_key in level:
                        node = next(n for n in self.snapshot.get("nodes", []) if n.get("node_key") == node_key)
                        extended_config = node.get("extended_config", {})
                        is_stream = extended_config.get("stream_mode", False) if extended_config else False
                        input_data = {
                            **self.input_data,
                            **self._get_upstream_outputs(node_key),
                        }

                        task = self._create_task_for_node(node)
                        result = task(input_data) if is_stream else await task(input_data)
                        self.node_outputs[node_key] = result

                end_result = self.node_outputs[self.end_node_key]

                if isinstance(end_result, AsyncGenerator):
                    async for chunk in end_result:
                        yield chunk
                else:
                    yield end_result
            except Exception as e:
                raise e

        return workflow_stream_flow

    def execute(self):
        """Execute the streaming workflow."""
        logger.info(f"Executing streaming workflow: {self.workflow_name}")

        flow = self._create_flow()
        stream = flow()
        return stream


class WorkflowVersionStreamExecutor(StreamExecutorBase, WorkflowVersionExecutor):
    """Stream executor for versioned workflows."""

    def __init__(
        self,
        workflow_id: str,
        version: str,
        snapshot: Dict[str, Any],
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
    ):
        WorkflowVersionExecutor.__init__(
            self,
            workflow_id=workflow_id,
            version=version,
            snapshot=snapshot,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
        )


class WorkflowDebugStreamExecutor(StreamExecutorBase, WorkflowDebugExecutor):
    """Stream executor for debug workflows."""

    def __init__(
        self,
        workflow_id: str,
        snapshot: Dict[str, Any],
        snapshot_timestamp: datetime,
        snapshot_hash: str,
        input_data: Dict[str, Any],
        execution_context: Dict[str, Any],
    ):
        WorkflowDebugExecutor.__init__(
            self,
            workflow_id=workflow_id,
            snapshot=snapshot,
            snapshot_timestamp=snapshot_timestamp,
            snapshot_hash=snapshot_hash,
            input_data=input_data,
            execution_context=execution_context,
        )
