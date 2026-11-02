from sqlalchemy import distinct, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_feizhu.entity.do.file_detail_do import FileDetail, FileKeyword, FileKeywordTopic
from module_feizhu.entity.vo.file_detail_vo import FileDetailModel, FileDetailOptionsModel, FileDetailPageModel


class FileDetailService:
    @staticmethod
    def split_values(value: str | None) -> list[str]:
        return [item.strip() for item in (value or '').split(',') if item.strip()]

    @classmethod
    async def options(cls, db: AsyncSession, keyword_ids: str | None) -> FileDetailOptionsModel:
        ids = cls.split_values(keyword_ids)
        topic_statement = select(distinct(FileKeywordTopic.topic))
        if ids:
            topic_statement = topic_statement.where(FileKeywordTopic.keyword_id.in_(ids))
        topics = (await db.scalars(topic_statement.order_by(FileKeywordTopic.topic))).all()
        keywords = (await db.execute(select(FileKeyword.id, FileKeyword.keyword).order_by(FileKeyword.sort_no, FileKeyword.keyword))).all()

        async def values(column):
            return (await db.scalars(select(distinct(column)).where(column.is_not(None)).order_by(column))).all()

        return FileDetailOptionsModel(
            keywords=[{'id': row.id, 'name': row.keyword} for row in keywords],
            topics=topics,
            exts=await values(FileDetail.ext),
            categories=await values(FileDetail.category),
            types=await values(FileDetail.type),
            valids=await values(FileDetail.valid),
            haspwds=await values(FileDetail.haspwd),
        )

    @classmethod
    async def page(
        cls, db: AsyncSession, page_num: int, page_size: int, keyword_ids: str | None, topics: str | None,
        exts: str | None, category: int | None, resource_type: str | None, valid: str | None,
        haspwd: str | None, keyword: str | None,
    ) -> FileDetailPageModel:
        statement = select(FileDetail)
        ids = cls.split_values(keyword_ids)
        if ids:
            statement = statement.where(exists(select(1).where(FileKeywordTopic.topic == FileDetail.topic, FileKeywordTopic.keyword_id.in_(ids))))
        values = cls.split_values(topics)
        if values:
            statement = statement.where(FileDetail.topic.in_(values))
        values = cls.split_values(exts)
        if values:
            statement = statement.where(FileDetail.ext.in_(values))
        if category is not None:
            statement = statement.where(FileDetail.category == category)
        if resource_type:
            statement = statement.where(FileDetail.type == resource_type)
        if valid:
            statement = statement.where(FileDetail.valid == valid)
        if haspwd:
            statement = statement.where(FileDetail.haspwd == haspwd)
        if keyword:
            statement = statement.where(FileDetail.filename.contains(keyword) | FileDetail.topic.contains(keyword) | FileDetail.url.contains(keyword))

        total = await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
        rows = (await db.scalars(statement.order_by(FileDetail.utime.desc(), FileDetail.id.desc()).offset((page_num - 1) * page_size).limit(page_size))).all()
        return FileDetailPageModel(
            rows=[FileDetailModel.model_validate(row, from_attributes=True) for row in rows],
            total=total,
            page_num=page_num,
            page_size=page_size,
        )
