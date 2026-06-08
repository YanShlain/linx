import sys
from typing import Any


class LinxException(Exception):
    """Application exception with the failing operation and its input parameters."""

    def __init__(
        self,
        operation: str,
        parameters: dict[str, Any] | None = None,
        *,
        cause: BaseException | None = None,
    ) -> None:
        """Initialize a LinxException.

        Args:
            operation: Name of the function or method where the failure occurred.
            parameters: Input arguments active at the point of failure.
            cause: Original exception, if any.
        """
        self.operation = operation
        self.parameters = dict(parameters or {})
        self.cause = cause
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        param_text = ", ".join(
            f"{key}={value!r}" for key, value in self.parameters.items()
        )
        parts = [f"operation={self.operation!r}"]
        if param_text:
            parts.append(f"parameters=({param_text})")
        if self.cause is not None:
            parts.append(f"cause={self.cause!r}")
        return "; ".join(parts)

    @classmethod
    def wrap(
        cls,
        operation: str,
        parameters: dict[str, Any],
        cause: BaseException,
    ) -> "LinxException":
        """Wrap a caught exception unless it is already a LinxException.

        Args:
            operation: Name of the function or method where the failure occurred.
            parameters: Input arguments active at the point of failure.
            cause: Exception to wrap.

        Returns:
            A LinxException describing the failure.
        """
        if isinstance(cause, cls):
            return cause
        return cls(operation=operation, parameters=parameters, cause=cause)


def report_linx_error(exc: LinxException) -> None:
    """Print a LinxException to stderr.

    Args:
        exc: Exception to report.
    """
    print(f"Error: {exc}", file=sys.stderr)
