from module_stock.service.stock_kline_service import StockKlineService


def test_stock_kline_resolves_a_share_markets() -> None:
    assert StockKlineService.market_code('600000') == '600000.SS'
    assert StockKlineService.market_code('000001') == '000001.SZ'
    assert StockKlineService.market_code('830799') == '830799.BJ'


def test_five_day_stock_kline_keeps_latest_trade_dates(monkeypatch) -> None:
    rows = [{'time': int(f'202610{day:02d}0930')} for day in (12, 13, 14, 15, 16, 19)]
    monkeypatch.setattr(StockKlineService, '_trend_rows', classmethod(lambda cls, *args: rows))
    result = StockKlineService.get('000001', '5d', 200)
    assert [str(row['time'])[:8] for row in result['rows']] == ['20261013', '20261014', '20261015', '20261016', '20261019']
