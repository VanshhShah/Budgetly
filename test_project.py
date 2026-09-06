import pytest
from project import parse_amount, monthly_summary, check_budget_status

# ---------- parse_amount ----------

def test_parse_amount_valid():
    assert parse_amount("200") == 200
    assert parse_amount(20) == 20.0
    assert parse_amount("7") == 7.0

def test_parse_amount_rounds_to_two_decimals():
    assert parse_amount("9.999") == 10.0
    assert parse_amount("1.005") == 1.0 or parse_amount("1.005") == 1.01  # float rounding edge case

def test_parse_amount_rejects_non_numeric():
    with pytest.raises(ValueError):
        parse_amount("twelve")

def test_parse_amount_rejects_zero_or_negative():
    with pytest.raises(ValueError):
        parse_amount(0)
    with pytest.raises(ValueError):
        parse_amount(-5)


# ---------- monthly_summary ----------

def test_monthly_summary_groups_by_category():
    expenses = [
        {"date": "2026-09-01", "amount": 100, "category": "groceries", "description": "a"},
        {"date": "2026-09-05", "amount": 150, "category": "groceries", "description": "b"},
        {"date": "2026-09-10", "amount": 200, "category": "transport", "description": "c"},
    ]
    result = monthly_summary(expenses)
    assert result == {"groceries": 1500, "transport": 500}

def test_monthly_summary_filters_by_month():
    expenses = [
        {"date": "2026-09-01", "amount": 1500, "category": "groceries", "description": "a"},
        {"date": "2026-08-15", "amount": 500, "category": "groceries", "description": "b"},
    ]
    result = monthly_summary(expenses, month="2026-09")
    assert result == {"groceries": 1500}

def test_monthly_summary_empty_list():
    assert monthly_summary([]) == {}


# ---------- check_budget_status ----------

def test_check_budget_status_under():
    assert check_budget_status(spent=500, budget=2000) == "under"

def test_check_budget_status_warning():
    assert check_budget_status(spent=1700, budget=2000) == "warning"

def test_check_budget_status_over():
    assert check_budget_status(spent=2500, budget=2000) == "over"


def test_check_budget_status_invalid_budget():
    with pytest.raises(ValueError):
        check_budget_status(spent=10, budget=0)