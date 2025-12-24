"""User model for Family Wealth AI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model representing a family member."""

    user_id: str
    display_name: str
    monthly_budget: int = 10000
    target_allocation: dict = field(
        default_factory=lambda: {"gold": 50, "stocks": 30, "crypto": 20}
    )
    risk_profile: str = "moderate"
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User from a dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            display_name=data.get("display_name", ""),
            monthly_budget=int(data.get("monthly_budget", 10000)),
            target_allocation=data.get("target_allocation", {}),
            risk_profile=data.get("risk_profile", "moderate"),
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> dict:
        """Convert User to dictionary."""
        return {
            "user_id": self.user_id,
            "display_name": self.display_name,
            "monthly_budget": self.monthly_budget,
            "target_allocation": self.target_allocation,
            "risk_profile": self.risk_profile,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }
