from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from typing import Any, ClassVar, Dict, List, Tuple

from loguru import logger

from ..schemas import OperatorEntity, OutputStream, StreamDependency


class StreamHandlingMixin(ABC):
    """Mixin class for handling stream operations."""

    _stream_node_ids: ClassVar[List[str]]
    _execution_context: Dict[str, Any]
    _output_stream: OutputStream | None
    _config_value_paths_map: Dict[str, List[str]]

    @abstractmethod
    def get_operator_schema(self) -> OperatorEntity:
        """Get the operator schema."""
        pass

    @property
    def stream_node_ids(self) -> List[str]:
        """Get the stream node IDs."""
        return self._stream_node_ids

    @property
    def is_stream(self) -> bool:
        """Get stream mode from execution context."""
        return self._execution_context.get("stream_mode", False)

    @property
    def has_stream_inputs(self) -> bool:
        """Check if any input is a stream."""
        return len(self.stream_node_ids) > 0

    @property
    def supports_output_stream(self) -> bool:
        """Get stream output support from operator schema."""
        schema = self.get_operator_schema()
        self._output_stream = schema.output_stream if hasattr(schema, "output_stream") else None
        return self._output_stream.enabled if self._output_stream else False

    def is_stream_input(self, input_data: Any) -> bool:
        """Check if a single input is a stream."""
        return isinstance(input_data, (Generator, AsyncGenerator))

    def prepare_stream_handling(self, input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Generator]]:
        """Prepare for stream handling by classifying inputs and recording stream node IDs.

        Args:
            input_data: Original input data dictionary

        Returns:
            Tuple[Dict[str, Any], Dict[str, Generator]]:
                - non_stream_inputs: Dictionary containing regular input data
                - stream_inputs: Dictionary mapping node IDs to their stream generators
        """
        non_stream_inputs = {}
        stream_inputs: Dict[str, Generator] = {}

        # Clear previous stream node IDs
        self._stream_node_ids = []

        for node_id, data in input_data.items():
            if self.is_stream_input(data):
                stream_inputs[node_id] = data
                self._stream_node_ids.append(node_id)
            else:
                non_stream_inputs[node_id] = data

        return non_stream_inputs, stream_inputs

    def _get_value_by_path(self, obj: Any, path: str) -> Any:
        """Get value from object by path, supporting both dict and object attribute access."""
        value = obj
        for part in path.split('.'):
            value = value[part] if isinstance(value, dict) else getattr(value, part)
        return value

    def render_stream_chunk_data(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render stream chunk data from input data"""
        config = {}

        for config_key, template_paths in self._config_value_paths_map.items():
            if len(template_paths) > 1:
                logger.error(f"Multiple stream inputs detected for {config_key}.")
                raise ValueError(f"Multiple stream inputs detected for {config_key}.")
            
            try:
                template_path = template_paths[0]
                value = self._get_value_by_path(chunk_data, template_path)
                
                current = config
                config_parts = config_key.split(".")
                
                for i, part in enumerate(config_parts):
                    if i == len(config_parts) - 1:
                        current[part] = value
                    else:
                        if part not in current:
                            current[part] = {}
                        current = current[part]

            except (KeyError, TypeError, AttributeError) as e:
                logger.warning(f"Error processing stream input for {config_key}: {e}")
                continue

        return config

    def _analyze_stream_dependencies(self) -> dict[str, StreamDependency]:
        """analyze stream dependencies"""
        dependencies = {}
        for config_key, template_paths in self._config_value_paths_map.items():
            required_streams = set()
            for path in template_paths:
                stream_id = path.split('.')[0]
                required_streams.add(stream_id)
            dependencies[config_key] = StreamDependency(
                config_key=config_key,
                required_streams=required_streams,
                current_chunks={}
            )
        return dependencies

    async def handle_multiple_streams(self, stream_inputs: Dict[str, AsyncGenerator]) -> AsyncGenerator:
        """handle multiple streams"""

        dependencies = self._analyze_stream_dependencies()
        
        stream_status = dict.fromkeys(stream_inputs, True)
        
        while any(stream_status.values()):
            # collect new chunks
            for stream_id, generator in stream_inputs.items():
                if not stream_status[stream_id]:
                    continue
                    
                try:
                    chunk = await generator.__anext__()
                    for dep in dependencies.values():
                        if stream_id in dep.required_streams:
                            dep.current_chunks[stream_id] = {stream_id: chunk}
                except StopAsyncIteration:
                    stream_status[stream_id] = False
                    continue
            
            # check if all required streams have data
            all_streams_ready = True
            required_streams = set()
            for dep in dependencies.values():
                required_streams.update(dep.required_streams)
                if not dep.required_streams.issubset(dep.current_chunks.keys()):
                    all_streams_ready = False
                    break
            
            if all_streams_ready:
                # merge all stream data into a single chunk
                merged_chunk = {}
                for stream_id in required_streams:
                    # find the current_chunks that contains the stream_id
                    for dep in dependencies.values():
                        if stream_id in dep.current_chunks:
                            merged_chunk.update(dep.current_chunks[stream_id])
                            break
                
                rendered_value = self.render_stream_chunk_data(merged_chunk)
                
                # clean up processed data
                for dep in dependencies.values():
                    for stream_id in dep.required_streams:
                        dep.current_chunks.pop(stream_id)
                
                yield rendered_value
