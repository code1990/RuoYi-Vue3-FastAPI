from datetime import date, datetime
import unittest
from zoneinfo import ZoneInfo

from module_future.service.training_service import TrainingService
from module_future.entity.do.paper_trading_do import FutureTrainingDecision
from module_future.entity.vo.training_vo import TrainingDecisionModel


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

    def test_history_model_uses_client_field_names(self) -> None:
        item = FutureTrainingDecision(decision_id=1, trade_date=date(2026, 10, 8), contract_code='RB888.XSGE', contract_name='螺纹钢主力', decision='多', reason='趋势向上', entry_price=3200, status='pending', create_time=datetime(2026, 10, 8, 15))
        row = TrainingDecisionModel.model_validate(item).model_dump(by_alias=True)
        self.assertEqual((row['contractCode'], row['contractName'], row['decision']), ('RB888.XSGE', '螺纹钢主力', '多'))


if __name__ == '__main__':
    unittest.main()
