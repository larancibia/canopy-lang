"""
Machine Learning Strategy Example

This example demonstrates how to use machine learning with Canopy
to predict price movements and generate trading signals.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score


def create_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create technical indicator features for ML model.

    Args:
        data: DataFrame with OHLCV data

    Returns:
        DataFrame with features
    """
    df = data.copy()

    # Price features
    df["returns"] = df["close"].pct_change()
    df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

    # Moving averages
    for period in [5, 10, 20, 50]:
        df[f"sma_{period}"] = df["close"].rolling(window=period).mean()
        df[f"ema_{period}"] = df["close"].ewm(span=period).mean()

    # Price relative to moving averages
    df["price_to_sma20"] = df["close"] / df["sma_20"]
    df["price_to_sma50"] = df["close"] / df["sma_50"]

    # Momentum indicators
    df["rsi_14"] = calculate_rsi(df["close"], 14)
    df["roc_10"] = df["close"].pct_change(10)
    df["roc_20"] = df["close"].pct_change(20)

    # Volatility features
    df["volatility_20"] = df["returns"].rolling(window=20).std()
    df["atr_14"] = calculate_atr(df, 14)

    # Volume features
    df["volume_sma_20"] = df["volume"].rolling(window=20).mean()
    df["volume_ratio"] = df["volume"] / df["volume_sma_20"]

    # MACD
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(df["close"])

    # Bollinger Bands
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = calculate_bollinger_bands(
        df["close"]
    )
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

    # Trend features
    df["higher_high"] = (df["high"] > df["high"].shift(1)).astype(int)
    df["lower_low"] = (df["low"] < df["low"].shift(1)).astype(int)

    return df


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI indicator."""
    delta = prices.diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()

    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Average True Range."""
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift(1))
    low_close = abs(df["low"] - df["close"].shift(1))

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()

    return atr


def calculate_macd(
    prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD indicator."""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    prices: pd.Series, period: int = 20, std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands."""
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return upper, middle, lower


def create_labels(df: pd.DataFrame, forward_periods: int = 5) -> pd.Series:
    """
    Create labels for ML model.

    Label: 1 if price increases by >1% in next N periods, 0 otherwise.

    Args:
        df: DataFrame with price data
        forward_periods: Number of periods to look forward

    Returns:
        Series of labels (1 or 0)
    """
    future_returns = df["close"].pct_change(forward_periods).shift(-forward_periods)
    labels = (future_returns > 0.01).astype(int)  # 1% threshold

    return labels


def train_ml_model(
    X: pd.DataFrame, y: pd.Series, model_type: str = "random_forest"
) -> Tuple[object, StandardScaler]:
    """
    Train ML model for trading signals.

    Args:
        X: Feature DataFrame
        y: Target labels
        model_type: Type of model ('random_forest' or 'gradient_boosting')

    Returns:
        Trained model and scaler
    """
    # Remove rows with NaN values
    mask = ~(X.isna().any(axis=1) | y.isna())
    X_clean = X[mask]
    y_clean = y[mask]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_clean, y_clean, test_size=0.2, shuffle=False
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Create model
    if model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_split=20, random_state=42
        )
    else:
        model = GradientBoostingClassifier(
            n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42
        )

    # Train model
    print(f"\nTraining {model_type} model...")
    model.fit(X_train_scaled, y_train)

    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)

    print(f"Training Accuracy: {train_score:.4f}")
    print(f"Testing Accuracy: {test_score:.4f}")

    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    print(f"Cross-validation Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Feature importance
    if hasattr(model, "feature_importances_"):
        feature_importance = pd.DataFrame(
            {"feature": X_train.columns, "importance": model.feature_importances_}
        ).sort_values("importance", ascending=False)

        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))

    # Predictions on test set
    y_pred = model.predict(X_test_scaled)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    return model, scaler


def generate_ml_signals(
    model: object, scaler: StandardScaler, features: pd.DataFrame
) -> List[str]:
    """
    Generate trading signals using ML model.

    Args:
        model: Trained ML model
        scaler: Fitted scaler
        features: Feature DataFrame

    Returns:
        List of signals ('BUY', 'SELL', 'HOLD')
    """
    # Remove NaN rows
    clean_features = features.dropna()

    # Scale features
    features_scaled = scaler.transform(clean_features)

    # Predict
    predictions = model.predict(features_scaled)
    probabilities = model.predict_proba(features_scaled)

    # Generate signals based on predictions and confidence
    signals = []
    for pred, proba in zip(predictions, probabilities):
        confidence = max(proba)

        if pred == 1 and confidence > 0.6:  # Buy with high confidence
            signals.append("BUY")
        elif pred == 0 and confidence > 0.6:  # Sell/avoid with high confidence
            signals.append("SELL")
        else:
            signals.append("HOLD")

    return signals


def example_ml_strategy():
    """
    Complete example of ML-based trading strategy.
    """
    from canopy.adapters.data.yahoo_provider import YahooProvider

    print("=== Machine Learning Trading Strategy ===\n")

    # 1. Fetch data
    print("Fetching data...")
    provider = YahooProvider()
    data = provider.fetch_data("AAPL", "2020-01-01", "2023-12-31")

    # Convert to DataFrame
    df = pd.DataFrame(
        {
            "open": [bar.open for bar in data.bars],
            "high": [bar.high for bar in data.bars],
            "low": [bar.low for bar in data.bars],
            "close": [bar.close for bar in data.bars],
            "volume": [bar.volume for bar in data.bars],
        }
    )

    print(f"Data points: {len(df)}")

    # 2. Create features
    print("\nCreating features...")
    df_features = create_features(df)

    # 3. Create labels
    print("Creating labels...")
    labels = create_labels(df_features, forward_periods=5)

    # 4. Select features for model
    feature_columns = [
        col
        for col in df_features.columns
        if col
        not in ["open", "high", "low", "close", "volume", "returns", "log_returns"]
    ]

    X = df_features[feature_columns]
    y = labels

    # 5. Train model
    model, scaler = train_ml_model(X, y, model_type="random_forest")

    # 6. Generate signals
    print("\nGenerating trading signals...")
    signals = generate_ml_signals(model, scaler, X)

    print(f"\nSignal distribution:")
    print(f"  BUY: {signals.count('BUY')}")
    print(f"  SELL: {signals.count('SELL')}")
    print(f"  HOLD: {signals.count('HOLD')}")

    return model, scaler, signals


if __name__ == "__main__":
    # Run example
    model, scaler, signals = example_ml_strategy()
    print("\nML strategy example completed successfully!")
