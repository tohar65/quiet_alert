from oref_alert_parser.locations import APPROVED_LOCATIONS

def test_approved_locations_not_empty():
    assert len(APPROVED_LOCATIONS) > 0

def test_approved_locations_sorted():
    # Note: Hebrew sorting in Python might differ from Oref's exact expectations,
    # but we check if it's generally sorted as per the list.
    assert APPROVED_LOCATIONS == sorted(APPROVED_LOCATIONS)

def test_specific_locations_exist():
    assert "פתח תקווה" in APPROVED_LOCATIONS
    assert "תל אביב - מרכז העיר" in APPROVED_LOCATIONS
    assert "אבו גוש" in APPROVED_LOCATIONS
