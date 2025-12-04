import numpy as np
from utils.logger import setup_logger

logger = setup_logger("base_model", log_file="base_model.log")

class BaseTradingModel:
    """
    Minimal interface that ANY ML model in this framework must follow.
    This keeps strategies independent of the underlying ML class.
    """

    def fit(self, X, y):
        raise NotImplementedError("fit() must be implemented.")

    def predict(self, X):
        """
        Must output 1 (up) or 0 (down)
        """
        raise NotImplementedError("predict() must be implemented.")

    def get_name(self):
        """
        Returns model name for logging and saving results.
        """
        return self.__class__.__name__

