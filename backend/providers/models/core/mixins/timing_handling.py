import time


class TimingHandlingMixin:
    """Mixin class for tracking model invocation timing."""
    
    _invoke_start_time: float = 0

    def start_invoke_timer(self) -> None:
        """Start the timer for model invocation latency calculation."""
        self._invoke_start_time = time.perf_counter()

    def get_invoke_latency(self) -> float:
        """Calculate the latency since invoke started."""
        return time.perf_counter() - self._invoke_start_time 