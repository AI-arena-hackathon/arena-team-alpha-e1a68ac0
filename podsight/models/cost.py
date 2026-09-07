"""Cost calculation models."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional


class CloudProvider(str, Enum):
    """Supported cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    OPENSHIFT = "openshift"
    ON_PREMISE = "on_premise"


@dataclass(frozen=True)
class ProviderCostRate:
    """Cost rates from a cloud provider."""

    provider: CloudProvider
    region: str
    instance_type: str
    cpu_cost_per_hour: Decimal
    memory_cost_per_gib_hour: Decimal
    currency: str = "USD"
    effective_date: Optional[str] = None


@dataclass(frozen=True)
class CostBreakdown:
    """Detailed cost breakdown for a pod."""

    cpu_cost_per_hour: Decimal
    memory_cost_per_hour: Decimal
    total_cost_per_hour: Decimal
    currency: str
    provider: CloudProvider
    region: str
    instance_type: str


@dataclass(frozen=True)
class PodCost:
    """Cost information for a pod."""

    pod_namespace: str
    pod_name: str
    pod_uid: str
    hourly_cost: Decimal
    monthly_cost_estimate: Decimal
    breakdown: CostBreakdown
    waste_cost_per_hour: Decimal = Decimal("0")
    waste_percentage: float = 0.0

    @property
    def annual_cost_estimate(self) -> Decimal:
        return self.monthly_cost_estimate * 12