"""
Strategy Service - Business logic for strategy operations.
"""

from typing import Dict, Any, List
from pathlib import Path
from canopy.parser.parser import parse_strategy
from canopy.domain.strategy import Strategy


class StrategyService:
    """Service for handling strategy-related operations."""

    def __init__(self):
        """Initialize the strategy service."""
        self.examples_dir = Path(__file__).parent.parent.parent.parent.parent / "examples"

    def parse_strategy(self, code: str) -> Dict[str, Any]:
        """
        Parse strategy code and return structured information.

        Args:
            code: Canopy strategy code

        Returns:
            Dictionary with parsed strategy information

        Raises:
            ValueError: If strategy code is invalid
        """
        try:
            strategy = parse_strategy(code)
            return {
                "success": True,
                "strategy_name": strategy.name,
                "strategy": strategy,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "strategy_name": None,
                "strategy": None,
                "error": str(e),
            }

    def validate_strategy(self, code: str) -> Dict[str, Any]:
        """
        Validate strategy syntax.

        Args:
            code: Canopy strategy code

        Returns:
            Dictionary with validation result
        """
        result = self.parse_strategy(code)
        return {
            "valid": result["success"],
            "error": result["error"],
        }

    def get_examples(self) -> List[Dict[str, Any]]:
        """
        Get list of example strategies.

        Returns:
            List of example strategy metadata
        """
        examples = []

        # For now, we have one example
        ma_crossover_file = self.examples_dir / "ma_crossover.canopy"
        if ma_crossover_file.exists():
            examples.append(
                {
                    "name": "ma_crossover",
                    "title": "Moving Average Crossover",
                    "description": "Simple moving average crossover strategy using 50 and 200 period SMAs",
                    "file": "ma_crossover.canopy",
                }
            )

        return examples

    def get_example_code(self, name: str) -> Dict[str, Any]:
        """
        Get example strategy code.

        Args:
            name: Example name

        Returns:
            Dictionary with example code and metadata

        Raises:
            FileNotFoundError: If example doesn't exist
        """
        example_file = self.examples_dir / f"{name}.canopy"

        if not example_file.exists():
            raise FileNotFoundError(f"Example '{name}' not found")

        code = example_file.read_text()

        # Get description from examples list
        examples = self.get_examples()
        description = next(
            (ex["description"] for ex in examples if ex["name"] == name),
            "No description available",
        )

        return {
            "name": name,
            "code": code,
            "description": description,
        }

    def extract_strategy_info(self, strategy: Strategy) -> Dict[str, Any]:
        """
        Extract information from a parsed strategy.

        Args:
            strategy: Parsed strategy instance

        Returns:
            Dictionary with strategy information
        """
        # For MVP, we only support MACrossoverStrategy
        info = {
            "name": strategy.name,
            "type": strategy.__class__.__name__,
        }

        # Add strategy-specific info
        if hasattr(strategy, "fast_period") and hasattr(strategy, "slow_period"):
            info["indicators"] = {
                "fast_ma": f"SMA({strategy.fast_period})",
                "slow_ma": f"SMA({strategy.slow_period})",
            }
            info["buy_rules"] = ["crossover(fast_ma, slow_ma)"]
            info["sell_rules"] = ["crossunder(fast_ma, slow_ma)"]

        return info
