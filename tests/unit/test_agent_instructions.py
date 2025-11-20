"""Unit tests for agent instructions feature."""

import tempfile
from pathlib import Path

from familiar.core.parser import read_agent_instructions, read_system_prompt
from familiar.core.runner import SPEED_OPTIMIZATION_PROMPT, build_system_message


class TestBuildSystemMessage:
    """Tests for system message building function."""

    def test_no_components(self):
        """Test with no components returns None."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md=None,
            scenario_agent_md=None,
            override_flag=False,
        )
        assert result is None

    def test_fast_mode_only(self):
        """Test with only fast mode."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=True,
            global_agent_md=None,
            scenario_agent_md=None,
            override_flag=False,
        )
        assert result == SPEED_OPTIMIZATION_PROMPT

    def test_global_only(self):
        """Test with only global agent.md."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md="Global context",
            scenario_agent_md=None,
            override_flag=False,
        )
        assert result == "Global context"

    def test_scenario_only(self):
        """Test with only scenario agent.md."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md=None,
            scenario_agent_md="Scenario context",
            override_flag=False,
        )
        assert result == "Scenario context"

    def test_fast_mode_plus_global(self):
        """Test fast mode + global combination."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=True,
            global_agent_md="Global context",
            scenario_agent_md=None,
            override_flag=False,
        )
        expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nGlobal context"
        assert result == expected

    def test_fast_mode_plus_scenario(self):
        """Test fast mode + scenario combination."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=True,
            global_agent_md=None,
            scenario_agent_md="Scenario context",
            override_flag=False,
        )
        expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nScenario context"
        assert result == expected

    def test_global_plus_scenario_no_override(self):
        """Test global + scenario without override."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md="Global context",
            scenario_agent_md="Scenario context",
            override_flag=False,
        )
        assert result == "Global context\n\nScenario context"

    def test_global_plus_scenario_with_override(self):
        """Test override ignores global."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md="Global context",
            scenario_agent_md="Scenario context",
            override_flag=True,
        )
        assert result == "Scenario context"
        assert "Global" not in result

    def test_all_components_no_override(self):
        """Test fast mode + global + scenario."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=True,
            global_agent_md="Global context",
            scenario_agent_md="Scenario context",
            override_flag=False,
        )
        expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nGlobal context\n\nScenario context"
        assert result == expected
        assert SPEED_OPTIMIZATION_PROMPT in result
        assert "Global context" in result
        assert "Scenario context" in result

    def test_all_components_with_override(self):
        """Test fast mode + scenario (override ignores global)."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=True,
            global_agent_md="Global context",
            scenario_agent_md="Scenario context",
            override_flag=True,
        )
        expected = f"{SPEED_OPTIMIZATION_PROMPT}\n\nScenario context"
        assert result == expected
        assert "Global" not in result

    def test_override_with_no_scenario(self):
        """Test override flag with no scenario still uses global."""
        result = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md="Global context",
            scenario_agent_md=None,
            override_flag=True,
        )
        # Override has no effect when no scenario present - fallback to global
        assert result == "Global context"

    def test_base_system_prompt_only(self):
        """Test with only base system prompt."""
        result = build_system_message(
            base_system_prompt="Base prompt",
            fast_mode=False,
            global_agent_md=None,
            scenario_agent_md=None,
            override_flag=False,
        )
        assert result == "Base prompt"

    def test_base_plus_fast_mode(self):
        """Test base system prompt + fast mode combination."""
        result = build_system_message(
            base_system_prompt="Base prompt",
            fast_mode=True,
            global_agent_md=None,
            scenario_agent_md=None,
            override_flag=False,
        )
        expected = f"Base prompt\n\n{SPEED_OPTIMIZATION_PROMPT}"
        assert result == expected

    def test_base_plus_all_components(self):
        """Test base prompt + fast mode + global + scenario."""
        result = build_system_message(
            base_system_prompt="Base prompt",
            fast_mode=True,
            global_agent_md="Global context",
            scenario_agent_md="Scenario context",
            override_flag=False,
        )
        expected = f"Base prompt\n\n{SPEED_OPTIMIZATION_PROMPT}\n\nGlobal context\n\nScenario context"
        assert result == expected
        # Verify order
        assert result.index("Base prompt") < result.index("Speed optimization")
        assert result.index("Speed optimization") < result.index("Global context")
        assert result.index("Global context") < result.index("Scenario context")


class TestReadAgentInstructions:
    """Tests for file reading function."""

    def test_file_not_found(self):
        """Test with non-existent file returns None."""
        path = Path("/nonexistent/directory/agent.md")
        result = read_agent_instructions(path)
        assert result is None

    def test_file_exists_and_valid(self):
        """Test reading valid file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("Test instructions")
            temp_path = Path(f.name)

        try:
            result = read_agent_instructions(temp_path)
            assert result == "Test instructions"
        finally:
            temp_path.unlink()

    def test_empty_file(self):
        """Test empty file returns None."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            # Write nothing
            temp_path = Path(f.name)

        try:
            result = read_agent_instructions(temp_path)
            assert result is None
        finally:
            temp_path.unlink()

    def test_whitespace_only_file(self):
        """Test whitespace-only file returns None."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("   \n\n  \t  ")
            temp_path = Path(f.name)

        try:
            result = read_agent_instructions(temp_path)
            assert result is None
        finally:
            temp_path.unlink()


class TestReadSystemPrompt:
    """Tests for system prompt reading function."""

    def test_file_not_found(self):
        """Test with non-existent file returns None."""
        path = Path("/nonexistent/directory/system_prompt.md")
        result = read_system_prompt(path)
        assert result is None

    def test_file_exists_and_valid(self):
        """Test reading valid system prompt file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("Base system prompt instructions")
            temp_path = Path(f.name)

        try:
            result = read_system_prompt(temp_path)
            assert result == "Base system prompt instructions"
        finally:
            temp_path.unlink()

    def test_empty_file(self):
        """Test empty system prompt file returns None."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            # Write nothing
            temp_path = Path(f.name)

        try:
            result = read_system_prompt(temp_path)
            assert result is None
        finally:
            temp_path.unlink()
