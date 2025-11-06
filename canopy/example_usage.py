#!/usr/bin/env python3
"""
Example: Using Data Providers
Demonstrates end-to-end usage of the data provider system
"""

import sys
sys.path.insert(0, '/home/user/canopy-lang/canopy/src')

from pathlib import Path
from canopy.adapters.data.provider_factory import DataProviderFactory
from canopy.application.fetch_data import FetchDataUseCase

def main():
    print("=" * 60)
    print("Canopy Data Providers - Example Usage")
    print("=" * 60)
    
    # Example 1: CSV Provider
    print("\n📁 Example 1: Using CSV Provider")
    print("-" * 60)
    
    fixtures_dir = Path("/home/user/canopy-lang/canopy/tests/fixtures")
    
    # Create CSV provider
    csv_provider = DataProviderFactory.create("csv", data_dir=fixtures_dir)
    print(f"✓ Created CSV provider with data_dir: {fixtures_dir}")
    
    # Create use case
    use_case = FetchDataUseCase(data_provider=csv_provider)
    
    # Validate symbol
    symbol = "SPY"
    if use_case.validate_symbol(symbol):
        print(f"✓ Symbol {symbol} is valid")
        
        # Fetch data
        timeseries = use_case.execute(
            symbol=symbol,
            start_date="2020-01-02",
            end_date="2020-01-31"
        )
        
        print(f"\n📊 Data fetched successfully:")
        print(f"   - Symbol: {symbol}")
        print(f"   - Data points: {len(timeseries)}")
        print(f"   - Date range: {timeseries.index[0].date()} to {timeseries.index[-1].date()}")
        print(f"   - First close: ${timeseries.close.iloc[0]:.2f}")
        print(f"   - Last close: ${timeseries.close.iloc[-1]:.2f}")
        print(f"   - Price change: {((timeseries.close.iloc[-1] / timeseries.close.iloc[0] - 1) * 100):.2f}%")
    
    # Example 2: Factory features
    print("\n\n🏭 Example 2: Factory Features")
    print("-" * 60)
    
    available = DataProviderFactory.get_available_providers()
    print(f"✓ Available providers: {', '.join(available)}")
    
    # Example 3: Provider switching
    print("\n\n🔄 Example 3: Easy Provider Switching")
    print("-" * 60)
    
    def analyze_data(provider_type: str, **kwargs):
        """Analyze data with any provider"""
        provider = DataProviderFactory.create(provider_type, **kwargs)
        use_case = FetchDataUseCase(data_provider=provider)
        
        data = use_case.execute("SPY", "2020-02-01", "2020-02-29")
        
        return {
            "provider": provider_type,
            "points": len(data),
            "avg_close": data.close.mean(),
            "volatility": data.close.std(),
        }
    
    # Analyze with CSV
    result = analyze_data("csv", data_dir=fixtures_dir)
    print(f"\n✓ CSV Analysis:")
    print(f"   - Data points: {result['points']}")
    print(f"   - Average close: ${result['avg_close']:.2f}")
    print(f"   - Volatility: ${result['volatility']:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
