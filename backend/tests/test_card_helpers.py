from app.services.billing_cycle import apply_billing_cycle_to_cards


class DummyUserCard:
    def __init__(self, billing_cycle_date: int):
        self.billing_cycle_date = billing_cycle_date


def test_apply_billing_cycle_updates_all_cards_in_place():
    cards = [DummyUserCard(1), DummyUserCard(10), DummyUserCard(25)]

    apply_billing_cycle_to_cards(cards, 15)

    assert [card.billing_cycle_date for card in cards] == [15, 15, 15]
