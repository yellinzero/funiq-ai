from __future__ import annotations

import uuid
from datetime import datetime
from json import JSONDecodeError
from pathlib import Path
from typing import Any, AsyncGenerator

import aiofiles.os
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure import with_session
from utils.common.json import json_loads

from .models import WorkflowDebugExecution, WorkflowDebugLog, WorkflowExecution, WorkflowExecutionLog
from .schemas import WorkflowLog


class WorkflowLoggerConfig:
    """Workflow logger configuration."""

    LOG_DIR = "logs/workflow"
    LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<yellow>WORKFLOW</yellow> | "
        "<magenta>{extra[run_id]}</magenta> | "
        "<blue>{extra[node_run_id]}</blue> | "
        "<cyan>{name}:{function}:{line}</cyan> | "
        "<level>{message}</level>"
    )


class WorkflowLogger:
    """Workflow logger that writes to file and manages log lifecycle."""

    def __init__(
        self,
        run_id: str,
        created_by: str,
        is_debug: bool = False,
        node_run_id: str | None = None,
    ):
        self._run_id = run_id
        self._created_by = created_by
        self._is_debug = is_debug
        self._node_run_id = node_run_id
        self._handler_id = None

        self._log_dir = Path(WorkflowLoggerConfig.LOG_DIR)
        self._log_dir.mkdir(parents=True, exist_ok=True)

        self._log_file = self._log_dir / f"{run_id}{'_debug' if is_debug else ''}.log"
        self._setup_logging()

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def created_by(self) -> str:
        return self._created_by

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @property
    def node_run_id(self) -> str | None:
        return self._node_run_id    

    @property
    def log_file(self) -> Path:
        return self._log_file

    @property
    def log_dir(self) -> Path:
        return self._log_dir

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        handler_id = str(uuid.uuid4())  # 为每个处理器生成唯一ID
        self._handler_id = logger.add(
            str(self.log_file),
            format=WorkflowLoggerConfig.LOG_FORMAT,
            enqueue=True,
            serialize=True,
            filter=lambda record: (
                "workflow" in record["extra"] and 
                record["extra"].get("run_id") == self.run_id and
                record["extra"].get("node_run_id") == self.node_run_id
            )
        )

    def _get_context_data(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "workflow": True,
            "run_id": self.run_id,
            "node_run_id": self.node_run_id,
            "created_by": self.created_by,
            "context": context or {},
        }

    def _cleanup_handler(self) -> None:
        """Cleanup the logger handler."""
        if self._handler_id is not None:
            logger.remove(self._handler_id)
            self._handler_id = None

    def _cleanup(self) -> None:
        """Cleanup the logger and remove file."""
        self._cleanup_handler()
            
        # delete file after archiving
        if self.log_file.exists():
            try:
                self.log_file.unlink()
            except Exception as e:
                logger.error(f"Error removing log file: {e}")

    def __del__(self) -> None:
        """Destructor to cleanup the logger."""
        self._cleanup()

    @with_session
    async def archive_logs(self, session: AsyncSession) -> None:
        """Archive logs from file to database."""
        if not self.log_file.exists():
            logger.warning(f"Log file {self.log_file} does not exist")
            return
    
        try:
            log_model = WorkflowDebugLog if self.is_debug else WorkflowExecutionLog
            logs_to_insert = []

            async with aiofiles.open(self.log_file) as f:
                async for line in f:
                    try:
                        log_data = json_loads(line)

                        if not isinstance(log_data, dict):
                            logger.error(f"Invalid log data format, expected dict but got: {type(log_data)}")
                            continue

                        record = log_data.get("record", {})
                        if not record:
                            logger.error(f"Missing record in log data: {log_data}")
                            continue

                        level = record.get("level", {}).get("name", "INFO")
                        time_data = record.get("time", {})
                        timestamp = time_data.get("timestamp")
                        extra_data = record.get("extra", {})

                        if not timestamp:
                            logger.error(f"Missing timestamp in record data: {record}")
                            continue

                        try:
                            timestamp = datetime.fromtimestamp(timestamp)
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid timestamp format: {timestamp}, error: {e}")
                            continue
                        
                        log_entry = log_model(
                            run_id=self.run_id,
                            level=level,
                            message=record.get("message", ""),
                            timestamp=timestamp,
                            context=extra_data,
                            created_by=extra_data.get("created_by", self.created_by),
                        )

                        logs_to_insert.append(log_entry)

                        # batch insert
                        if len(logs_to_insert) >= 1000:
                            session.add_all(logs_to_insert)
                            await session.commit()
                            logs_to_insert = []

                    except JSONDecodeError as e:
                        logger.error(f"Invalid JSON in log file: {line}, error: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing log line: {line}, error: {e}")
                        continue

            # insert remaining logs
            if logs_to_insert:
                session.add_all(logs_to_insert)
                await session.commit()

            # delete file after archiving
            await aiofiles.os.remove(self.log_file)
            self._cleanup_handler()

        except Exception as e:
            logger.error(f"Failed to archive logs for workflow {self.run_id}: {e}", exc_info=True)
            raise

    # log methods
    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        logger.bind(**self._get_context_data(context)).debug(message)

    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        logger.bind(**self._get_context_data(context)).info(message)

    def warning(self, message: str, context: dict[str, Any] | None = None) -> None:
        logger.bind(**self._get_context_data(context)).warning(message)

    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        logger.bind(**self._get_context_data(context)).error(message)

    def critical(self, message: str, context: dict[str, Any] | None = None) -> None:
        logger.bind(**self._get_context_data(context)).critical(message)


class WorkflowLogReader:
    """Workflow log reader that handles both file and database sources."""

    def __init__(self, run_id: str, is_debug: bool = False):
        self.run_id = run_id
        self.is_debug = is_debug
        self.log_file = Path(WorkflowLoggerConfig.LOG_DIR) / f"{run_id}.log"

    @with_session
    async def is_workflow_terminated(self, session: AsyncSession) -> bool:
        run_model = WorkflowDebugExecution if self.is_debug else WorkflowExecution
        workflow_execution = await session.execute(select(run_model).where(run_model.run_id == self.run_id))
        workflow_execution = workflow_execution.scalar_one_or_none()
        return workflow_execution and workflow_execution.is_terminated

    @with_session
    async def get_logs_from_db(
        self,
        session: AsyncSession,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[dict]:
        log_model = WorkflowDebugLog if self.is_debug else WorkflowExecutionLog
        query = select(log_model).where(log_model.run_id == self.run_id)

        if start_time:
            query = query.where(log_model.timestamp >= start_time)
        if end_time:
            query = query.where(log_model.timestamp <= end_time)

        query = query.order_by(log_model.timestamp.asc())
        result = await session.execute(query)
        logs = result.scalars().all()

        return [
            {"timestamp": log.timestamp, "level": log.level, "message": log.message, "context": log.context}
            for log in logs
        ]

    async def read_file_logs(self, start_position: int = 0) -> AsyncGenerator[WorkflowLog, None]:
        if not self.log_file.exists():
            return

        async with aiofiles.open(self.log_file) as f:
            await f.seek(start_position)
            while True:
                line = await f.readline()
                if not line:
                    break

                try:
                    log_data = json_loads(line)
                    record = log_data.get("record", {})
                    if not record:
                        continue

                    time_data = record.get("time", {})
                    timestamp = time_data.get("timestamp")
                    if not timestamp:
                        continue

                    yield {
                        "timestamp": datetime.fromtimestamp(timestamp),
                        "level": record.get("level", {}).get("name", "INFO"),
                        "message": record.get("message", ""),
                        "context": record.get("extra", {}),
                    }
                except Exception as e:
                    logger.error(f"Error processing log line: {line}, error: {e}")
                    continue

    async def get_logs(
        self,
        start_position: int = 0,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> AsyncGenerator[WorkflowLog, None]:
        """get logs from file or database"""
        is_terminated = await self.is_workflow_terminated()

        if is_terminated:
            # workflow is terminated, read from database
            logs = await self.get_logs_from_db(start_time, end_time)
            for log in logs:
                yield log
        else:
            # workflow is not completed, read from file
            async for log in self.read_file_logs(start_position):
                yield log
