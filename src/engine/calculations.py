def calculate_total_income(profile):
    return profile.monthly_salary + profile.other_income


def calculate_total_fixed_expenses(profile):
    return sum(profile.fixed_expenses.values())


def calculate_total_essential_expenses(profile):
    return sum(profile.essential_expenses.values())


def calculate_total_flexible_expenses(profile):
    return sum(profile.flexible_expenses.values())


def calculate_total_expenses(profile):
    return (
        calculate_total_fixed_expenses(profile)
        + calculate_total_essential_expenses(profile)
        + calculate_total_flexible_expenses(profile)
    )


def calculate_monthly_free_cash(profile):
    return calculate_total_income(profile) - calculate_total_expenses(profile)


def calculate_goal_adjusted_surplus(profile):
    return calculate_monthly_free_cash(profile) - profile.monthly_savings_goal
