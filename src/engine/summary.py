def summarize_simulation(results, minimum_buffer):

    lowest_savings = min(
        result.ending_savings
        for result in results
    )

    buffer_breached = any(
        not result.buffer_safe
        for result in results
    )

    first_buffer_breach_month = None

    for result in results:
        if result.ending_savings < minimum_buffer:
            first_buffer_breach_month = result.month
            break

    savings_goal_missed_months = 0

    for result in results:
        if not result.savings_goal_met:
            savings_goal_missed_months += 1

    return (
        lowest_savings,
        buffer_breached,
        first_buffer_breach_month,
        savings_goal_missed_months,
    )