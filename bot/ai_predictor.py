import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging

logger = logging.getLogger(__name__)

class AIPredictor:
    def __init__(self):
        # We use a Random Forest because it handles non-linear relationships well
        # and is less prone to overfitting than a single decision tree.
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares the data for ML by creating the target variable.
        """
        if df.empty or len(df) < 2:
            return pd.DataFrame()

        df = df.copy()

        # Target: 1 if the next period's close is higher than current close, else 0
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)

        # Drop the last row because it won't have a target (shift(-1) creates a NaN)
        df = df.dropna()

        return df

    def train(self, df: pd.DataFrame):
        """
        Trains the Random Forest model on historical indicator data.
        """
        df_prep = self.prepare_data(df)
        if df_prep.empty or len(df_prep) < 50:
            logger.warning("Not enough data to train AI model.")
            return

        # Features (X): all columns except our Target
        features = ['Open', 'High', 'Low', 'Close', 'Volume',
                    'SMA_20', 'EMA_50', 'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Diff',
                    'BB_High', 'BB_Low', 'BB_Mid']

        # Ensure all feature columns exist in the dataframe
        available_features = [f for f in features if f in df_prep.columns]

        X = df_prep[available_features]
        y = df_prep['Target']

        # Simple train/test split to evaluate internal performance
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Calculate accuracy for logging
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        logger.info(f"AI Model trained successfully. Test Accuracy: {accuracy:.2f}")

    def predict(self, df: pd.DataFrame) -> str:
        """
        Predicts if the next period will be UP or DOWN.
        Returns 'UP', 'DOWN', or 'UNKNOWN'
        """
        if not self.is_trained:
            logger.warning("Model is not trained. Attempting to train on provided data.")
            self.train(df)
            if not self.is_trained:
                return 'UNKNOWN'

        # Features (X):
        features = ['Open', 'High', 'Low', 'Close', 'Volume',
                    'SMA_20', 'EMA_50', 'RSI_14', 'MACD', 'MACD_Signal', 'MACD_Diff',
                    'BB_High', 'BB_Low', 'BB_Mid']

        available_features = [f for f in features if f in df.columns]

        if not available_features:
             return 'UNKNOWN'

        # Get the latest row of data to make a prediction
        latest_data = df[available_features].iloc[-1:]

        try:
            prediction = self.model.predict(latest_data)
            return 'UP' if prediction[0] == 1 else 'DOWN'
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 'UNKNOWN'
