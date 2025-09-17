import json
import os
from typing import Dict, Any
from pathlib import Path

class ConfigManager:
    """Manages configuration settings for the trading strategy."""
    
    DEFAULT_CONFIG_PATH = "config.json"
    REQUIRED_FIELDS = {
        'trading': ['mode', 'capital', 'max_loss_percentage', 'target_profit_percentage'],
        'strategy': ['target_delta', 'position_sizing', 'adjustment_threshold'],
        'zerodha': ['api_key', 'api_secret']
    }

    def __init__(self, config_path: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Dict containing configuration settings
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is not valid JSON
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}. "
                "Please copy config.sample.json to config.json and update with your settings."
            )

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def _validate_config(self) -> None:
        """
        Validate that all required configuration fields are present.
        
        Raises:
            ValueError: If any required field is missing
        """
        for section, fields in self.REQUIRED_FIELDS.items():
            if section not in self.config:
                raise ValueError(f"Missing required config section: {section}")
            
            for field in fields:
                if field not in self.config[section]:
                    raise ValueError(f"Missing required config field: {section}.{field}")

    def get(self, section: str, field: str = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: The configuration section
            field: The specific field in the section (optional)
            
        Returns:
            Configuration value if field specified, else entire section
            
        Raises:
            KeyError: If section or field doesn't exist
        """
        if section not in self.config:
            raise KeyError(f"Configuration section '{section}' not found")
            
        if field is None:
            return self.config[section]
            
        if field not in self.config[section]:
            raise KeyError(f"Configuration field '{field}' not found in section '{section}'")
            
        return self.config[section][field]

    def update(self, section: str, field: str, value: Any) -> None:
        """
        Update a configuration value.
        
        Args:
            section: The configuration section
            field: The field to update
            value: The new value
            
        Raises:
            KeyError: If section doesn't exist
        """
        if section not in self.config:
            raise KeyError(f"Configuration section '{section}' not found")
            
        self.config[section][field] = value

    def save(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    @classmethod
    def create_default_config(cls, path: str = None) -> None:
        """
        Create a default configuration file from sample.
        
        Args:
            path: Path where to create the config file (optional)
        """
        path = path or cls.DEFAULT_CONFIG_PATH
        sample_path = Path(path).parent / "config.sample.json"
        
        if not os.path.exists(sample_path):
            raise FileNotFoundError("Config sample file not found")
            
        if os.path.exists(path):
            raise FileExistsError("Config file already exists")
            
        with open(sample_path, 'r') as f:
            sample_config = json.load(f)
            
        with open(path, 'w') as f:
            json.dump(sample_config, f, indent=4)

    def __str__(self) -> str:
        """String representation of current configuration."""
        return json.dumps(self.config, indent=2)