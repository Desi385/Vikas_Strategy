from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

@dataclass
class Position:
    symbol: str
    quantity: int
    entry_price: Decimal
    current_price: Decimal
    delta: Decimal
    option_type: str  # 'CE' or 'PE'
    strike_price: int
    expiry: str

    @property
    def pnl(self) -> Decimal:
        """Calculate the current P&L for the position."""
        return Decimal(str((self.current_price - self.entry_price) * self.quantity))

    @property
    def net_delta(self) -> Decimal:
        """Calculate the net delta contribution of the position."""
        return self.delta * self.quantity

class PortfolioManager:
    def __init__(self, target_delta: float = 0.0):
        self.positions: Dict[str, Position] = {}
        self.target_delta = Decimal(str(target_delta))
    
    @property
    def total_delta(self) -> Decimal:
        """Calculate the total delta of the portfolio."""
        return sum(pos.net_delta for pos in self.positions.values())

    @property
    def delta_deviation(self) -> Decimal:
        """Calculate how far the current delta is from the target."""
        return self.total_delta - self.target_delta

    def add_position(self, position: Position) -> None:
        """Add a new position to the portfolio."""
        self.positions[position.symbol] = position

    def remove_position(self, symbol: str) -> None:
        """Remove a position from the portfolio."""
        if symbol in self.positions:
            del self.positions[symbol]

    def update_position(self, symbol: str, **kwargs) -> None:
        """Update an existing position's attributes."""
        if symbol in self.positions:
            position = self.positions[symbol]
            for key, value in kwargs.items():
                if hasattr(position, key):
                    setattr(position, key, value)

    def get_adjustment_trades(self, threshold: float = 0.1) -> List[dict]:
        """
        Calculate required adjustment trades to maintain delta neutrality.
        
        Args:
            threshold: Maximum acceptable deviation from target delta
        
        Returns:
            List of suggested trades to adjust the portfolio
        """
        deviation = float(self.delta_deviation)
        if abs(deviation) <= threshold:
            return []

        adjustments = []
        if deviation > threshold:
            # Portfolio is too positive delta, need to add negative delta
            adjustments.append({
                'action': 'BUY',
                'option_type': 'PE',
                'target_delta': -deviation
            })
        elif deviation < -threshold:
            # Portfolio is too negative delta, need to add positive delta
            adjustments.append({
                'action': 'BUY',
                'option_type': 'CE',
                'target_delta': abs(deviation)
            })

        return adjustments

    def get_total_pnl(self) -> Decimal:
        """Calculate the total P&L of the portfolio."""
        return sum(pos.pnl for pos in self.positions.values())

    def __str__(self) -> str:
        """String representation of the portfolio."""
        return (f"Portfolio Summary:\n"
                f"Total Positions: {len(self.positions)}\n"
                f"Total Delta: {self.total_delta:.2f}\n"
                f"Target Delta: {self.target_delta:.2f}\n"
                f"Current P&L: {self.get_total_pnl():.2f}")