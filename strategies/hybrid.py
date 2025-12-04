from utils.logger import setup_logger

logger = setup_logger("hybrid_strategy", log_file="strategy_hybrid.log")

class HybridStrategy:
    """
    Novel hybrid strategy:
    - sliding window training
    - forced retrain whenever regime changes (HMM/CP)
    - interval retrain safety
    - uses one global model (not per-regime)
    """

    def should_retrain(self, regime_changed, steps_since_last_retrain, retrain_interval):
        # hybrid = FIRST priority is regime change
        if regime_changed:
            return True
        return steps_since_last_retrain >= retrain_interval

    def select_model(self, model_pool, current_regime_key, global_model):
        # hybrid = always use global model 
        return global_model
