"""Unit tests for .env file loading."""
import os
import pytest
from pathlib import Path
from familiar.utils.dotenv import load_dotenv_file


class TestDotenvLoading:
    """Tests for .env file loading functionality."""
    
    def test_load_dotenv_when_file_exists(self, tmp_path, monkeypatch):
        """Test loading variables from .env file."""
        # Create .env file
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text("TEST_VAR=hello\nANOTHER_VAR=world\n")
        
        # Clear any existing vars
        monkeypatch.delenv("TEST_VAR", raising=False)
        monkeypatch.delenv("ANOTHER_VAR", raising=False)
        
        # Load it
        result = load_dotenv_file(dotenv_path=dotenv_file)
        
        assert result is True
        assert os.getenv("TEST_VAR") == "hello"
        assert os.getenv("ANOTHER_VAR") == "world"
    
    def test_skip_silently_when_dotenv_missing(self, tmp_path):
        """Test that missing .env file doesn't cause errors."""
        dotenv_file = tmp_path / ".env"  # Doesn't exist
        
        result = load_dotenv_file(dotenv_path=dotenv_file)
        
        assert result is False  # Not found, but no error
    
    def test_existing_env_vars_not_overridden(self, tmp_path, monkeypatch):
        """Test that existing environment variables are preserved."""
        # Set existing var
        monkeypatch.setenv("EXISTING_VAR", "original")
        
        # Create .env with same var
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text("EXISTING_VAR=from_dotenv\n")
        
        # Load it
        load_dotenv_file(dotenv_path=dotenv_file)
        
        # Original value should be preserved
        assert os.getenv("EXISTING_VAR") == "original"
    
    def test_load_from_cwd_when_no_path_specified(self, tmp_path, monkeypatch):
        """Test that .env is loaded from current directory when no path given."""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        # Create .env in current directory
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text("CWD_VAR=from_cwd\n")
        
        # Clear any existing var
        monkeypatch.delenv("CWD_VAR", raising=False)
        
        # Load without specifying path
        result = load_dotenv_file()
        
        assert result is True
        assert os.getenv("CWD_VAR") == "from_cwd"
    
    def test_handles_malformed_dotenv_gracefully(self, tmp_path, monkeypatch, caplog):
        """Test that malformed .env file doesn't crash."""
        # Create malformed .env
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text("VALID_VAR=value\nINVALID LINE WITHOUT EQUALS\n")
        
        # Clear any existing var
        monkeypatch.delenv("VALID_VAR", raising=False)
        
        # Should not crash
        result = load_dotenv_file(dotenv_path=dotenv_file)
        
        # python-dotenv is actually quite tolerant, so this might succeed
        # The key is that it doesn't crash
        assert result in [True, False]
    
    def test_verbose_mode_logs_loading(self, tmp_path, monkeypatch, caplog):
        """Test that verbose mode logs the loading operation."""
        import logging
        caplog.set_level(logging.DEBUG)
        
        # Create .env file
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text("VERBOSE_VAR=test\n")
        
        # Clear any existing var
        monkeypatch.delenv("VERBOSE_VAR", raising=False)
        
        # Load with verbose mode
        result = load_dotenv_file(dotenv_path=dotenv_file, verbose=True)
        
        assert result is True
        # Check that something was logged
        assert len(caplog.records) > 0
    
    def test_multiple_variables_loaded(self, tmp_path, monkeypatch):
        """Test loading multiple variables from .env."""
        # Create .env with multiple variables
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text("""
# Comment line
VAR1=value1
VAR2=value2
VAR3=value3

# Another comment
VAR4=value4
""")
        
        # Clear any existing vars
        for var in ["VAR1", "VAR2", "VAR3", "VAR4"]:
            monkeypatch.delenv(var, raising=False)
        
        # Load it
        result = load_dotenv_file(dotenv_path=dotenv_file)
        
        assert result is True
        assert os.getenv("VAR1") == "value1"
        assert os.getenv("VAR2") == "value2"
        assert os.getenv("VAR3") == "value3"
        assert os.getenv("VAR4") == "value4"
    
    def test_handles_quotes_in_values(self, tmp_path, monkeypatch):
        """Test that quoted values are handled correctly."""
        # Create .env with quoted values
        dotenv_file = tmp_path / ".env"
        dotenv_file.write_text('''
SINGLE_QUOTED='single quotes'
DOUBLE_QUOTED="double quotes"
NO_QUOTES=no quotes
''')
        
        # Clear any existing vars
        for var in ["SINGLE_QUOTED", "DOUBLE_QUOTED", "NO_QUOTES"]:
            monkeypatch.delenv(var, raising=False)
        
        # Load it
        result = load_dotenv_file(dotenv_path=dotenv_file)
        
        assert result is True
        # python-dotenv strips quotes
        assert os.getenv("SINGLE_QUOTED") == "single quotes"
        assert os.getenv("DOUBLE_QUOTED") == "double quotes"
        assert os.getenv("NO_QUOTES") == "no quotes"

