#!/usr/bin/env python3
"""
Paper trading example for the delta-neutral options strategy.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from src.utils.config import ConfigManager
from src.utils.monitoring import TradingLogger, PerformanceMonitor
from src.strategy.delta_neutral import DeltaNeutralStrategy
from src.trading.paper_trading import PaperTradingExecutor

def main(config_path: str, data_path: str = None):
    # Initialize logging
    logger = TradingLogger(log_dir="logs", log_level="INFO")
    
    try:
        # Load configuration
        config = ConfigManager(config_path)
        
        # Initialize monitoring
        monitor = PerformanceMonitor(output_dir="results")
        
        # Create strategy instance
        strategy = DeltaNeutralStrategy(config.config)
        
        # Initialize paper trading executor
        executor = PaperTradingExecutor(
            strategy=strategy,
            data_path=data_path
        )
        
        logging.info("Starting paper trading simulation...")
        
        # Start trading execution
        executor.start()
        
    except KeyboardInterrupt:
        logging.info("Stopping paper trading simulation...")
        
        # Generate and save performance report
        report = monitor.generate_report()
        logging.info(f"Performance Report:\n{report}")
        
    except Exception as e:
        logging.error(f"Error in paper trading: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run delta-neutral strategy in paper trading mode")
    parser.add_argument("--config", "-c", default="config.json",
                       help="Path to configuration file")
    parser.add_argument("--data", "-d",
                       help="Path to historical market data (optional)")
    
    args = parser.parse_args()
    main(args.config, args.data)