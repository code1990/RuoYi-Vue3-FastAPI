import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from config.env import AppConfig


class FutureOptionCalendarService:
    URL = 'https://fuyao.aicubes.cn/api/options/calendar/session-timeline'

    @classmethod
    def get_timeline(cls, thscode: str) -> dict:
        load_dotenv(Path(AppConfig.future_stat_db_path).parent / '.env')
        key = os.getenv('HITHINK_FINANCE_API_KEY') or os.getenv('FUYAO_API_KEY')
        if not key:
            raise RuntimeError('FUYAO_API_KEY is required for option calendar')
        response = requests.get(cls.URL, params={'thscode': thscode}, headers={'X-api-key': key}, timeout=(5, 20))
        response.raise_for_status()
        payload = response.json()
        if int(payload.get('code', -1)) != 0:
            raise RuntimeError(f"option calendar API failed: {payload.get('message')}")
        return payload.get('data') or {}
