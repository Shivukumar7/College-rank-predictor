def difficulty_adjust(raw_score: float, expected_max: float, historical_avg_max: float) -> float:
    """
    Adjusts raw score for paper difficulty:
    Adjusted Score = Raw Score * (Average Historical Max / This Year's Expected Max)
    """
    if expected_max <= 0:
        return raw_score
    adjusted = raw_score * (historical_avg_max / expected_max)
    return min(historical_avg_max, max(0.0, adjusted))
