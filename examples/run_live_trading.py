#!/usr/bin/env python3
"""
Live trading example for the delta-neutral options strategy.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from src.utils.config import ConfigManager
from src.utils.monitoring import TradingLogger, PerformanceMonitor
from src.strategy.delta_neutral import DeltaNeutralStrategy
from src.trading.live_trading import LiveTradingExecutor

def main(config_path: str):
    # Initialize logging
    logger = TradingLogger(log_dir="logs", log_level="INFO")
    
    try:
        # Load configuration
        config = ConfigManager(config_path)
        
        # Initialize monitoring
        monitor = PerformanceMonitor(output_dir="results")
        
        # Create strategy instance
        strategy = DeltaNeutralStrategy(config.config)
        
        # Initialize live trading executor
        executor = LiveTradingExecutor(
            strategy=strategy,
            api_key=config.get("zerodha", "api_key"),
            api_secret=config.get("zerodha", "api_secret")
        )
        
        logging.info("Starting live trading...")
        
        # Start trading execution
        executor.start()
        
    except KeyboardInterrupt:
        logging.info("Stopping live trading...")
        
        # Generate and save performance report
        report = monitor.generate_report()
        logging.info(f"Performance Report:\n{report}")
        
        # Disconnect from broker
        executor.disconnect()
        
    except Exception as e:
        logging.error(f"Error in live trading: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run delta-neutral strategy in live trading mode")
    parser.add_argument("--config", "-c", default="config.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()
    main(args.config)