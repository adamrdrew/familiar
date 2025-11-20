"""Integration tests for agent instructions feature."""

from familiar.core.parser import SuiteParser
from familiar.core.runner import SuiteRunner


class TestAgentInstructionsIntegration:
    """Integration tests for agent instructions end-to-end."""

    def test_parser_reads_scenario_agent_md(self, tmp_path):
        """Test parser reads scenario agent.md and stores in TestSuite."""
        # Create a minimal test suite with agent.md
        suite_dir = tmp_path / "test-suite"
        suite_dir.mkdir()

        # Create suite.yaml
        (suite_dir / "suite.yaml").write_text(
            """name: Test Suite
base_url: http://example.com
"""
        )

        # Create agent.md
        (suite_dir / "agent.md").write_text("This is scenario instructions")

        # Create a step file
        (suite_dir / "00-test.md").write_text("# Test Step\n\nSome content")

        # Parse suite
        parser = SuiteParser()
        suite = parser.parse_suite(suite_dir)

        assert suite.agent_instructions == "This is scenario instructions"
        assert suite.name == "Test Suite"

    def test_parser_handles_missing_agent_md(self, tmp_path):
        """Test parser handles missing agent.md gracefully."""
        suite_dir = tmp_path / "test-suite"
        suite_dir.mkdir()

        (suite_dir / "suite.yaml").write_text(
            """name: Test Suite
base_url: http://example.com
"""
        )
        (suite_dir / "00-test.md").write_text("# Test Step\n\nSome content")

        parser = SuiteParser()
        suite = parser.parse_suite(suite_dir)

        assert suite.agent_instructions is None

    def test_runner_accepts_agent_parameters(self):
        """Test SuiteRunner accepts agent instruction parameters."""
        runner = SuiteRunner(
            headless=True,
            fast_mode=False,
            scenario_agent_override=True,
            global_agent_instructions="Global context",
            base_system_prompt="Base prompt",
        )

        assert runner.scenario_agent_override is True
        assert runner.global_agent_instructions == "Global context"
        assert runner.base_system_prompt == "Base prompt"

    def test_runner_with_fast_mode_and_agent_instructions(self):
        """Test runner combines fast mode with agent instructions."""
        runner = SuiteRunner(
            headless=True,
            fast_mode=True,
            scenario_agent_override=False,
            global_agent_instructions="Global context",
        )

        assert runner.fast_mode is True
        assert runner.global_agent_instructions == "Global context"

    def test_parser_strips_whitespace_from_agent_md(self, tmp_path):
        """Test parser strips leading/trailing whitespace from agent.md."""
        suite_dir = tmp_path / "test-suite"
        suite_dir.mkdir()

        (suite_dir / "suite.yaml").write_text(
            """name: Test Suite
base_url: http://example.com
"""
        )
        (suite_dir / "agent.md").write_text("\n\n  Instructions here  \n\n")
        (suite_dir / "00-test.md").write_text("# Test Step\n\nSome content")

        parser = SuiteParser()
        suite = parser.parse_suite(suite_dir)

        assert suite.agent_instructions == "Instructions here"

    def test_empty_agent_md_returns_none(self, tmp_path):
        """Test empty agent.md file results in None."""
        suite_dir = tmp_path / "test-suite"
        suite_dir.mkdir()

        (suite_dir / "suite.yaml").write_text(
            """name: Test Suite
base_url: http://example.com
"""
        )
        (suite_dir / "agent.md").write_text("")
        (suite_dir / "00-test.md").write_text("# Test Step\n\nSome content")

        parser = SuiteParser()
        suite = parser.parse_suite(suite_dir)

        assert suite.agent_instructions is None


class TestAgentInstructionsContract:
    """Contract tests verifying behavior against spec."""

    def test_prompt_combination_order_contract(self):
        """Verify prompt combination follows Base → Fast → Global → Scenario order."""
        from familiar.core.runner import SPEED_OPTIMIZATION_PROMPT, build_system_message

        result = build_system_message(
            base_system_prompt=None,
            fast_mode=True,
            global_agent_md="GLOBAL",
            scenario_agent_md="SCENARIO",
            override_flag=False,
        )

        # Verify order by checking positions
        assert SPEED_OPTIMIZATION_PROMPT in result
        assert "GLOBAL" in result
        assert "SCENARIO" in result

        # Verify Fast comes before Global
        assert result.index("Speed optimization") < result.index("GLOBAL")
        # Verify Global comes before Scenario
        assert result.index("GLOBAL") < result.index("SCENARIO")

    def test_cli_flag_behavior_contract(self):
        """Verify --scenario-agent-override flag behavior matches spec."""
        from familiar.core.runner import build_system_message

        # Without override: both global and scenario used
        result1 = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md="GLOBAL",
            scenario_agent_md="SCENARIO",
            override_flag=False,
        )
        assert "GLOBAL" in result1
        assert "SCENARIO" in result1

        # With override: only scenario used
        result2 = build_system_message(
            base_system_prompt=None,
            fast_mode=False,
            global_agent_md="GLOBAL",
            scenario_agent_md="SCENARIO",
            override_flag=True,
        )
        assert "GLOBAL" not in result2
        assert "SCENARIO" in result2

    def test_base_prompt_combination_order_contract(self):
        """Verify base prompt comes first in combination order."""
        from familiar.core.runner import build_system_message

        result = build_system_message(
            base_system_prompt="BASE",
            fast_mode=True,
            global_agent_md="GLOBAL",
            scenario_agent_md="SCENARIO",
            override_flag=False,
        )

        # Verify all components present
        assert "BASE" in result
        assert "Speed optimization" in result
        assert "GLOBAL" in result
        assert "SCENARIO" in result

        # Verify order: Base → Fast → Global → Scenario
        assert result.index("BASE") < result.index("Speed optimization")
        assert result.index("Speed optimization") < result.index("GLOBAL")
        assert result.index("GLOBAL") < result.index("SCENARIO")
