def generate_suggestion(zone_name, predicted_avg, historical_avg):
    """
    Rule-based suggestion engine comparing predicted consumption to historical averages.
    """
    if historical_avg == 0:
        return "Not enough historical data to generate a suggestion."
        
    diff_percent = ((predicted_avg - historical_avg) / historical_avg) * 100
    
    # Thresholds config
    HIGH_THRESHOLD = 5.0 # 5% increase
    LOW_THRESHOLD = -5.0 # 5% decrease
    
    if diff_percent > HIGH_THRESHOLD:
        return f"Peak load expected in {zone_name}. Consumption is trending higher by {diff_percent:.1f}%. Consider preparing additional capacity."
    elif diff_percent < LOW_THRESHOLD:
        return f"Consumption trending lower in {zone_name} by {abs(diff_percent):.1f}%. Resources could potentially be reallocated."
    else:
        return f"Consumption in {zone_name} is expected to remain stable, deviating by only {abs(diff_percent):.1f}%."
