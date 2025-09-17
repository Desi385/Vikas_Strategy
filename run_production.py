#!/usr/bin/env python3
"""
Production runner for the delta-neutral options strategy with proxy and SSL handling.
"""

import os
import sys
import logging
from pathlib import Path
import warnings
import requests
import urllib3
from urllib.request import getproxies

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add project root to path for imports
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.utils.config import ConfigManager
from src.utils.monitoring import TradingLogger, PerformanceMonitor
from src.strategy.delta_neutral import DeltaNeutralStrategy
from src.trading.live_trading import LiveTradingExecutor

def get_system_proxies():
    """Get system proxy settings."""
    return getproxies()

def test_zerodha_connection(api_key):
    """Test connection to Zerodha API."""
    url = "https://api.kite.trade/quote"
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {api_key}"
    }
    
    proxies = get_system_proxies()
    logging.info(f"Using system proxies: {proxies}")
    
    try:
        # First try with SSL verification
        response = requests.get(url, headers=headers, proxies=proxies)
        return True, None
    except requests.exceptions.SSLError:
        try:
            # Try without SSL verification
            response = requests.get(url, headers=headers, proxies=proxies, verify=False)
            return True, "SSL verification disabled"
        except Exception as e:
            return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    # Initialize logging
    logger = TradingLogger(log_dir="logs", log_level="INFO")
    logging.info("Starting production trading system...")
    
    try:
        # Load configuration
        config = ConfigManager("config.json")
        api_key = config.get("zerodha", "api_key")
        
        # Test connection
        logging.info("Testing connection to Zerodha API...")
        success, message = test_zerodha_connection(api_key)
        
        if not success:
            logging.error(f"Failed to connect to Zerodha API: {message}")
            return
            
        if message:
            logging.warning(message)
        
        # Initialize monitoring
        monitor = PerformanceMonitor(output_dir="results")
        
        # Get system proxy settings
        proxies = get_system_proxies()
        
        # Create strategy instance
        strategy = DeltaNeutralStrategy(config.config)
        
        # Initialize live trading executor with proxy and SSL settings
        executor = LiveTradingExecutor(
            strategy=strategy,
            api_key=config.get("zerodha", "api_key"),
            api_secret=config.get("zerodha", "api_secret"),
            proxies=proxies,
            disable_ssl=True  # Only for testing
        )
        
        logging.info("Trading executor initialized successfully")
        logging.info("Starting strategy execution...")
        
        # Start trading execution
        executor.start()
        
    except requests.exceptions.SSLError as e:
        logging.error("SSL Error - Please check corporate proxy settings")
        logging.error(str(e))
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error in trading system: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        try:
            # Generate and save performance report
            report = monitor.generate_report()
            logging.info(f"Performance Report:\n{report}")
            
            # Disconnect from broker
            if 'executor' in locals():
                executor.disconnect()
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    main()