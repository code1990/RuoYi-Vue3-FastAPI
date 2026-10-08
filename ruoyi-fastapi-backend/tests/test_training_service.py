from datetime import datetime
import unittest
from zoneinfo import ZoneInfo

from module_future.service.training_service import TrainingService


class TrainingServiceTest(unittest.TestCase):
    TZ = ZoneInfo('Asia/Shanghai')

    def at(self, hour: int, minute: int) -> datetime:
        return datetime(2026, 10, 8, hour, minute, tzinfo=self.TZ)

    def test_domestic_sessions(self) -> None:
        self.assertTrue(TrainingService.is_trading_time('LC888.XGFE', self.at(14, 55)))
        self.assertFalse(TrainingService.is_trading_time('RB888.XSGE', self.at(18, 33)))
        self.assertFalse(TrainingService.is_trading_time('LC888.XGFE', self.at(21, 0)))
        self.assertTrue(TrainingService.is_trading_time('RB888.XSGE', self.at(22, 59)))
        self.assertFalse(TrainingService.is_trading_time('RB888.XSGE', self.at(23, 0)))
        self.assertTrue(TrainingService.is_trading_time('CU888.XSGE', self.at(0, 59)))
        self.assertFalse(TrainingService.is_trading_time('CU888.XSGE', self.at(1, 0)))
        self.assertTrue(TrainingService.is_trading_time('AU888.XSGE', self.at(2, 29)))
        self.assertFalse(TrainingService.is_trading_time('AU888.XSGE', self.at(2, 30)))


if __name__ == '__main__':
    unittest.main()
