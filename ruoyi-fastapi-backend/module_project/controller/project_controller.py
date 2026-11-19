from datetime import datetime
import csv
from pathlib import Path as FilePath
from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_project.entity.do.project_do import FuncCombinationManage, FuncManage, ProjectManage, ResearchBacktest, ResearchReview, ResearchSimAccount, ResearchStrategy, ResearchFeature, ResearchRequirement
from module_project.entity.vo.project_vo import (BacktestModel, BacktestPageQuery, CombinationModel, CombinationPageQuery, FuncModel,
                                                  FuncPageQuery, ProjectModel, ProjectPageQuery, ReviewModel, ReviewPageQuery, StrategyModel, StrategyPageQuery,
                                                  SimAccountModel, SimAccountPageQuery, ResearchFeatureModel, ResearchFeaturePageQuery, ResearchRequirementModel, ResearchRequirementPageQuery)
from common.aspect.pre_auth import CurrentUserDependency
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil


project_controller = APIRouterPro(prefix='/project/manage', order_num=20, tags=['项目研究-项目管理'], dependencies=[PreAuthDependency()])
function_controller = APIRouterPro(prefix='/function/manage', order_num=21, tags=['项目研究-函数管理'], dependencies=[PreAuthDependency()])
combination_controller = APIRouterPro(prefix='/function/combination', order_num=22, tags=['项目研究-函数组合管理'], dependencies=[PreAuthDependency()])
backtest_controller = APIRouterPro(prefix='/research/backtest', order_num=23, tags=['项目研究-回测'], dependencies=[PreAuthDependency()])
strategy_controller = APIRouterPro(prefix='/research/strategy', order_num=23, tags=['项目研究-交易策略'], dependencies=[PreAuthDependency()])
simulation_controller = APIRouterPro(prefix='/research/simulation', order_num=24, tags=['项目研究-模拟交易'], dependencies=[PreAuthDependency()])
review_controller = APIRouterPro(prefix='/research/review', order_num=25, tags=['项目研究-复盘'], dependencies=[PreAuthDependency()])
research_requirement_controller = APIRouterPro(prefix='/research/requirement', order_num=26, tags=['项目研究-需求管理'], dependencies=[PreAuthDependency()])
research_feature_controller = APIRouterPro(prefix='/research/feature', order_num=27, tags=['项目研究-功能管理'], dependencies=[PreAuthDependency()])


async def _save(db: AsyncSession, model, data: dict, user: CurrentUserModel, is_new: bool):
    record_id = data.pop('id', None)
    data['created_by'] = user.user.user_name
    data['create_time' if is_new else 'update_time'] = datetime.now()
    if is_new:
        db.add(model(**data))
    else:
        obj = (await db.execute(select(model).where(model.id == record_id))).scalars().first()
        if not obj:
            return False
        for key, value in data.items():
            if key != 'id' and hasattr(obj, key):
                setattr(obj, key, value)
    await db.commit()
    return True


@project_controller.get('/list', response_model=PageResponseModel[ProjectModel], dependencies=[UserInterfaceAuthDependency('project:manage:list')])
async def project_list(query: Annotated[ProjectPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(ProjectManage).where(ProjectManage.project_name.like(f'%{query.project_name}%') if query.project_name else True).order_by(ProjectManage.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@project_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('project:manage:add')])
async def project_add(data: ProjectModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await _save(db, ProjectManage, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='新增成功')


@project_controller.put('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('project:manage:edit')])
async def project_edit(data: ProjectModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    if not await _save(db, ProjectManage, data.model_dump(exclude_unset=True), user, False):
        return ResponseUtil.failure(msg='项目不存在')
    return ResponseUtil.success(msg='更新成功')


@project_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('project:manage:remove')])
async def project_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    project_ids = [int(i) for i in ids.split(',')]
    linked_count = (await db.execute(select(func.count()).select_from(FuncManage).where(FuncManage.project_id.in_(project_ids)))).scalar_one()
    if linked_count:
        return ResponseUtil.failure(msg='项目下存在函数，请先删除函数')
    await db.execute(delete(ProjectManage).where(ProjectManage.id.in_(project_ids)))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@project_controller.get('/{id}', response_model=DataResponseModel[ProjectModel], dependencies=[UserInterfaceAuthDependency('project:manage:list')])
async def project_detail(id: int, db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=(await db.get(ProjectManage, id)))


@function_controller.get('/list', response_model=PageResponseModel[FuncModel], dependencies=[UserInterfaceAuthDependency('function:manage:list')])
async def function_list(query: Annotated[FuncPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(FuncManage).where(FuncManage.func_name.like(f'%{query.func_name}%') if query.func_name else True).order_by(FuncManage.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@function_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('function:manage:add')])
async def function_add(data: FuncModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await _save(db, FuncManage, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='新增成功')


@function_controller.put('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('function:manage:edit')])
async def function_edit(data: FuncModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    if not await _save(db, FuncManage, data.model_dump(exclude_unset=True), user, False):
        return ResponseUtil.failure(msg='函数不存在')
    return ResponseUtil.success(msg='更新成功')


@function_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('function:manage:remove')])
async def function_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    function_ids = [int(i) for i in ids.split(',')]
    linked = (await db.execute(
        select(func.count()).select_from(ResearchFeature).where(
            func.json_overlaps(ResearchFeature.function_ids, func.json_array(*function_ids))
        )
    )).scalar_one()
    if linked:
        return ResponseUtil.failure(msg='函数已关联功能，请先移除功能中的关联')
    await db.execute(delete(FuncManage).where(FuncManage.id.in_(function_ids)))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@function_controller.get('/{id}/visual-data', dependencies=[UserInterfaceAuthDependency('function:manage:list')])
async def function_visual_data(
    id: int,
    db: Annotated[AsyncSession, DBSessionDependency()],
    source: Annotated[str, Query()] = 'static',
    func_name: Annotated[str | None, Query()] = None,
) -> Response:
    if source == 'real':
        return ResponseUtil.failure(msg='真实行情接口尚未配置')
    function = await db.get(FuncManage, id)
    if not function:
        return ResponseUtil.failure(msg='函数不存在')
    if not function.visual_enabled:
        return ResponseUtil.failure(msg='该函数未配置可视化')
    csv_path = FilePath(__file__).resolve().parents[1] / 'demo_data' / 'EURUSD_15M.csv'
    with csv_path.open(encoding='utf-8') as file:
        rows = [
            {
                'time': row['Date'],
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': float(row['Volume']),
            }
            for row in csv.DictReader(file)
        ]
    data = {
        'source': 'static',
        'symbol': 'EURUSD',
        'timeframe': '15m',
        'funcName': function.func_name,
        'visualEnabled': function.visual_enabled,
        'visualSummary': function.visual_summary,
        'rows': rows,
    }
    indicator_files = {
        'swing_highs_lows': ('swing_highs_lows_result_data.csv', {'HighLow': 'highLow', 'Level': 'level'}),
        'fvg': ('fvg_result_data.csv', {'FVG': 'fvg', 'Top': 'top', 'Bottom': 'bottom', 'MitigatedIndex': 'mitigatedIndex'}),
        'bos_choch': ('bos_choch_result_data.csv', {'BOS': 'bos', 'CHOCH': 'choch', 'Level': 'level', 'BrokenIndex': 'brokenIndex'}),
        'ob': ('ob_result_data.csv', {'OB': 'ob', 'Top': 'top', 'Bottom': 'bottom', 'OBVolume': 'obVolume', 'MitigatedIndex': 'mitigatedIndex', 'Percentage': 'percentage'}),
        'liquidity': ('liquidity_result_data.csv', {'Liquidity': 'liquidity', 'Level': 'level', 'End': 'end', 'Swept': 'swept'}),
        'previous_high_low': ('previous_high_low_result_data_1D.csv', {'PreviousHigh': 'previousHigh', 'PreviousLow': 'previousLow', 'BrokenHigh': 'brokenHigh', 'BrokenLow': 'brokenLow'}),
        'sessions': ('sessions_result_data.csv', {'Active': 'active', 'High': 'high', 'Low': 'low'}),
        'retracements': ('retracements_result_data.csv', {'Direction': 'direction', 'CurrentRetracement%': 'currentRetracement', 'DeepestRetracement%': 'deepestRetracement'}),
    }
    visual_func_name = func_name or function.func_name
    if visual_func_name in indicator_files:
        result_file, fields = indicator_files[visual_func_name]
        result_path = FilePath(__file__).resolve().parents[1] / 'demo_data' / result_file
        with result_path.open(encoding='utf-8') as file:
            indicator = []
            for row in csv.DictReader(file):
                item = {}
                for source, target in fields.items():
                    value = row[source].strip()
                    item[target] = float(value) if value else None
                indicator.append(item)
        data['indicator'] = indicator[:len(rows)]
    return ResponseUtil.success(data=data)


@function_controller.get('/{id}', response_model=DataResponseModel[FuncModel], dependencies=[UserInterfaceAuthDependency('function:manage:list')])
async def function_detail(id: int, db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=(await db.get(FuncManage, id)))


@research_requirement_controller.get('/list', response_model=PageResponseModel[ResearchRequirementModel], dependencies=[UserInterfaceAuthDependency('research:requirement:list')])
async def research_requirement_list(query: Annotated[ResearchRequirementPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    keyword = f'%{query.title}%'
    stmt = select(ResearchRequirement).where(or_(ResearchRequirement.title.like(keyword), ResearchRequirement.source_document_title.like(keyword), ResearchRequirement.source_note_title.like(keyword)) if query.title else True).order_by(ResearchRequirement.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@research_requirement_controller.get('/{id}', response_model=DataResponseModel[ResearchRequirementModel], dependencies=[UserInterfaceAuthDependency('research:requirement:list')])
async def research_requirement_detail(id: int, db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=(await db.get(ResearchRequirement, id)))


@research_requirement_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:requirement:add')])
async def research_requirement_add(data: ResearchRequirementModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    if not data.requirement_code or not data.title:
        return ResponseUtil.failure(msg='需求编号和名称不能为空')
    await _save(db, ResearchRequirement, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='需求已创建')


@research_requirement_controller.put('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:requirement:edit')])
async def research_requirement_edit(data: ResearchRequirementModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    if not await _save(db, ResearchRequirement, data.model_dump(exclude_unset=True), user, False):
        return ResponseUtil.failure(msg='需求不存在')
    return ResponseUtil.success(msg='需求已更新')


@research_requirement_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:requirement:remove')])
async def research_requirement_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    requirement_ids = [int(i) for i in ids.split(',')]
    linked = (await db.execute(select(func.count()).select_from(ResearchFeature).where(ResearchFeature.requirement_id.in_(requirement_ids)))).scalar_one()
    if linked:
        return ResponseUtil.failure(msg='需求下存在功能，请先删除功能')
    await db.execute(delete(ResearchRequirement).where(ResearchRequirement.id.in_(requirement_ids)))
    await db.commit()
    return ResponseUtil.success(msg='需求已删除')


@research_feature_controller.get('/list', response_model=PageResponseModel[ResearchFeatureModel], dependencies=[UserInterfaceAuthDependency('research:feature:list')])
async def research_feature_list(query: Annotated[ResearchFeaturePageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(ResearchFeature).where(
        ResearchFeature.title.like(f'%{query.title}%') if query.title else True,
        ResearchFeature.requirement_id == query.requirement_id if query.requirement_id else True,
    ).order_by(ResearchFeature.requirement_id.desc(), ResearchFeature.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


async def _function_ids_exist(db: AsyncSession, function_ids: list[int]) -> bool:
    if not function_ids:
        return True
    found = (await db.execute(select(func.count()).select_from(FuncManage).where(FuncManage.id.in_(function_ids)))).scalar_one()
    return found == len(set(function_ids))


@research_feature_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:feature:add')])
async def research_feature_add(data: ResearchFeatureModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    if not data.requirement_id or not data.feature_code or not data.title:
        return ResponseUtil.failure(msg='关联需求、功能编号和名称不能为空')
    if not await db.get(ResearchRequirement, data.requirement_id):
        return ResponseUtil.failure(msg='关联需求不存在')
    if not await _function_ids_exist(db, data.function_ids or []):
        return ResponseUtil.failure(msg='关联函数不存在')
    await _save(db, ResearchFeature, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='功能已创建')


@research_feature_controller.put('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:feature:edit')])
async def research_feature_edit(data: ResearchFeatureModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    if data.requirement_id and not await db.get(ResearchRequirement, data.requirement_id):
        return ResponseUtil.failure(msg='关联需求不存在')
    if data.function_ids is not None and not await _function_ids_exist(db, data.function_ids):
        return ResponseUtil.failure(msg='关联函数不存在')
    if not await _save(db, ResearchFeature, data.model_dump(exclude_unset=True), user, False):
        return ResponseUtil.failure(msg='功能不存在')
    return ResponseUtil.success(msg='功能已更新')


@research_feature_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:feature:remove')])
async def research_feature_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    await db.execute(delete(ResearchFeature).where(ResearchFeature.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='功能已删除')


@combination_controller.get('/list', response_model=PageResponseModel[CombinationModel], dependencies=[UserInterfaceAuthDependency('function:combination:list')])
async def combination_list(query: Annotated[CombinationPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(FuncCombinationManage).where(FuncCombinationManage.combination_name.like(f'%{query.combination_name}%') if query.combination_name else True).order_by(FuncCombinationManage.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@combination_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('function:combination:add')])
async def combination_add(data: CombinationModel, db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    db.add(FuncCombinationManage(**data.model_dump(exclude_unset=True, exclude={'id'})))
    await db.commit()
    return ResponseUtil.success(msg='新增成功')


@combination_controller.put('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('function:combination:edit')])
async def combination_edit(data: CombinationModel, db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    row = await db.get(FuncCombinationManage, data.id)
    if not row:
        return ResponseUtil.failure(msg='组合不存在')
    for key, value in data.model_dump(exclude_unset=True, exclude={'id'}).items():
        setattr(row, key, value)
    await db.commit()
    return ResponseUtil.success(msg='更新成功')


@combination_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('function:combination:remove')])
async def combination_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    await db.execute(delete(FuncCombinationManage).where(FuncCombinationManage.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@strategy_controller.get('/list', response_model=PageResponseModel[StrategyModel], dependencies=[UserInterfaceAuthDependency('research:strategy:list')])
async def strategy_list(query: Annotated[StrategyPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(ResearchStrategy).where(ResearchStrategy.strategy_name.like(f'%{query.strategy_name}%') if query.strategy_name else True).order_by(ResearchStrategy.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@strategy_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:strategy:add')])
async def strategy_add(data: StrategyModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await _save(db, ResearchStrategy, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='策略已创建')


@strategy_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:strategy:remove')])
async def strategy_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    await db.execute(delete(ResearchStrategy).where(ResearchStrategy.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@backtest_controller.get('/list', response_model=PageResponseModel[BacktestModel], dependencies=[UserInterfaceAuthDependency('research:backtest:list')])
async def backtest_list(query: Annotated[BacktestPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(ResearchBacktest).where(ResearchBacktest.name.like(f'%{query.name}%') if query.name else True).order_by(ResearchBacktest.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@backtest_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:backtest:add')])
async def backtest_add(data: BacktestModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await _save(db, ResearchBacktest, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='回测任务已创建')


@backtest_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:backtest:remove')])
async def backtest_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    await db.execute(delete(ResearchBacktest).where(ResearchBacktest.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@simulation_controller.get('/list', response_model=PageResponseModel[SimAccountModel], dependencies=[UserInterfaceAuthDependency('research:simulation:list')])
async def simulation_list(query: Annotated[SimAccountPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(ResearchSimAccount).where(ResearchSimAccount.account_name.like(f'%{query.account_name}%') if query.account_name else True).order_by(ResearchSimAccount.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@simulation_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:simulation:add')])
async def simulation_add(data: SimAccountModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    payload = data.model_dump(exclude_unset=True)
    payload.setdefault('available_balance', payload.get('initial_balance', 100000))
    await _save(db, ResearchSimAccount, payload, user, True)
    return ResponseUtil.success(msg='模拟账户已创建')


@simulation_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:simulation:remove')])
async def simulation_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    await db.execute(delete(ResearchSimAccount).where(ResearchSimAccount.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@review_controller.get('/list', response_model=PageResponseModel[ReviewModel], dependencies=[UserInterfaceAuthDependency('research:review:list')])
async def review_list(query: Annotated[ReviewPageQuery, Query()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    stmt = select(ResearchReview).order_by(ResearchReview.id.desc())
    return ResponseUtil.success(model_content=await PageUtil.paginate(db, stmt, query.page_num, query.page_size, True))


@review_controller.post('', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:review:add')])
async def review_add(data: ReviewModel, db: Annotated[AsyncSession, DBSessionDependency()], user: Annotated[CurrentUserModel, CurrentUserDependency()]) -> Response:
    await _save(db, ResearchReview, data.model_dump(exclude_unset=True), user, True)
    return ResponseUtil.success(msg='复盘已保存')


@review_controller.delete('/{ids}', response_model=ResponseBaseModel, dependencies=[UserInterfaceAuthDependency('research:review:remove')])
async def review_delete(ids: Annotated[str, Path()], db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    await db.execute(delete(ResearchReview).where(ResearchReview.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')
