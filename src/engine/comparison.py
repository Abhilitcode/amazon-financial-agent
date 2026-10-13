
from simulation import simulate_scenario
from summary import summarize_simulation


def compare_scenarios(profile, scenario_a, scenario_b, months=24):
    # 1. Simulate both scenarios
    results_a = simulate_scenario(profile, scenario_a, months)
    results_b = simulate_scenario(profile, scenario_b, months)

    # 2. Summarize both simulations
    summary_a = summarize_simulation(results_a, profile.minimum_buffer)
    summary_b = summarize_simulation(results_b, profile.minimum_buffer)

    # 3. Get the final savings from each scenario
    ending_savings_a = results_a[-1].ending_savings
    ending_savings_b = results_b[-1].ending_savings

    # 4. Compare savings month by month
    monthly_comparison = []

    for result_a, result_b in zip(results_a, results_b):
        monthly_comparison.append({
            "month": result_a.month,
            "scenario_a_savings": result_a.ending_savings,
            "scenario_b_savings": result_b.ending_savings,
            "difference": (
                result_b.ending_savings - result_a.ending_savings
            ),
        })

    # 5. Return the comparison
    return {
        "scenario_a": {
            "name": scenario_a.name,
            "ending_savings": ending_savings_a,
            "lowest_savings": summary_a[0],
            "buffer_breached": summary_a[1],
            "first_buffer_breach_month": summary_a[2],
            "savings_goal_missed_months": summary_a[3],
        },
        "scenario_b": {
            "name": scenario_b.name,
            "ending_savings": ending_savings_b,
            "lowest_savings": summary_b[0],
            "buffer_breached": summary_b[1],
            "first_buffer_breach_month": summary_b[2],
            "savings_goal_missed_months": summary_b[3],
        },
        "ending_savings_difference": ending_savings_b - ending_savings_a,
        "monthly_comparison": monthly_comparison,
    }
