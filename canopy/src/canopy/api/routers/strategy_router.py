"""
Strategy Router - Endpoints for parsing and validating Canopy strategies.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from canopy.parser.parser import CanopyParser

router = APIRouter()


class ParseStrategyRequest(BaseModel):
    """Request model for parsing a strategy."""

    strategy_code: str
    validate: bool = True


class ParseStrategyResponse(BaseModel):
    """Response model for parsed strategy."""

    success: bool
    strategy_name: str | None = None
    indicators: list[str] = []
    signals: list[str] = []
    plots: list[str] = []
    errors: list[str] = []


@router.post("/parse", response_model=ParseStrategyResponse)
async def parse_strategy(request: ParseStrategyRequest) -> ParseStrategyResponse:
    """
    Parse and validate a Canopy strategy.

    Args:
        request: Strategy code and validation options

    Returns:
        Parsed strategy information or errors
    """
    try:
        parser = CanopyParser()
        strategy = parser.parse(request.strategy_code)

        return ParseStrategyResponse(
            success=True,
            strategy_name=strategy.name,
            indicators=[ind.name for ind in strategy.indicators],
            signals=[sig.type.value for sig in strategy.signals],
            plots=[plot.name for plot in strategy.plots],
            errors=[],
        )
    except Exception as e:
        return ParseStrategyResponse(
            success=False,
            errors=[str(e)],
        )


@router.post("/validate")
async def validate_strategy(request: ParseStrategyRequest) -> Dict[str, Any]:
    """
    Validate a Canopy strategy without full parsing.

    Args:
        request: Strategy code

    Returns:
        Validation result
    """
    try:
        parser = CanopyParser()
        strategy = parser.parse(request.strategy_code)

        return {
            "valid": True,
            "strategy_name": strategy.name,
            "indicators_count": len(strategy.indicators),
            "signals_count": len(strategy.signals),
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }


@router.get("/examples")
async def get_example_strategies() -> Dict[str, Any]:
    """
    Get list of example strategies.

    Returns:
        List of available example strategies
    """
    examples = [
        {
            "name": "MA Crossover",
            "description": "Simple moving average crossover strategy",
            "file": "ma_crossover.canopy",
            "difficulty": "beginner",
        },
        {
            "name": "RSI Mean Reversion",
            "description": "RSI-based mean reversion strategy",
            "file": "rsi_meanreversion.canopy",
            "difficulty": "beginner",
        },
        {
            "name": "Bollinger Bands Squeeze",
            "description": "Bollinger Bands squeeze breakout strategy",
            "file": "bollinger_squeeze.canopy",
            "difficulty": "intermediate",
        },
    ]

    return {
        "examples": examples,
        "count": len(examples),
    }
