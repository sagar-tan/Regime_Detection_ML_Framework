from utils.logger import setup_logger

logger = setup_logger("static_strategy", log_file="strategy_static.log")

class StaticStrategy:
    """
    Always use the same model.
    Retrain based on interval only (NOT regime change).
    """

    def should_retrain(self, regime_changed, steps_since_last_retrain, retrain_interval):
        # static = no regime reaction
        return steps_since_last_retrain >= retrain_interval

    def select_model(self, model_pool, current_regime_key, global_model):
        # static = always use global model
        return global_model
