"""Custom exceptions for PodSight with structured error information."""


class PodSightError(Exception):
    """Base exception for all PodSight errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "PODSIGHT_ERROR",
        details: dict | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.retryable = retryable

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "retryable": self.retryable,
            }
        }


class TelemetryError(PodSightError):
    """Error collecting telemetry from cluster."""

    def __init__(
        self,
        message: str,
        *,
        source: str,
        details: dict | None = None,
        retryable: bool = True,
    ):
        super().__init__(
            message,
            code="TELEMETRY_ERROR",
            details={"source": source, **(details or {})},
            retryable=retryable,
        )
        self.source = source


class CostAdapterError(PodSightError):
    """Error from cost adapter (billing API)."""

    def __init__(
        self,
        message: str,
        *,
        provider: str,
        details: dict | None = None,
        retryable: bool = True,
    ):
        super().__init__(
            message,
            code="COST_ADAPTER_ERROR",
            details={"provider": provider, **(details or {})},
            retryable=retryable,
        )
        self.provider = provider


class ValidationError(PodSightError):
    """Input validation error."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        details: dict | None = None,
    ):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field, **(details or {})},
            retryable=False,
        )
        self.field = field


class PlaybookError(PodSightError):
    """Error executing remediation playbook."""

    def __init__(
        self,
        message: str,
        *,
        playbook_id: str,
        step: str | None = None,
        details: dict | None = None,
        retryable: bool = False,
    ):
        super().__init__(
            message,
            code="PLAYBOOK_ERROR",
            details={"playbook_id": playbook_id, "step": step, **(details or {})},
            retryable=retryable,
        )
        self.playbook_id = playbook_id
        self.step = step


class ResourceNotFoundError(PodSightError):
    """Resource not found error."""

    def __init__(
        self,
        message: str,
        *,
        resource_type: str,
        resource_id: str,
        details: dict | None = None,
    ):
        super().__init__(
            message,
            code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id, **(details or {})},
            retryable=False,
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class CircuitOpenError(PodSightError):
    """Circuit breaker is open."""

    def __init__(
        self,
        message: str,
        *,
        circuit_name: str,
        retry_after_seconds: float,
        details: dict | None = None,
    ):
        super().__init__(
            message,
            code="CIRCUIT_OPEN",
            details={"circuit_name": circuit_name, "retry_after_seconds": retry_after_seconds, **(details or {})},
            retryable=True,
        )
        self.circuit_name = circuit_name
        self.retry_after_seconds = retry_after_seconds