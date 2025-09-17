# Delta-Neutral Options Trading Strategy

A production-ready implementation of a delta-neutral options trading strategy with support for paper trading and live trading through Zerodha Kite.

## Features

- Delta-neutral options trading strategy implementation
- Configurable parameters for strategy customization
- Paper trading support for strategy testing
- Live trading capability through Zerodha Kite
- Comprehensive logging and monitoring
- Proper error handling and risk management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/delta-neutral-strategy.git
cd delta-neutral-strategy
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Copy and configure settings:
```bash
cp config.sample.json config.json
# Edit config.json with your settings
```

## Configuration

Create a `config.json` file with your settings:

```json
{
    "trading": {
        "mode": "paper",  // or "live"
        "capital": 100000,
        "max_loss_percentage": 2.0,
        "target_profit_percentage": 1.0
    },
    "strategy": {
        "target_delta": 0.5,
        "position_sizing": 1.0,
        "adjustment_threshold": 0.1
    },
    "zerodha": {
        "api_key": "your_api_key",
        "api_secret": "your_api_secret"
    }
}
```

## Usage

1. Paper Trading:
```bash
python src/run_paper_trading.py
```

2. Live Trading:
```bash
python src/run_live_trading.py
```

## Project Structure

```
delta-neutral-strategy/
├── src/
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── delta_neutral.py
│   │   └── position_manager.py
│   ├── trading/
│   │   ├── __init__.py
│   │   ├── paper_trading.py
│   │   └── live_trading.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logging.py
├── tests/
├── logs/
├── results/
├── setup.py
├── requirements.txt
├── config.sample.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.