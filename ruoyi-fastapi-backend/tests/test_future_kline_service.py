from module_future.service.future_kline_service import FutureKlineService


def test_five_day_kline_only_returns_latest_five_trade_dates(monkeypatch) -> None:
    rows = [{'time': int(f'202609{day:02d}0900')} for day in (21, 22, 23, 24, 28, 29, 30)]
    monkeypatch.setattr(FutureKlineService, '_get_trend_rows', classmethod(lambda cls, *args: rows))

    result = FutureKlineService.get('WR888.XSGE', '5d', 500)

    assert [item['time'] for item in result['rows']] == [202609230900, 202609240900, 202609280900, 202609290900, 202609300900]


def test_trend_rows_convert_cumulative_volume_to_minute_volume(monkeypatch) -> None:
    class Response:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {'data': {'trend': {'fields': ['min_time', 'last_px', 'business_amount', 'business_balance'], 'WR888.XSGE': [
                [202609300900, 10, 2, 20], [202609300901, 11, 5, 53], [202609300902, 11, 5, 53],
            ]}}}

    monkeypatch.setattr('module_future.service.future_kline_service.requests.get', lambda *args, **kwargs: Response())

    rows = FutureKlineService._get_trend_rows('WR888.XSGE', 'real_trend')

    assert [(row['volume'], row['turnover']) for row in rows] == [(2, 20), (3, 33), (0, 0)]


def test_latest_price_uses_the_last_valid_real_time_point(monkeypatch) -> None:
    monkeypatch.setattr(FutureKlineService, '_get_trend_rows', classmethod(lambda cls, *args: [
        {'close': 3200}, {'close': 0}, {'close': 3212.5},
    ]))

    assert FutureKlineService.get_latest_price('RB888.XSGE') == 3212.5
