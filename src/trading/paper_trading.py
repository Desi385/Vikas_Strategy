from typing import Dict, List
import pandas as pd
from decimal import Decimal
from datetime import datetime
import logging

from trading.base import TradingExecutor
from strategy.portfolio import Position

class PaperTradingExecutor(TradingExecutor):
    """Paper trading implementation for testing strategies."""

    def __init__(self, strategy, data_path: str = None):
        """
        Initialize paper trading executor.
        
        Args:
            strategy: Trading strategy instance
            data_path: Path to historical market data (optional)
        """
        super().__init__(strategy)
        self.positions: Dict[str, Position] = {}
        self.orders: List[Dict] = []
        self.market_data = self._load_market_data(data_path) if data_path else {}
        self.current_time = datetime.now()
        self.logger = logging.getLogger(__name__)

    def _load_market_data(self, data_path: str) -> Dict:
        """
        Load historical market data from file.
        
        Args:
            data_path: Path to market data file
            
        Returns:
            Dictionary of market data
        """
        try:
            df = pd.read_csv(data_path)
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Failed to load market data: {str(e)}")
            return {}

    def place_order(self, symbol: str, quantity: int, side: str, order_type: str = "MARKET") -> Dict:
        """
        Simulate order placement in paper trading.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: Order side ("BUY" or "SELL")
            order_type: Order type (default: "MARKET")
            
        Returns:
            Simulated order details
        """
        market_data = self.get_market_data([symbol])
        if not market_data or symbol not in market_data:
            raise ValueError(f"No market data available for {symbol}")

        current_price = Decimal(str(market_data[symbol]['last_price']))
        
        order = {
            'symbol': symbol,
            'quantity': quantity,
            'side': side,
            'type': order_type,
            'price': current_price,
            'status': 'COMPLETE',
            'timestamp': datetime.now(),
            'order_id': len(self.orders) + 1
        }
        
        self.orders.append(order)
        
        # Update positions
        if side == "BUY":
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=current_price,
                    current_price=current_price,
                    delta=Decimal(str(market_data[symbol].get('delta', 0))),
                    option_type=market_data[symbol].get('instrument_type', ''),
                    strike_price=market_data[symbol].get('strike', 0),
                    expiry=market_data[symbol].get('expiry', '')
                )
            else:
                pos = self.positions[symbol]
                avg_price = (pos.entry_price * pos.quantity + current_price * quantity) / (pos.quantity + quantity)
                pos.quantity += quantity
                pos.entry_price = avg_price
                
        elif side == "SELL":
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos.quantity -= quantity
                if pos.quantity <= 0:
                    del self.positions[symbol]
                    
        return order

    def get_market_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current market data for paper trading.
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary of market data for requested symbols
        """
        if not self.market_data:
            # Simulate some basic market data if no historical data is loaded
            return {
                symbol: {
                    'last_price': 100.0,
                    'bid_price': 99.5,
                    'ask_price': 100.5,
                    'volume': 1000,
                    'delta': 0.5,
                    'instrument_type': 'CE',
                    'strike': 100,
                    'expiry': '2024-01-31'
                }
                for symbol in symbols
            }
            
        # Filter market data for requested symbols
        return {
            symbol: data
            for symbol in symbols
            for data in [self.market_data.get(symbol)]
            if data is not None
        }

    def get_positions(self) -> List[Dict]:
        """
        Get current paper trading positions.
        
        Returns:
            List of current positions
        """
        return [
            {
                'symbol': symbol,
                'quantity': position.quantity,
                'entry_price': float(position.entry_price),
                'current_price': float(position.current_price),
                'pnl': float(position.pnl)
            }
            for symbol, position in self.positions.items()
        ]

    def get_orders(self) -> List[Dict]:
        """
        Get paper trading order history.
        
        Returns:
            List of orders
        """
        return self.orders

    def simulate_market_update(self, market_data: Dict[str, Dict]) -> None:
        """
        Simulate market data updates for paper trading.
        
        Args:
            market_data: Updated market data
        """
        self.market_data.update(market_data)
        
        # Update position prices
        for symbol, position in self.positions.items():
            if symbol in market_data:
                data = market_data[symbol]
                position.current_price = Decimal(str(data['last_price']))
                if 'delta' in data:
                    position.delta = Decimal(str(data['delta']))