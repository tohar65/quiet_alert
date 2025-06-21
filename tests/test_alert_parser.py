import unittest
from alert_parser import categorize_alerts

class TestAlertParser(unittest.TestCase):

    def test_categorize_alerts(self):
        mock_alerts = [
            {"title": "ירי רקטות וטילים", "data": "Tel Aviv"},
            {"title": "בדקות הקרובות צפויות להתקבל התרעות באזורך", "data": "Ashkelon"},
            {"title": "חדירת כלי טיס עוין", "data": "Golan"},
            {"title": "חדירת כלי טיס עוין - האירוע הסתיים", "data": "Metula"},
            {"title": "ירי רקטות וטילים -  האירוע הסתיים", "data": "Sderot"},
            {"title": "Some Other Alert", "data": "Haifa"},
            {"title": "ירי רקטות וטילים", "data": "Jerusalem"}
        ]
        
        active_alerts, upcoming_alerts, aircraft_intrusion_alerts, ended_alerts, unexpected_alerts = categorize_alerts(mock_alerts)
        
        self.assertEqual(len(active_alerts), 2)
        self.assertEqual(len(upcoming_alerts), 1)
        self.assertEqual(len(aircraft_intrusion_alerts), 1)
        self.assertEqual(len(ended_alerts), 2)
        self.assertEqual(len(unexpected_alerts), 1)
        self.assertEqual(active_alerts[0]["data"], "Tel Aviv")
        self.assertEqual(upcoming_alerts[0]["data"], "Ashkelon")
        self.assertEqual(aircraft_intrusion_alerts[0]["data"], "Golan")
        self.assertEqual(ended_alerts[0]["data"], "Metula")
        self.assertEqual(ended_alerts[1]["data"], "Sderot")
        self.assertEqual(unexpected_alerts[0]["data"], "Haifa")

if __name__ == '__main__':
    unittest.main()