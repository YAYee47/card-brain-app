from app.services.diff_engine import serialize_alerts


class DummyAlert:
    def __init__(self):
        self.id = 7
        self.alert_type = "BENEFIT_CHANGE"
        self.severity = "WARNING"
        self.card_id = 3
        self.user_card_id = 10
        self.title = "權益異動"
        self.body = "內容"
        self.diff_detail = "detail"
        self.is_read = False
        self.created_at = __import__("datetime").datetime(2026, 8, 15, 9, 30, 0)


def test_serialize_alerts_converts_model_to_schema():
    result = serialize_alerts([DummyAlert()])

    assert len(result) == 1
    assert result[0].id == 7
    assert result[0].alert_type == "BENEFIT_CHANGE"
    assert result[0].created_at == "2026-08-15T09:30:00"
