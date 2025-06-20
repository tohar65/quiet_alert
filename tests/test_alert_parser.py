import unittest
from alert_parser import categorize_alerts

class TestAlertParser(unittest.TestCase):

    def test_categorize_alerts(self):
        mock_alerts = [
            {"title": "ירי רקטות וטילים", "data": "Tel Aviv"},
            {"title": "Some Other Alert", "data": "Haifa"},
            {"title": "ירי רקטות וטילים", "data": "Jerusalem"}
        ]
        
        active_alerts, upcoming_alerts = categorize_alerts(mock_alerts)
        
        self.assertEqual(len(active_alerts), 2)
        self.assertEqual(len(upcoming_alerts), 1)
        self.assertEqual(active_alerts[0]["data"], "Tel Aviv")
        self.assertEqual(upcoming_alerts[0]["data"], "Haifa")

if __name__ == '__main__':
    unittest.main()