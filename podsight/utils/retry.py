"""Retry policies with exponential backoff and jitter."""

import asyncio
import random
import time
from dataclasses import dataclass
from functools import wraps
from typing import Callable, TypeVar, Awaitable, Optional

from podsight.exceptions import PodSightError

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (PodSightError,)

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        delay = min(self.base_delay * (self.exponential_base ** attempt), self.max_delay)
        if self.jitter:
            delay *= 0.5 + random.random()  # 0.5x to 1.5x
        return delay


async def with_retry(
    func: Callable[..., Awaitable[T]],
    *args,
    policy: Optional[RetryPolicy] = None,
    **kwargs,
) -> T:
    """Execute async function with retry policy."""
    policy = policy or RetryPolicy()
    last_exception: Optional[Exception] = None

    for attempt in range(policy.max_attempts):
        try:
            return await func(*args, **kwargs)
        except policy.retryable_exceptions as e:
            last_exception = e
            if not getattr(e, "retryable", True):
                raise
            if attempt < policy.max_attempts - 1:
                delay = policy.calculate_delay(attempt)
                await asyncio.sleep(delay)
            continue
        except Exception as e:
            last_exception = e
            raise

    raise last_exception


def with_retry_sync(
    func: Callable[..., T],
    *args,
    policy: Optional[RetryPolicy] = None,
    **kwargs,
) -> T:
    """Execute sync function with retry policy."""
    policy = policy or RetryPolicy()
    last_exception: Optional[Exception] = None

    for attempt in range(policy.max_attempts):
        try:
            return func(*args, **kwargs)
        except policy.retryable_exceptions as e:
            last_exception = e
            if not getattr(e, "retryable", True):
                raise
            if attempt < policy.max_attempts - 1:
                delay = policy.calculate_delay(attempt)
                time.sleep(delay)
            continue
        except Exception as e:
            last_exception = e
            raise

    raise last_exception


class CircuitBreakerState:
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """
    Circuit breaker implementation for preventing cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests fail fast
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 30.0,
        excluded_exceptions: tuple[type[Exception], ...] = (),
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.excluded_exceptions = excluded_exceptions

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    @property
    def state(self) -> str:
        return self._state

    def _is_excluded(self, exc: Exception) -> bool:
        return isinstance(exc, self.excluded_exceptions)

    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self._state == CircuitBreakerState.OPEN:
                if self._last_failure_time and (
                    time.time() - self._last_failure_time >= self.timeout_seconds
                ):
                    self._state = CircuitBreakerState.HALF_OPEN
                    self._success_count = 0
                else:
                    from podsight.exceptions import CircuitOpenError
                    raise CircuitOpenError(
                        f"Circuit breaker '{self.name}' is OPEN",
                        circuit_name=self.name,
                        retry_after_seconds=self.timeout_seconds - (time.time() - self._last_failure_time),
                    )

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            if not self._is_excluded(e):
                await self._on_failure()
            raise

    async def _on_success(self):
        async with self._lock:
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._state = CircuitBreakerState.CLOSED
                    self._failure_count = 0
            elif self._state == CircuitBreakerState.CLOSED:
                self._failure_count = 0

    async def _on_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.OPEN
            elif self._state == CircuitBreakerState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitBreakerState.OPEN

    def reset(self):
        """Manually reset circuit breaker to closed state."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None


# Registry for circuit breakers
_circuit_breakers: dict[str, CircuitBreaker] = {}


def circuit_breaker(
    name: str,
    *,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout_seconds: float = 30.0,
    excluded_exceptions: tuple[type[Exception], ...] = (),
) -> CircuitBreaker:
    """Get or create a circuit breaker by name."""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout_seconds=timeout_seconds,
            excluded_exceptions=excluded_exceptions,
        )
    return _circuit_breakers[name]


def get_circuit_breaker(name: str) -> Optional[CircuitBreaker]:
    """Get circuit breaker by name."""
    return _circuit_breakers.get(name)


def reset_all_circuits():
    """Reset all circuit breakers."""
    for cb in _circuit_breakers.values():
        cb.reset()