import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

class TradingLogger:
    """Configures and manages logging for the trading system."""

    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize the trading logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Create logs directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create rotating file handler for general logs
        general_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'trading.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        general_handler.setFormatter(formatter)

        # Create rotating file handler for trade logs
        trade_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'trades.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        trade_handler.setFormatter(formatter)

        # Create rotating file handler for errors
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)

        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(general_handler)
        root_logger.addHandler(error_handler)

        # Create trade logger
        trade_logger = logging.getLogger('trades')
        trade_logger.addHandler(trade_handler)
        trade_logger.setLevel(self.log_level)

    @staticmethod
    def log_trade(trade_data: dict) -> None:
        """
        Log trade execution details.
        
        Args:
            trade_data: Dictionary containing trade details
        """
        logger = logging.getLogger('trades')
        logger.info(f"Trade executed: {json.dumps(trade_data)}")

    @staticmethod
    def log_portfolio_update(portfolio_data: dict) -> None:
        """
        Log portfolio update details.
        
        Args:
            portfolio_data: Dictionary containing portfolio details
        """
        logger = logging.getLogger('trades')
        logger.info(f"Portfolio update: {json.dumps(portfolio_data)}")

    @staticmethod
    def log_error(error: Exception, context: Optional[str] = None) -> None:
        """
        Log error details with context.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
        """
        logger = logging.getLogger()
        error_msg = f"{str(error)}"
        if context:
            error_msg = f"{context}: {error_msg}"
        logger.error(error_msg, exc_info=True)

class PerformanceMonitor:
    """Monitors and tracks trading strategy performance."""

    def __init__(self, output_dir: str = "results"):
        """
        Initialize the performance monitor.
        
        Args:
            output_dir: Directory to store performance results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.metrics = {
            'trades': [],
            'pnl': [],
            'portfolio_value': [],
            'delta_exposure': []
        }

    def record_trade(self, trade_data: dict) -> None:
        """
        Record trade execution details.
        
        Args:
            trade_data: Dictionary containing trade details
        """
        self.metrics['trades'].append({
            'timestamp': datetime.now().isoformat(),
            **trade_data
        })
        self._save_metrics()

    def record_portfolio_update(self, portfolio_data: dict) -> None:
        """
        Record portfolio metrics.
        
        Args:
            portfolio_data: Dictionary containing portfolio details
        """
        timestamp = datetime.now().isoformat()
        
        self.metrics['pnl'].append({
            'timestamp': timestamp,
            'value': portfolio_data.get('total_pnl', 0)
        })
        
        self.metrics['portfolio_value'].append({
            'timestamp': timestamp,
            'value': portfolio_data.get('portfolio_value', 0)
        })
        
        self.metrics['delta_exposure'].append({
            'timestamp': timestamp,
            'value': portfolio_data.get('total_delta', 0)
        })
        
        self._save_metrics()

    def _save_metrics(self) -> None:
        """Save performance metrics to file."""
        try:
            output_file = self.output_dir / f"performance_{self.current_session}.json"
            with open(output_file, 'w') as f:
                json.dump(self.metrics, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {str(e)}")

    def generate_report(self) -> dict:
        """
        Generate performance report.
        
        Returns:
            Dictionary containing performance metrics
        """
        total_trades = len(self.metrics['trades'])
        if total_trades == 0:
            return {'error': 'No trades recorded'}

        winning_trades = sum(1 for trade in self.metrics['trades'] 
                           if trade.get('pnl', 0) > 0)
        losing_trades = sum(1 for trade in self.metrics['trades'] 
                          if trade.get('pnl', 0) < 0)

        pnl_values = [p['value'] for p in self.metrics['pnl']]
        max_drawdown = self._calculate_max_drawdown(pnl_values)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / total_trades) * 100 if total_trades > 0 else 0,
            'total_pnl': pnl_values[-1] if pnl_values else 0,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': self._calculate_sharpe_ratio(pnl_values),
            'average_delta_exposure': sum(d['value'] for d in self.metrics['delta_exposure']) / len(self.metrics['delta_exposure'])
            if self.metrics['delta_exposure'] else 0
        }

    @staticmethod
    def _calculate_max_drawdown(values: list) -> float:
        """
        Calculate maximum drawdown from a list of values.
        
        Args:
            values: List of numerical values
            
        Returns:
            Maximum drawdown percentage
        """
        max_drawdown = 0
        peak = values[0]
        
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak != 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
            
        return max_drawdown * 100

    @staticmethod
    def _calculate_sharpe_ratio(pnl_values: list, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio from PnL values.
        
        Args:
            pnl_values: List of PnL values
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        import numpy as np
        
        if len(pnl_values) < 2:
            return 0
            
        returns = np.diff(pnl_values) / pnl_values[:-1]
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        
        if len(excess_returns) == 0:
            return 0
            
        return np.sqrt(252) * np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0