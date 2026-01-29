"""
Configuration loader for BMAD Forge.

Loads configuration from config.yaml file with fallback to environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


# Default configuration values
DEFAULT_CONFIG = {
    'application': {
        'version': '1.2.0',
        'name': 'BMAD Forge',
    },
    'templates': {
        'local_path': 'forge/templates/agents',
        'github': {
            'repository': 'DXCSithlordPadawan/BMAD_Forge',
            'branch': 'main',
            'remote_path': 'webapp/forge/templates',
        },
        'sync': {
            'overwrite_existing': True,
            'match_by': 'title',
        },
    },
}


class ConfigLoader:
    """
    Configuration loader that reads from config.yaml with fallback to defaults.
    """
    
    _config: Optional[Dict[str, Any]] = None
    _config_path: Optional[Path] = None
    
    @classmethod
    def get_config_path(cls) -> Path:
        """Get the path to the config file."""
        if cls._config_path:
            return cls._config_path
        
        # Check environment variable for custom config path
        env_path = os.environ.get('BMAD_CONFIG_PATH')
        if env_path:
            return Path(env_path)
        
        # Default to config.yaml in the webapp directory
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / 'config.yaml'
    
    @classmethod
    def set_config_path(cls, path: Path) -> None:
        """Set a custom config file path (useful for testing)."""
        cls._config_path = path
        cls._config = None  # Reset loaded config
    
    @classmethod
    def load_config(cls, reload: bool = False) -> Dict[str, Any]:
        """
        Load configuration from config.yaml file.
        
        Args:
            reload: Force reload the configuration from disk
            
        Returns:
            Configuration dictionary
        """
        if cls._config is not None and not reload:
            return cls._config
        
        config_path = cls.get_config_path()
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f) or {}
        else:
            file_config = {}
        
        # Merge with defaults (file config takes precedence)
        cls._config = cls._merge_config(DEFAULT_CONFIG, file_config)
        
        # Override with environment variables if set
        cls._apply_env_overrides(cls._config)
        
        return cls._config
    
    @classmethod
    def _merge_config(cls, default: Dict, override: Dict) -> Dict:
        """Deep merge configuration dictionaries."""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @classmethod
    def _apply_env_overrides(cls, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides to config."""
        # APP_VERSION overrides application.version
        if os.environ.get('APP_VERSION'):
            config['application']['version'] = os.environ['APP_VERSION']
        
        # APP_NAME overrides application.name
        if os.environ.get('APP_NAME'):
            config['application']['name'] = os.environ['APP_NAME']
        
        # TEMPLATE_REPO overrides templates.github.repository
        if os.environ.get('TEMPLATE_REPO'):
            config['templates']['github']['repository'] = os.environ['TEMPLATE_REPO']
    
    @classmethod
    def get(cls, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path to config key (e.g., 'application.version')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        config = cls.load_config()
        keys = key_path.split('.')
        
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @classmethod
    def reset(cls) -> None:
        """Reset the loaded configuration (useful for testing)."""
        cls._config = None
        cls._config_path = None


# Convenience functions for common config values
def get_app_version() -> str:
    """Get the application version."""
    return ConfigLoader.get('application.version', '1.0.0')


def get_app_name() -> str:
    """Get the application name."""
    return ConfigLoader.get('application.name', 'BMAD Forge')


def get_template_local_path() -> str:
    """Get the local templates path."""
    return ConfigLoader.get('templates.local_path', 'forge/templates/agents')


def get_template_github_repo() -> str:
    """Get the GitHub repository for templates."""
    return ConfigLoader.get('templates.github.repository', 'DXCSithlordPadawan/BMAD_Forge')


def get_template_github_branch() -> str:
    """Get the GitHub branch for templates."""
    return ConfigLoader.get('templates.github.branch', 'main')


def get_template_github_path() -> str:
    """Get the remote path for templates in GitHub."""
    return ConfigLoader.get('templates.github.remote_path', 'webapp/forge/templates')


def get_sync_overwrite_existing() -> bool:
    """Get whether to overwrite existing templates during sync."""
    return ConfigLoader.get('templates.sync.overwrite_existing', True)


def get_sync_match_by() -> str:
    """Get the field to match templates by during sync."""
    return ConfigLoader.get('templates.sync.match_by', 'title')
