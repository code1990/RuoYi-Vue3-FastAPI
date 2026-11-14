from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_project.entity.do.project_do import FuncManage, ProjectManage
from module_project.entity.vo.project_vo import FuncModel, FuncPageQuery, ProjectModel, ProjectPageQuery
from common.aspect.pre_auth import CurrentUserDependency
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil


project_controller = APIRouterPro(prefix='/project/manage', order_num=20, tags=['项目研究-项目管理'], dependencies=[PreAuthDependency()])
function_controller = APIRouterPro(prefix='/function/manage', order_num=21, tags=['项目研究-函数管理'], dependencies=[PreAuthDependency()])


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
    await db.execute(delete(FuncManage).where(FuncManage.id.in_([int(i) for i in ids.split(',')])))
    await db.commit()
    return ResponseUtil.success(msg='删除成功')


@function_controller.get('/{id}', response_model=DataResponseModel[FuncModel], dependencies=[UserInterfaceAuthDependency('function:manage:list')])
async def function_detail(id: int, db: Annotated[AsyncSession, DBSessionDependency()]) -> Response:
    return ResponseUtil.success(data=(await db.get(FuncManage, id)))
