"""
Strategy Router - Endpoints for strategy operations.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from canopy.api.models.requests import StrategyParseRequest, StrategyValidateRequest
from canopy.api.models.responses import (
    StrategyParseResponse,
    StrategyExampleResponse,
    ErrorResponse,
)
from canopy.api.services.strategy_service import StrategyService

router = APIRouter(prefix="/strategies", tags=["strategies"])
strategy_service = StrategyService()


@router.post("/parse", response_model=StrategyParseResponse)
async def parse_strategy(request: StrategyParseRequest):
    """
    Parse Canopy strategy code.

    Parses the strategy code and returns structured information about
    the strategy, including indicators, buy/sell rules, and any errors.

    Example:
        ```
        POST /api/strategies/parse
        {
            "strategy_code": "strategy \"MA Crossover\"\\n\\nfast_ma = sma(close, 50)\\n..."
        }
        ```
    """
    result = strategy_service.parse_strategy(request.strategy_code)

    if result["success"]:
        strategy_info = strategy_service.extract_strategy_info(result["strategy"])
        return StrategyParseResponse(
            success=True,
            strategy_name=strategy_info["name"],
            indicators=strategy_info.get("indicators"),
            buy_rules=strategy_info.get("buy_rules"),
            sell_rules=strategy_info.get("sell_rules"),
            error=None,
        )
    else:
        return StrategyParseResponse(
            success=False,
            strategy_name=None,
            indicators=None,
            buy_rules=None,
            sell_rules=None,
            error=result["error"],
        )


@router.post("/validate")
async def validate_strategy(request: StrategyValidateRequest):
    """
    Validate Canopy strategy syntax.

    Checks if the strategy code is syntactically valid without executing it.

    Example:
        ```
        POST /api/strategies/validate
        {
            "strategy_code": "strategy \"MA Crossover\"\\n\\nfast_ma = sma(close, 50)\\n..."
        }
        ```
    """
    result = strategy_service.validate_strategy(request.strategy_code)
    return {
        "valid": result["valid"],
        "error": result["error"],
        "message": "Strategy is valid" if result["valid"] else "Strategy has errors",
    }


@router.get("/examples", response_model=List[dict])
async def list_examples():
    """
    List available example strategies.

    Returns a list of example strategies that can be used as templates
    or for learning the Canopy language.

    Example:
        ```
        GET /api/strategies/examples
        ```
    """
    examples = strategy_service.get_examples()
    return examples


@router.get("/examples/{name}", response_model=StrategyExampleResponse)
async def get_example(name: str):
    """
    Get example strategy code.

    Retrieves the full code for a specific example strategy.

    Args:
        name: Example strategy name (e.g., "ma_crossover")

    Example:
        ```
        GET /api/strategies/examples/ma_crossover
        ```
    """
    try:
        example = strategy_service.get_example_code(name)
        return StrategyExampleResponse(
            name=example["name"],
            code=example["code"],
            description=example["description"],
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example '{name}' not found",
        )
