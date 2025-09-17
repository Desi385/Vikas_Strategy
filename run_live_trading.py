#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import argparse
import logging

from utils.config import ConfigManager
from utils.monitoring import TradingLogger, PerformanceMonitor
from strategy.delta_neutral import DeltaNeutralStrategy
from trading.live_trading import LiveTradingExecutor

def main():
    """Run the live trading strategy."""
    parser = argparse.ArgumentParser(description="Run delta-neutral strategy in live trading mode")
    parser.add_argument("--config", "-c", default="config.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()

    # Initialize logging
    logger = TradingLogger(log_dir="logs", log_level="INFO")
    
    try:
        # Load configuration
        config = ConfigManager(args.config)
        
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
    main()