import os
import unittest
from unittest.mock import Mock, patch

from module_future.service.future_option_calendar_service import FutureOptionCalendarService


class FutureOptionCalendarServiceTest(unittest.TestCase):
    @patch.dict(os.environ, {'FUYAO_API_KEY': 'test-key'}, clear=False)
    @patch('module_future.service.future_option_calendar_service.requests.get')
    def test_queries_timeline_with_full_thscode(self, get):
        response = Mock()
        response.json.return_value = {'code': 0, 'data': {'thscode': 'IO2601-C-4000.CFE', 'trade_stages': []}}
        get.return_value = response
        self.assertEqual('IO2601-C-4000.CFE', FutureOptionCalendarService.get_timeline('IO2601-C-4000.CFE')['thscode'])
        self.assertEqual({'thscode': 'IO2601-C-4000.CFE'}, get.call_args.kwargs['params'])
        self.assertEqual('test-key', get.call_args.kwargs['headers']['X-api-key'])
