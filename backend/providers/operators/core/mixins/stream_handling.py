from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator
from typing import Any, ClassVar, Dict, List, Tuple

from ..schemas import OperatorEntity, OutputStream


class StreamHandlingMixin(ABC):
    """Mixin class for handling stream operations."""

    _stream_node_ids: ClassVar[List[str]] = []
    _execution_context: Dict[str, Any]
    _supports_input_stream: bool = False
    _output_stream: OutputStream | None = None

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
    def supports_input_stream(self) -> bool:
        """Get stream input support from operator schema."""
        schema = self.get_operator_schema()
        self._supports_input_stream = (
            schema.supports_input_stream if hasattr(schema, "supports_input_stream") else False
        )
        return self._supports_input_stream

    @property
    def supports_output_stream(self) -> bool:
        """Get stream output support from operator schema."""
        schema = self.get_operator_schema()
        self._output_stream = schema.output_stream if hasattr(schema, "output_stream") else None
        return self._output_stream.enabled if self._output_stream else False

    def is_stream_input(self, input_data: Any) -> bool:
        """Check if a single input is a stream."""
        return isinstance(input_data, (Generator, AsyncGenerator))

    def prepare_stream_handling(
        self, input_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Generator]]:
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
