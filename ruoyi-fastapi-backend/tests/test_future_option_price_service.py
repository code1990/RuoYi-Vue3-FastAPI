import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from module_future.service.future_option_price_service import FutureOptionPriceService


class FutureOptionPriceServiceTest(unittest.TestCase):
    @patch.dict(os.environ, {'FUYAO_API_KEY': 'test-key'}, clear=False)
    @patch('module_future.service.future_option_price_service.FutureOptionDao.is_market_contract', return_value=True)
    @patch('module_future.service.future_option_price_service.requests.get')
    def test_caches_io_daily_research_quote(self, get, _market_contract):
        response = Mock()
        response.json.return_value = {'code': 0, 'data': {'timestamp': 1790938000000, 'thscode': 'IO2601-C-4000.CFE', 'item': [{
            'timestamp': 1790899200000, 'open_price': 34.8, 'high_price': 36.1, 'low_price': 34.2, 'close_price': 35.2, 'volume': 120, 'turnover': 422400,
        }]}}
        get.return_value = response
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'option.db'
            FutureOptionPriceService.get_daily_research('IO2601-C-4000.CFE', str(path))
            with sqlite3.connect(path) as connection:
                self.assertEqual(('IO2601-C-4000.CFE', 35.2), connection.execute('SELECT thscode, close_price FROM t_option_quote').fetchone())
        self.assertEqual('IO2601-C-4000.CFE', get.call_args.kwargs['params']['thscode'])

    @patch('module_future.service.future_option_price_service.FutureOptionDao.is_market_contract', return_value=False)
    def test_rejects_non_io_contract(self, _market_contract) -> None:
        with self.assertRaisesRegex(ValueError, 'market-pool'):
            FutureOptionPriceService.get_intraday('10011425.SH')
