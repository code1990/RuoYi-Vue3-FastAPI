UPDATE sys_menu
SET parent_id=0,
    path='stock-pools',
    component='stock/stockPool',
    route_name='StockPools',
    menu_type='C',
    is_frame=1,
    update_time=NOW(),
    update_by='admin'
WHERE menu_name='股票池';
