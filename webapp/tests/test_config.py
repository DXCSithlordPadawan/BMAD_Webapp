"""
Tests for BMAD Forge configuration loader.
"""

import os
import pytest
import tempfile
from pathlib import Path
import yaml

from bmad_forge.config import (
    ConfigLoader,
    get_app_version,
    get_app_name,
    get_template_local_path,
    get_template_github_repo,
    get_template_github_branch,
    get_template_github_path,
    get_sync_overwrite_existing,
    get_sync_match_by,
    DEFAULT_CONFIG,
)


class TestConfigLoader:
    """Tests for the ConfigLoader class."""
    
    def setup_method(self):
        """Reset config before each test."""
        ConfigLoader.reset()
    
    def teardown_method(self):
        """Clean up after each test."""
        ConfigLoader.reset()
        # Clear any environment variables we may have set
        for key in ['APP_VERSION', 'APP_NAME', 'TEMPLATE_REPO']:
            if key in os.environ:
                del os.environ[key]
    
    def test_load_config_returns_default_when_no_file(self):
        """Test that default config is returned when no config file exists."""
        # Point to a non-existent file
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
        
        config = ConfigLoader.load_config()
        
        assert config['application']['version'] == '1.2.0'
        assert config['application']['name'] == 'BMAD Forge'
    
    def test_load_config_from_yaml_file(self):
        """Test loading configuration from a YAML file."""
        config_content = {
            'application': {
                'version': '2.0.0',
                'name': 'Test App'
            },
            'templates': {
                'local_path': 'test/templates'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            temp_path = Path(f.name)
        
        try:
            ConfigLoader.set_config_path(temp_path)
            config = ConfigLoader.load_config()
            
            assert config['application']['version'] == '2.0.0'
            assert config['application']['name'] == 'Test App'
            assert config['templates']['local_path'] == 'test/templates'
            # Should still have default values for unspecified keys
            assert 'github' in config['templates']
        finally:
            temp_path.unlink()
    
    def test_env_variables_override_config(self):
        """Test that environment variables override config file values."""
        config_content = {
            'application': {
                'version': '2.0.0',
                'name': 'Config App'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            temp_path = Path(f.name)
        
        try:
            # Set environment variables
            os.environ['APP_VERSION'] = '3.0.0'
            os.environ['APP_NAME'] = 'Env App'
            
            ConfigLoader.set_config_path(temp_path)
            config = ConfigLoader.load_config()
            
            # Environment variables should override
            assert config['application']['version'] == '3.0.0'
            assert config['application']['name'] == 'Env App'
        finally:
            temp_path.unlink()
            del os.environ['APP_VERSION']
            del os.environ['APP_NAME']
    
    def test_get_method_returns_nested_values(self):
        """Test the get method with dot-separated paths."""
        ConfigLoader.reset()
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
        
        assert ConfigLoader.get('application.version') == '1.2.0'
        assert ConfigLoader.get('templates.github.branch') == 'main'
        assert ConfigLoader.get('nonexistent.key', 'default') == 'default'
    
    def test_config_caching(self):
        """Test that config is cached after first load."""
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
        
        config1 = ConfigLoader.load_config()
        config2 = ConfigLoader.load_config()
        
        assert config1 is config2  # Same object due to caching
    
    def test_reload_forces_fresh_load(self):
        """Test that reload=True forces a fresh config load."""
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
        
        config1 = ConfigLoader.load_config()
        config2 = ConfigLoader.load_config(reload=True)
        
        # Contents should be equal but different objects
        assert config1 == config2
        assert config1 is not config2


class TestConfigConvenienceFunctions:
    """Tests for convenience functions."""
    
    def setup_method(self):
        """Reset config before each test."""
        ConfigLoader.reset()
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
    
    def teardown_method(self):
        """Clean up after each test."""
        ConfigLoader.reset()
    
    def test_get_app_version(self):
        """Test getting app version."""
        assert get_app_version() == '1.2.0'
    
    def test_get_app_name(self):
        """Test getting app name."""
        assert get_app_name() == 'BMAD Forge'
    
    def test_get_template_local_path(self):
        """Test getting local template path."""
        assert get_template_local_path() == 'forge/templates/agents'
    
    def test_get_template_github_repo(self):
        """Test getting GitHub repo."""
        assert get_template_github_repo() == 'DXCSithlordPadawan/BMAD_Forge'
    
    def test_get_template_github_branch(self):
        """Test getting GitHub branch."""
        assert get_template_github_branch() == 'main'
    
    def test_get_template_github_path(self):
        """Test getting GitHub path."""
        assert get_template_github_path() == 'webapp/forge/templates'
    
    def test_get_sync_overwrite_existing(self):
        """Test getting sync overwrite setting."""
        assert get_sync_overwrite_existing() is True
    
    def test_get_sync_match_by(self):
        """Test getting sync match_by setting."""
        assert get_sync_match_by() == 'title'


class TestTemplateSyncOverwrite:
    """Tests for template sync overwrite behavior."""
    
    def setup_method(self):
        """Reset config before each test."""
        ConfigLoader.reset()
    
    def teardown_method(self):
        """Clean up after each test."""
        ConfigLoader.reset()
    
    def test_overwrite_config_defaults_to_true(self):
        """Test that overwrite is enabled by default."""
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
        
        assert get_sync_overwrite_existing() is True
    
    def test_match_by_defaults_to_title(self):
        """Test that match_by defaults to title."""
        ConfigLoader.set_config_path(Path('/nonexistent/config.yaml'))
        
        assert get_sync_match_by() == 'title'
    
    def test_custom_overwrite_setting(self):
        """Test custom overwrite setting from config."""
        config_content = {
            'templates': {
                'sync': {
                    'overwrite_existing': False,
                    'match_by': 'remote_path'
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            temp_path = Path(f.name)
        
        try:
            ConfigLoader.set_config_path(temp_path)
            
            assert get_sync_overwrite_existing() is False
            assert get_sync_match_by() == 'remote_path'
        finally:
            temp_path.unlink()
