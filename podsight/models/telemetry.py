"""Telemetry data models from cluster sources."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ContainerTelemetry:
    """Resource usage for a single container."""

    name: str
    cpu_request_millicores: int
    cpu_limit_millicores: int
    memory_request_bytes: int
    memory_limit_bytes: int
    cpu_usage_millicores: int
    memory_usage_bytes: int
    restart_count: int = 0
    ready: bool = True


@dataclass(frozen=True)
class PodTelemetry:
    """Telemetry data for a single pod."""

    namespace: str
    name: str
    uid: str
    node_name: str
    phase: str
    containers: list[ContainerTelemetry]
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    creation_timestamp: Optional[datetime] = None
    start_time: Optional[datetime] = None
    qos_class: str = "BestEffort"

    @property
    def total_cpu_request_millicores(self) -> int:
        return sum(c.cpu_request_millicores for c in self.containers)

    @property
    def total_cpu_limit_millicores(self) -> int:
        return sum(c.cpu_limit_millicores for c in self.containers)

    @property
    def total_memory_request_bytes(self) -> int:
        return sum(c.memory_request_bytes for c in self.containers)

    @property
    def total_memory_limit_bytes(self) -> int:
        return sum(c.memory_limit_bytes for c in self.containers)

    @property
    def total_cpu_usage_millicores(self) -> int:
        return sum(c.cpu_usage_millicores for c in self.containers)

    @property
    def total_memory_usage_bytes(self) -> int:
        return sum(c.memory_usage_bytes for c in self.containers)

    @property
    def cpu_request_utilization(self) -> float:
        if self.total_cpu_request_millicores == 0:
            return 0.0
        return self.total_cpu_usage_millicores / self.total_cpu_request_millicores

    @property
    def memory_request_utilization(self) -> float:
        if self.total_memory_request_bytes == 0:
            return 0.0
        return self.total_memory_usage_bytes / self.total_memory_request_bytes


@dataclass(frozen=True)
class NodeTelemetry:
    """Telemetry data for a node."""

    name: str
    cpu_capacity_millicores: int
    memory_capacity_bytes: int
    cpu_allocatable_millicores: int
    memory_allocatable_bytes: int
    cpu_usage_millicores: int
    memory_usage_bytes: int
    labels: dict[str, str] = field(default_factory=dict)
    taints: list[str] = field(default_factory=list)
    conditions: dict[str, str] = field(default_factory=dict)

    @property
    def cpu_allocatable_utilization(self) -> float:
        if self.cpu_allocatable_millicores == 0:
            return 0.0
        return self.cpu_usage_millicores / self.cpu_allocatable_millicores

    @property
    def memory_allocatable_utilization(self) -> float:
        if self.memory_allocatable_bytes == 0:
            return 0.0
        return self.memory_usage_bytes / self.memory_allocatable_bytes