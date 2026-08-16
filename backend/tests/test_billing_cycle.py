import pytest

from app.services.billing_cycle import validate_billing_cycle_date


def test_valid_billing_cycle_date_accepts_1_to_31():
    validate_billing_cycle_date(1)
    validate_billing_cycle_date(15)
    validate_billing_cycle_date(31)


def test_invalid_billing_cycle_date_raises_value_error():
    with pytest.raises(ValueError, match="1 至 31"):
        validate_billing_cycle_date(0)

    with pytest.raises(ValueError, match="1 至 31"):
        validate_billing_cycle_date(32)
