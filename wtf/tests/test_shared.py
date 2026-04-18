import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
from wtf.shared import get_api_key, check_api_key, CONFIG_PATH, update_config, get_config, remove_config_value
import wtf.shared # Import the module itself to patch its functions
import dotenv

@pytest.fixture(autouse=True)
def disable_dotenv_load(monkeypatch):
    """
    Fixture to prevent dotenv.load_dotenv() from running during tests.
    """
    monkeypatch.setattr(dotenv, 'load_dotenv', lambda: None)
    # Also ensure that get_api_key doesn't accidentally load real env vars
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

# Test for get_api_key
def test_get_api_key_from_env(monkeypatch):
    """
    Tests that get_api_key correctly retrieves the API key from environment variables.
    """
    test_key = "test_env_key_123"
    monkeypatch.setenv("OPENAI_API_KEY", test_key)
    assert get_api_key() == test_key

def test_get_api_key_from_config_file(monkeypatch, tmp_path):
    """
    Tests that get_api_key correctly retrieves the API key from the config file
    when it's not present in environment variables.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False) # Ensure env var is not set

    mock_wtf_config_dir = tmp_path / ".wtf"
    mock_wtf_config_dir.mkdir()
    
    # Mock Path.home() and wtf.shared.CONFIG_PATH
    monkeypatch.setattr(Path, 'home', lambda: tmp_path)
    monkeypatch.setattr(wtf.shared, 'CONFIG_PATH', mock_wtf_config_dir) # Explicitly set CONFIG_PATH in the module

    config_file = mock_wtf_config_dir / "config.json"
    config_file.write_text(json.dumps({"OPENAI_API_KEY": "test_file_key_456"}))
    
    assert get_api_key() == "test_file_key_456"

def test_get_api_key_none_if_not_found(monkeypatch, tmp_path):
    """
    Tests that get_api_key returns None if the API key is not found
    in environment variables or the config file.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    nonexistent_mock_home = tmp_path / "nonexistent_home"
    # Mock Path.home() and wtf.shared.CONFIG_PATH to point to a non-existent directory
    monkeypatch.setattr(Path, 'home', lambda: nonexistent_mock_home)
    monkeypatch.setattr(wtf.shared, 'CONFIG_PATH', nonexistent_mock_home / ".wtf")
    
    assert get_api_key() is None

# Test for check_api_key
def test_check_api_key_true(monkeypatch):
    """
    Tests that check_api_key returns True when an API key is available.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "any_key")
    assert check_api_key() is True

def test_check_api_key_false(monkeypatch, tmp_path):
    """
    Tests that check_api_key returns False when no API key is available.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    # Mock Path.home() to return a non-existent directory for config
    monkeypatch.setattr(Path, 'home', lambda: tmp_path / "nonexistent_home")
    
    assert check_api_key() is False

# Test for update_config
@pytest.fixture
def mock_config_path(tmp_path, monkeypatch):
    """Fixture to mock CONFIG_PATH to a temporary directory."""
    mock_home = tmp_path / "mock_home"
    mock_home.mkdir()
    monkeypatch.setattr(Path, 'home', lambda: mock_home)
    # Ensure CONFIG_PATH in the shared module points to the mocked path
    monkeypatch.setattr(wtf.shared, 'CONFIG_PATH', mock_home / ".wtf")
    yield mock_home / ".wtf"

def test_update_config_new_file(mock_config_path):
    """Test updating config when config.json does not exist."""
    assert not (mock_config_path / "config.json").exists()
    assert update_config({"test_key": "test_value"})
    assert (mock_config_path / "config.json").exists()
    with open(mock_config_path / "config.json", "r") as f:
        config = json.load(f)
    assert config == {"test_key": "test_value"}

def test_update_config_existing_file(mock_config_path):
    """Test updating an existing config.json file."""
    # Create an initial config file
    mock_config_path.mkdir(parents=True, exist_ok=True)
    with open(mock_config_path / "config.json", "w") as f:
        json.dump({"initial_key": "initial_value"}, f)
    
    assert update_config({"new_key": "new_value"})
    with open(mock_config_path / "config.json", "r") as f:
        config = json.load(f)
    assert config == {"initial_key": "initial_value", "new_key": "new_value"}

def test_update_config_delete(mock_config_path):
    """Test deleting the config directory."""
    mock_config_path.mkdir(parents=True, exist_ok=True)
    (mock_config_path / "config.json").write_text("{}")
    
    assert mock_config_path.exists()
    assert update_config(delete=True)
    assert not mock_config_path.exists()

# Test for get_config
def test_get_config_existing(mock_config_path):
    """Test getting config from an existing file."""
    expected_config = {"key1": "value1", "key2": "value2"}
    mock_config_path.mkdir(parents=True, exist_ok=True)
    with open(mock_config_path / "config.json", "w") as f:
        json.dump(expected_config, f)
    
    assert get_config() == expected_config

def test_get_config_not_found(mock_config_path, capsys):
    """Test getting config when file is not found."""
    assert get_config() is None
    captured = capsys.readouterr()
    assert "Config not found" in captured.out

def test_get_config_invalid_json(mock_config_path, capsys):
    """Test getting config when file contains invalid JSON."""
    mock_config_path.mkdir(parents=True, exist_ok=True)
    (mock_config_path / "config.json").write_text("invalid json")
    
    assert get_config() is None
    captured = capsys.readouterr()
    assert "Config not found" in captured.out

# Test for remove_config_value
def test_remove_config_value_success(mock_config_path, capsys):
    """Test removing an existing key-value pair."""
    initial_config = {"key_to_remove": "value1", "key2": "value2"}
    mock_config_path.mkdir(parents=True, exist_ok=True)
    with open(mock_config_path / "config.json", "w") as f:
        json.dump(initial_config, f)
    
    remove_config_value("key_to_remove")
    
    with open(mock_config_path / "config.json", "r") as f:
        updated_config = json.load(f)
    assert updated_config == {"key2": "value2"}
    captured = capsys.readouterr()
    assert "Removed value successfully" in captured.out

def test_remove_config_value_key_not_found(mock_config_path, capsys):
    """Test removing a non-existent key."""
    initial_config = {"key1": "value1"}
    mock_config_path.mkdir(parents=True, exist_ok=True)
    with open(mock_config_path / "config.json", "w") as f:
        json.dump(initial_config, f)
    
    remove_config_value("non_existent_key")
    
    with open(mock_config_path / "config.json", "r") as f:
        updated_config = json.load(f)
    assert updated_config == initial_config # Config should remain unchanged
    captured = capsys.readouterr()
    assert 'Value "non_existent_key" not found.' in captured.out

def test_remove_config_value_empty_config(mock_config_path, capsys):
    """Test removing from an empty config."""
    # Ensure no config file exists initially
    remove_config_value("any_key")
    captured = capsys.readouterr()
    assert "Empty config, no need for changes." in captured.out


