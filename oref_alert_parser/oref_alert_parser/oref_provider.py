import requests
import json
import gzip
from typing import List, Dict, Any, Optional
from .provider import AlertProvider
from .models import Alert
from .parser import OrefAlertParser

class OrefProvider(AlertProvider):
    """
    Implementation of AlertProvider for Pikud Haoref (Home Front Command).
    """

    def __init__(self, history_url: str, realtime_url: str, user_agent: str):
        self.history_url = history_url
        self.realtime_url = realtime_url
        self.headers = {
            'User-Agent': user_agent,
            'Referer': 'https://www.oref.org.il/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'Accept': 'application/json, text/plain, */*',
        }

    def fetch_realtime_alerts(self) -> List[Alert]:
        """
        Fetches real-time alert data from Oref API.
        """
        headers = self.headers.copy()
        headers['X-Requested-With'] = 'XMLHttpRequest'
        
        try:
            response = requests.get(self.realtime_url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()

            raw_content = response.raw.read()
            if not raw_content or raw_content.strip() == b"":
                return []

            json_text = self._decode_content(response, raw_content)
            if not json_text or not json_text.strip():
                return []

            data = json.loads(json_text)
            alerts_data = []
            if isinstance(data, dict):
                alerts_data = [data]
            elif isinstance(data, list):
                alerts_data = data
            
            if alerts_data:
                parser = OrefAlertParser(alerts_data)
                return parser.get_alerts()
            return []

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            # In a production app, we might want to log this
            # print(f"Error fetching real-time data: {e}")
            return []

    def fetch_history_alerts(self) -> List[Alert]:
        """
        Fetches historical alert data from Oref API.
        """
        headers = self.headers.copy()
        headers['Referer'] = 'https://www.oref.org.il/heb/alerts-history'
        
        try:
            response = requests.get(self.history_url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()

            raw_content = response.raw.read()
            json_text = self._decode_content(response, raw_content)
            
            if not json_text:
                return []
                
            data = json.loads(json_text)
            if data:
                parser = OrefAlertParser(data)
                return parser.get_alerts()
            return []

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            # print(f"Error fetching history data: {e}")
            return []

    def _decode_content(self, response: requests.Response, raw_content: bytes) -> Optional[str]:
        """
        Handles decompression and decoding of the response content.
        """
        try:
            decompressed_content = raw_content
            if response.headers.get('Content-Encoding') == 'gzip':
                try:
                    decompressed_content = gzip.decompress(raw_content)
                except (gzip.BadGzipFile, OSError):
                    pass
            
            return decompressed_content.decode('utf-8-sig')
        except Exception:
            return None
