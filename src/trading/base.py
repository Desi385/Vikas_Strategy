from typing import Dict, List, Optional
from abc import ABC, abstractmethod
import logging
from datetime import datetime

from strategy.delta_neutral import DeltaNeutralStrategy

class TradingExecutor(ABC):
    """Abstract base class for trading execution."""
    
    def __init__(self, strategy: DeltaNeutralStrategy):
        """
        Initialize the trading executor.
        
        Args:
            strategy: Instance of DeltaNeutralStrategy
        """
        self.strategy = strategy
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def place_order(self, symbol: str, quantity: int, side: str, order_type: str = "MARKET") -> Dict:
        """
        Place a new order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: Order side ("BUY" or "SELL")
            order_type: Order type (default: "MARKET")
            
        Returns:
            Order details dictionary
        """
        pass

    @abstractmethod
    def get_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current market data for symbols.
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary of market data for each symbol
        """
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """
        Get current positions.
        
        Returns:
            List of current positions
        """
        pass

    @abstractmethod
    def get_orders(self) -> List[Dict]:
        """
        Get current orders.
        
        Returns:
            List of current orders
        """
        pass

    def execute_trades(self, signals: List[Dict]) -> List[Dict]:
        """
        Execute a list of trade signals.
        
        Args:
            signals: List of trade signals
            
        Returns:
            List of executed order details
        """
        executed_orders = []
        
        for signal in signals:
            try:
                order = self.place_order(
                    symbol=signal['symbol'],
                    quantity=signal['quantity'],
                    side=signal['action']
                )
                executed_orders.append(order)
                self.logger.info(f"Executed trade: {signal}")
            except Exception as e:
                self.logger.error(f"Failed to execute trade {signal}: {str(e)}")
                
        return executed_orders

    def update_portfolio(self) -> None:
        """Update portfolio with current market data."""
        try:
            symbols = [pos.symbol for pos in self.strategy.portfolio.positions.values()]
            if symbols:
                market_data = self.get_market_data(symbols)
                self.strategy.update_positions(market_data)
        except Exception as e:
            self.logger.error(f"Failed to update portfolio: {str(e)}")

    def check_and_adjust_portfolio(self) -> None:
        """Check if portfolio needs adjustment and execute necessary trades."""
        try:
            needs_adjustment, adjustments = self.strategy.check_adjustment_needed()
            
            if needs_adjustment:
                self.logger.info("Portfolio adjustment needed")
                self.execute_trades(adjustments)
            
        except Exception as e:
            self.logger.error(f"Failed to adjust portfolio: {str(e)}")

    def monitor_and_execute(self) -> None:
        """Main execution loop for monitoring and trading."""
        try:
            # Update portfolio with current market data
            self.update_portfolio()
            
            # Check and execute exit signals
            exit_signals = self.strategy.get_exit_signals()
            if exit_signals:
                self.execute_trades(exit_signals)
            
            # Check and execute entry signals
            entry_signals = self.strategy.get_entry_signals(
                self.get_market_data([])  # Pass relevant options data
            )
            if entry_signals:
                self.execute_trades(entry_signals)
            
            # Check and adjust portfolio delta
            self.check_and_adjust_portfolio()
            
        except Exception as e:
            self.logger.error(f"Error in monitor and execute loop: {str(e)}")

    def start(self) -> None:
        """Start the trading execution."""
        self.logger.info("Starting trading execution...")
        
        while True:
            if not self.strategy.is_trading_time():
                self.logger.info("Outside trading hours, waiting...")
                continue
                
            self.monitor_and_execute()