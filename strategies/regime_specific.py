from utils.logger import setup_logger

logger = setup_logger("regime_specific_strategy", log_file="strategy_regime_specific.log")

class RegimeSpecificStrategy:
    """
    Maintain a separate model per regime signature.
    Retrain when entering a regime with no model or forced retrain.
    """

    def should_retrain(self, regime_changed, steps_since_last_retrain, retrain_interval):
        # retrain on regime change or interval
        return regime_changed or (steps_since_last_retrain >= retrain_interval)

    def select_model(self, model_pool, current_regime_key, global_model):
        # if no model exists for this regime, return None (engine trains it)
        return model_pool.get(current_regime_key, None)
