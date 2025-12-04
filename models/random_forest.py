import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from utils.logger import setup_logger
from models.base_model import BaseTradingModel

logger = setup_logger("random_forest", log_file="random_forest.log")

class RandomForestTradingModel(BaseTradingModel):

    def __init__(self, n_estimators=200, max_depth=6, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        logger.info(
            f"Initialized RandomForestTradingModel "
            f"(n_estimators={n_estimators}, max_depth={max_depth})"
        )

    def fit(self, X, y):
        logger.info(f"Fitting RandomForest on {X.shape[0]} samples and {X.shape[1]} features")
        try:
            self.model.fit(X, y)
        except Exception as e:
            logger.error(f"RandomForest fit failed: {e}")
            raise

    def predict(self, X):
        """
        Returns binary signals: 1 for up, 0 for down
        """
        try:
            preds = self.model.predict(X)
            return preds.astype(int)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def get_name(self):
        return "RandomForestTradingModel"
