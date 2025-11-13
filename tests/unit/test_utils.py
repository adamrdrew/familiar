"""Unit tests for utility modules."""
import os
import pytest
from familiar.utils.env import get_env_vars, get_required_env, get_optional_env, get_bool_env
from familiar.utils.interpolation import interpolate_variables, extract_variables


class TestEnvUtils:
    """Tests for environment variable utilities."""
    
    def test_get_env_vars_no_prefix(self, monkeypatch):
        """Test getting all environment variables."""
        monkeypatch.setenv("TEST_VAR", "value")
        env_vars = get_env_vars()
        assert "TEST_VAR" in env_vars
        assert env_vars["TEST_VAR"] == "value"
    
    def test_get_env_vars_with_prefix(self, monkeypatch):
        """Test getting environment variables with prefix."""
        monkeypatch.setenv("APP_URL", "http://localhost")
        monkeypatch.setenv("APP_USER", "testuser")
        monkeypatch.setenv("OTHER_VAR", "other")
        
        env_vars = get_env_vars("APP_")
        assert "URL" in env_vars
        assert "USER" in env_vars
        assert "OTHER_VAR" not in env_vars
        assert env_vars["URL"] == "http://localhost"
    
    def test_get_required_env_exists(self, monkeypatch):
        """Test getting required environment variable that exists."""
        monkeypatch.setenv("REQUIRED_VAR", "value")
        assert get_required_env("REQUIRED_VAR") == "value"
    
    def test_get_required_env_missing(self):
        """Test getting required environment variable that is missing."""
        with pytest.raises(ValueError, match="Required environment variable"):
            get_required_env("MISSING_VAR_12345")
    
    def test_get_optional_env_exists(self, monkeypatch):
        """Test getting optional environment variable that exists."""
        monkeypatch.setenv("OPTIONAL_VAR", "value")
        assert get_optional_env("OPTIONAL_VAR", "default") == "value"
    
    def test_get_optional_env_missing(self):
        """Test getting optional environment variable that is missing."""
        assert get_optional_env("MISSING_VAR_12345", "default") == "default"
    
    def test_get_bool_env_true_values(self, monkeypatch):
        """Test boolean environment variables with true values."""
        for value in ["true", "TRUE", "1", "yes", "YES", "on", "ON"]:
            monkeypatch.setenv("BOOL_VAR", value)
            assert get_bool_env("BOOL_VAR") is True
    
    def test_get_bool_env_false_values(self, monkeypatch):
        """Test boolean environment variables with false values."""
        for value in ["false", "FALSE", "0", "no", "NO", "off", "OFF"]:
            monkeypatch.setenv("BOOL_VAR", value)
            assert get_bool_env("BOOL_VAR") is False
    
    def test_get_bool_env_default(self):
        """Test boolean environment variable with default."""
        assert get_bool_env("MISSING_VAR_12345", True) is True
        assert get_bool_env("MISSING_VAR_12345", False) is False


class TestInterpolation:
    """Tests for variable interpolation utilities."""
    
    def test_interpolate_variables_basic(self):
        """Test basic variable interpolation."""
        text = "Visit ${APP_URL} and login"
        variables = {"APP_URL": "http://localhost:3000"}
        result = interpolate_variables(text, variables)
        assert result == "Visit http://localhost:3000 and login"
    
    def test_interpolate_variables_multiple(self):
        """Test interpolating multiple variables."""
        text = "Visit ${APP_URL} as ${USERNAME} with ${PASSWORD}"
        variables = {
            "APP_URL": "http://localhost",
            "USERNAME": "admin",
            "PASSWORD": "secret",
        }
        result = interpolate_variables(text, variables)
        assert result == "Visit http://localhost as admin with secret"
    
    def test_interpolate_variables_missing(self):
        """Test that missing variables are left unchanged."""
        text = "Visit ${APP_URL} and ${MISSING_VAR}"
        variables = {"APP_URL": "http://localhost"}
        result = interpolate_variables(text, variables)
        assert result == "Visit http://localhost and ${MISSING_VAR}"
    
    def test_interpolate_variables_empty_text(self):
        """Test interpolation with empty text."""
        assert interpolate_variables("", {"VAR": "value"}) == ""
    
    def test_interpolate_variables_no_variables(self):
        """Test interpolation with no variable placeholders."""
        text = "Plain text without variables"
        result = interpolate_variables(text, {"VAR": "value"})
        assert result == text
    
    def test_extract_variables_basic(self):
        """Test extracting variable names."""
        text = "Visit ${APP_URL} and login"
        variables = extract_variables(text)
        assert variables == ["APP_URL"]
    
    def test_extract_variables_multiple(self):
        """Test extracting multiple variable names."""
        text = "Visit ${APP_URL} as ${USERNAME}"
        variables = extract_variables(text)
        assert variables == ["APP_URL", "USERNAME"]
    
    def test_extract_variables_duplicates(self):
        """Test that duplicate variables are deduplicated."""
        text = "Visit ${APP_URL} and navigate from ${APP_URL}"
        variables = extract_variables(text)
        assert variables == ["APP_URL"]
    
    def test_extract_variables_none(self):
        """Test extracting from text with no variables."""
        text = "Plain text without variables"
        variables = extract_variables(text)
        assert variables == []
    
    def test_extract_variables_empty_text(self):
        """Test extracting from empty text."""
        variables = extract_variables("")
        assert variables == []

