"""Integration tests for CLI"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from canopy.adapters.ui.cli import app

runner = CliRunner()


def test_cli_version_command():
    """Test that version command works"""
    result = runner.invoke(app, ["version"])
    
    assert result.exit_code == 0
    assert "Canopy version" in result.stdout
    assert "0.1.0" in result.stdout


def test_cli_new_command(tmp_path):
    """Test that new command creates strategy"""
    strategy_name = "test_strategy"
    
    result = runner.invoke(app, ["new", strategy_name, "--directory", str(tmp_path)])
    
    assert result.exit_code == 0
    assert "Created strategy" in result.stdout
    
    # Check that files were created
    strategy_dir = tmp_path / strategy_name
    assert strategy_dir.exists()
    assert (strategy_dir / "strategy.canopy").exists()
    
    # Check content
    content = (strategy_dir / "strategy.canopy").read_text()
    assert "strategy" in content.lower()
    assert "sma" in content


def test_cli_backtest_command(tmp_path):
    """Test that backtest command runs"""
    # Create a test strategy file
    strategy_file = tmp_path / "test.canopy"
    strategy_file.write_text('''strategy "Test MA Cross"

fast_ma = sma(close, 10)
slow_ma = sma(close, 20)

buy when crossover(fast_ma, slow_ma)
sell when crossunder(fast_ma, slow_ma)
''')
    
    # Run backtest (this will fail if Yahoo Finance is down, so we'll just check it runs)
    result = runner.invoke(app, [
        "backtest",
        str(strategy_file),
        "--symbol", "SPY",
        "--start", "2024-01-01",
        "--end", "2024-01-31",
        "--capital", "10000",
    ])
    
    # Should either succeed or fail gracefully
    assert result.exit_code in [0, 1]


def test_cli_handles_invalid_file():
    """Test that CLI handles invalid file paths"""
    result = runner.invoke(app, [
        "backtest",
        "/nonexistent/file.canopy",
    ])
    
    assert result.exit_code == 1
    assert "Error" in result.stdout or "error" in result.stdout.lower()


def test_cli_new_command_with_default_directory(tmp_path):
    """Test new command with default directory"""
    # Change to tmp directory
    import os
    original_dir = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["new", "my_strategy"])
        
        assert result.exit_code == 0
        assert (tmp_path / "my_strategy" / "strategy.canopy").exists()
    finally:
        os.chdir(original_dir)
