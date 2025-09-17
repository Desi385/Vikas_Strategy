from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

from .portfolio import PortfolioManager, Position

class DeltaNeutralStrategy:
    def __init__(self, config: Dict):
        """
        Initialize the delta neutral strategy.
        
        Args:
            config: Strategy configuration dictionary
        """
        self.config = config
        self.portfolio = PortfolioManager(target_delta=config['strategy']['target_delta'])
        self.logger = logging.getLogger(__name__)

    def is_trading_time(self) -> bool:
        """Check if current time is within trading hours."""
        now = datetime.now().time()
        start_time = datetime.strptime(self.config['trading']['trading_hours']['start'], '%H:%M').time()
        end_time = datetime.strptime(self.config['trading']['trading_hours']['end'], '%H:%M').time()
        return start_time <= now <= end_time

    def select_options(self, spot_price: float, options_chain: List[Dict]) -> List[Dict]:
        """
        Select suitable options for the strategy based on spot price and options chain.
        
        Args:
            spot_price: Current spot price of the underlying
            options_chain: List of available options with their details
            
        Returns:
            List of selected options to trade
        """
        min_premium = self.config['strategy']['min_premium']
        max_positions = self.config['strategy']['max_positions']
        
        # Filter options by minimum premium
        valid_options = [
            opt for opt in options_chain 
            if float(opt['last_price']) >= min_premium
        ]
        
        # Sort by liquidity (bid-ask spread)
        valid_options.sort(key=lambda x: abs(float(x['bid_price']) - float(x['ask_price'])))
        
        # Select options closest to spot price
        call_options = [opt for opt in valid_options if opt['instrument_type'] == 'CE']
        put_options = [opt for opt in valid_options if opt['instrument_type'] == 'PE']
        
        selected_options = []
        for options in [call_options, put_options]:
            if options:
                options.sort(key=lambda x: abs(float(x['strike']) - spot_price))
                selected_options.extend(options[:max_positions//2])
        
        return selected_options[:max_positions]

    def calculate_position_size(self, option: Dict) -> int:
        """
        Calculate the appropriate position size for an option.
        
        Args:
            option: Option details dictionary
            
        Returns:
            Number of contracts to trade
        """
        capital = self.config['trading']['capital']
        position_sizing = self.config['strategy']['position_sizing']
        
        max_risk = capital * (self.config['trading']['max_loss_percentage'] / 100)
        option_price = float(option['last_price'])
        
        # Calculate max quantity based on risk per trade
        max_quantity = int(max_risk / option_price)
        
        # Apply position sizing factor
        target_quantity = int(max_quantity * position_sizing)
        
        # Ensure minimum quantity of 1
        return max(1, target_quantity)

    def check_adjustment_needed(self) -> Tuple[bool, List[dict]]:
        """
        Check if portfolio needs delta adjustment and calculate required trades.
        
        Returns:
            Tuple of (needs_adjustment: bool, adjustment_trades: List[dict])
        """
        threshold = self.config['strategy']['adjustment_threshold']
        adjustments = self.portfolio.get_adjustment_trades(threshold)
        return bool(adjustments), adjustments

    def update_positions(self, market_data: Dict[str, Dict]) -> None:
        """
        Update current positions with latest market data.
        
        Args:
            market_data: Dictionary of current market prices and greeks
        """
        for symbol, position in self.portfolio.positions.items():
            if symbol in market_data:
                data = market_data[symbol]
                self.portfolio.update_position(
                    symbol,
                    current_price=Decimal(str(data['last_price'])),
                    delta=Decimal(str(data['delta']))
                )

    def get_entry_signals(self, options_data: List[Dict]) -> List[Dict]:
        """
        Generate entry signals for new positions.
        
        Args:
            options_data: List of available options with their details
            
        Returns:
            List of entry signals with option details and quantities
        """
        signals = []
        current_positions = len(self.portfolio.positions)
        max_positions = self.config['strategy']['max_positions']
        
        if current_positions >= max_positions:
            return signals
            
        selected_options = self.select_options(
            spot_price=options_data[0]['underlying_price'],
            options_chain=options_data
        )
        
        for option in selected_options:
            quantity = self.calculate_position_size(option)
            signals.append({
                'symbol': option['symbol'],
                'action': 'BUY',
                'quantity': quantity,
                'option_type': option['instrument_type'],
                'strike_price': option['strike'],
                'expiry': option['expiry']
            })
            
        return signals

    def get_exit_signals(self) -> List[Dict]:
        """
        Generate exit signals based on profit targets or stop losses.
        
        Returns:
            List of exit signals for current positions
        """
        signals = []
        target_profit = self.config['trading']['target_profit_percentage'] / 100
        max_loss = self.config['trading']['max_loss_percentage'] / 100
        
        for symbol, position in self.portfolio.positions.items():
            pnl_percentage = float(position.pnl) / (float(position.entry_price) * position.quantity)
            
            if pnl_percentage >= target_profit or pnl_percentage <= -max_loss:
                signals.append({
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': position.quantity,
                    'reason': 'target_hit' if pnl_percentage >= target_profit else 'stop_loss'
                })
                
        return signals

    def __str__(self) -> str:
        """String representation of the strategy state."""
        return (f"Delta Neutral Strategy Status:\n"
                f"{str(self.portfolio)}\n"
                f"Trading Configuration:\n"
                f"Max Loss %: {self.config['trading']['max_loss_percentage']}%\n"
                f"Target Profit %: {self.config['trading']['target_profit_percentage']}%\n"
                f"Position Sizing: {self.config['strategy']['position_sizing']}x")