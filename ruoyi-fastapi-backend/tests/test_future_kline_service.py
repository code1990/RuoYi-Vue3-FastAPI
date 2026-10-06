from module_future.service.future_kline_service import FutureKlineService


def test_five_day_kline_only_returns_latest_five_trade_dates(monkeypatch) -> None:
    rows = [{'time': int(f'202609{day:02d}0900')} for day in (21, 22, 23, 24, 28, 29, 30)]
    monkeypatch.setattr(FutureKlineService, '_get_rows', classmethod(lambda cls, *args: rows))

    result = FutureKlineService.get('WR888.XSGE', '5d', 500)

    assert [item['time'] for item in result['rows']] == [202609230900, 202609240900, 202609280900, 202609290900, 202609300900]
