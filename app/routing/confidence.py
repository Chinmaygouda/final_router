"""
Confidence scoring module.
Calculates confidence based on score difference between top candidates.
"""


def compute_confidence(models):
    """
    Compute confidence based on gap between top 2 models.
    
    If gap is large → high confidence (select best model)
    If gap is small → low confidence (defer to exploration/bandit)
    """
    if len(models) < 2:
        return 1.0  # Only 1 model? Full confidence

    # Gap between top 2 models
    diff = models[0]["score"] - models[1]["score"]

    # Scale: diff/2 gives range [0, 1] for reasonable gaps
    # If diff = 2.0, confidence = 1.0 (high)
    # If diff = 0.2, confidence = 0.1 (low)
    return min(diff / 2, 1.0)
