"""
Example showing how to backtest the delta-neutral strategy using historical data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from pathlib import Path
import argparse

from src.utils.config import ConfigManager
from src.utils.monitoring import TradingLogger, PerformanceMonitor
from src.strategy.delta_neutral import DeltaNeutralStrategy
from src.trading.paper_trading import PaperTradingExecutor

def load_historical_data(data_dir: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Load and prepare historical market data for backtesting.
    
    Args:
        data_dir: Directory containing historical data files
        start_date: Start date for backtesting
        end_date: End date for backtesting
        
    Returns:
        DataFrame containing prepared market data
    """
    data_files = []
    data_path = Path(data_dir)
    
    # Load all CSV files in the directory
    for file in data_path.glob("*.csv"):
        try:
            df = pd.read_csv(file)
            data_files.append(df)
        except Exception as e:
            logging.warning(f"Failed to load {file}: {str(e)}")
    
    if not data_files:
        raise ValueError("No data files found")
        
    # Combine all data
    data = pd.concat(data_files, ignore_index=True)
    
    # Convert date columns
    data['date'] = pd.to_datetime(data['date'])
    
    # Filter by date range
    mask = (data['date'] >= start_date) & (data['date'] <= end_date)
    data = data[mask]
    
    return data

def run_backtest(config_path: str, data_dir: str, start_date: str, end_date: str):
    """
    Run strategy backtest using historical data.
    
    Args:
        config_path: Path to configuration file
        data_dir: Directory containing historical data
        start_date: Start date for backtest (YYYY-MM-DD)
        end_date: End date for backtest (YYYY-MM-DD)
    """
    # Initialize logging
    logger = TradingLogger(log_dir="logs", log_level="INFO")
    
    try:
        # Load configuration
        config = ConfigManager(config_path)
        
        # Initialize monitoring
        monitor = PerformanceMonitor(output_dir="results")
        
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Load historical data
        logging.info("Loading historical data...")
        data = load_historical_data(data_dir, start, end)
        
        # Create strategy instance
        strategy = DeltaNeutralStrategy(config.config)
        
        # Initialize paper trading executor
        executor = PaperTradingExecutor(strategy=strategy)
        
        # Run backtest
        logging.info("Starting backtest...")
        current_date = start
        while current_date <= end:
            # Get data for current date
            daily_data = data[data['date'].dt.date == current_date.date()]
            
            if daily_data.empty:
                current_date += timedelta(days=1)
                continue
            
            # Update market data
            market_data = daily_data.to_dict('records')
            executor.simulate_market_update(market_data)
            
            # Execute strategy
            executor.monitor_and_execute()
            
            # Record metrics
            portfolio_data = {
                'date': current_date,
                'total_pnl': float(strategy.portfolio.get_total_pnl()),
                'portfolio_value': sum(float(pos.current_price * pos.quantity) 
                                    for pos in strategy.portfolio.positions.values()),
                'total_delta': float(strategy.portfolio.total_delta)
            }
            monitor.record_portfolio_update(portfolio_data)
            
            current_date += timedelta(days=1)
        
        # Generate and save performance report
        report = monitor.generate_report()
        logging.info(f"Backtest completed. Performance Report:\n{report}")
        
    except Exception as e:
        logging.error(f"Error in backtest: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backtest delta-neutral strategy")
    parser.add_argument("--config", "-c", default="config.json",
                       help="Path to configuration file")
    parser.add_argument("--data-dir", "-d", required=True,
                       help="Directory containing historical data files")
    parser.add_argument("--start-date", "-s", required=True,
                       help="Start date for backtest (YYYY-MM-DD)")
    parser.add_argument("--end-date", "-e", required=True,
                       help="End date for backtest (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    run_backtest(args.config, args.data_dir, args.start_date, args.end_date)