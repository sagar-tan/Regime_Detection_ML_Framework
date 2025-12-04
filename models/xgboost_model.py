import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from utils.logger import setup_logger
from models.base_model import BaseTradingModel

logger = setup_logger("xgboost_model", log_file="xgboost_model.log")


class XGBoostTradingModel(BaseTradingModel):
    def __init__(self, n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42):
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=random_state,
        )
        logger.info(
            f"Initialized XGBoostTradingModel "
            f"(n_estimators={n_estimators}, max_depth={max_depth}, lr={learning_rate})"
        )

    def fit(self, X, y):
        """
        X: numpy array or pandas DataFrame of features
        y: 1D array-like binary labels (0/1)
        """
        logger.info(f"Fitting XGBoost on {X.shape[0]} samples and {X.shape[1]} features")
        try:
            self.model.fit(X, y)
            logger.info("XGBoost fit complete")
        except Exception as e:
            logger.error(f"XGBoost fit failed: {e}")
            raise

    def predict(self, X):
        """
        Returns binary signals: 1 for up, 0 for down
        """
        try:
            preds = self.model.predict(X)
            return preds.astype(int)
        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}")
            raise

    def get_name(self):
        return "XGBoostTradingModel"
