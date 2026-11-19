"""store source document titles on research requirements"""

from alembic import op
import sqlalchemy as sa


revision = '202611190043'
down_revision = '202611190042'
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column['name'] for column in sa.inspect(op.get_bind()).get_columns('research_requirement')}
    if 'source_document_title' not in columns:
        op.add_column('research_requirement', sa.Column('source_document_title', sa.String(length=500), nullable=True))
    if 'source_note_title' not in columns:
        op.add_column('research_requirement', sa.Column('source_note_title', sa.String(length=500), nullable=True))
    source_titles = {
        1331: '01.第0讲-先导课：认识订单流', 1332: '02.第1讲：流动性原理', 1333: '03.1401-【复训】复训流动性原理及结构',
        1334: '04.第2讲：订单流基本概念', 1335: '05.1402-【复训】复训基本概念和名词解释', 1336: '06.第3讲：供应和需求（上集）',
        1337: '07.1403-【复训】复训供需区和OB的区别', 1338: '08.第4讲：供应和需求（下集）', 1339: '09.1404-【复训】复训供需区力量的判断',
        1340: '10.第5讲：订单块（上集）', 1341: '11.第6讲：订单块（下集）', 1342: '12.1406-【复训】复训订单块类型及性质',
        1343: '13.第7讲：合理价值缺口-FVG', 1344: '1409-【复训】订单流交流会(直播2023.07.12)', 1345: '15.20230619-【复训】第7期特训营旁听课堂',
        1346: '16.20230620-【复训】第7期特训营旁听课堂', 1347: '17.20230621-【复训】第7期特训营旁听课堂', 1348: '18.20230622-【复训】第7期特训营旁听课堂',
        1349: '19.20230624-【复训】第7期特训营旁听课堂', 1350: '20.20230623-【复训】第7期特训营旁听课堂', 1351: '21.20230626-【复训】第7期特训营旁听课堂',
        1352: '22.1407-1【复训】复训FVG的多种用法', 1353: '23.1407-2【复训】搭建交易系统预热', 1354: '24第8讲：订单流策略系统（上集）',
        1355: '25第8讲：订单流策略系统（下集）', 1356: '26.20230707-【复训】-分析行情挖掘机会', 1357: '27.1408-【复训】用订单流搭建交易系统',
        1358: '28第9讲：当订单流遇上价格行为', 1359: '29_1409-【复训】订单流交流会', 1360: '30第10讲：如何深入学习订单流',
    }
    note_titles = {
        1331: '第0讲-先导课：认识订单流', 1332: '第1讲：流动性原理', 1333: '1401-复训流动性原理及结构', 1334: '第2讲：订单流基本概念',
        1335: '1402-复训基本概念和名词解释', 1336: '第3讲：供应和需求（上集）', 1337: '1403-复训供需区和OB的区别', 1338: '第4讲：供应和需求（下集）',
        1339: '1404-复训供需区力量的判断', 1340: '第5讲：订单块（上集）', 1341: '第6讲：订单块（下集）', 1342: '1406-复训订单块类型及性质',
        1343: '第7讲：合理价值缺口-FVG', 1344: '订单流交流会(直播2023.07.12)', 1345: '20230619-第7期特训营旁听课堂', 1346: '20230620-第7期特训营旁听课堂',
        1347: '20230621-第7期特训营旁听课堂', 1348: '20230622-第7期特训营旁听课堂', 1349: '20230624-第7期特训营旁听课堂', 1350: '20230623-第7期特训营旁听课堂',
        1351: '20230626-第7期特训营旁听课堂', 1352: '1407-1复训FVG的多种用法', 1353: '1407-2搭建交易系统预热', 1354: '第8讲：订单流策略系统（上集）',
        1355: '第8讲：订单流策略系统（下集）', 1356: '20230707--分析行情挖掘机会', 1357: '1408-用订单流搭建交易系统', 1358: '第9讲：当订单流遇上价格行为',
        1359: '1409-订单流交流会', 1360: '第10讲：如何深入学习订单流',
    }
    requirement = sa.table('research_requirement', sa.column('source_document_id', sa.BigInteger), sa.column('source_note_id', sa.BigInteger), sa.column('source_document_title', sa.String), sa.column('source_note_title', sa.String))
    for document_id, title in source_titles.items():
        op.execute(requirement.update().where(requirement.c.source_document_id == document_id).values(source_document_title=title))
    for note_id, title in note_titles.items():
        op.execute(requirement.update().where(requirement.c.source_note_id == note_id).values(source_note_title=title))


def downgrade() -> None:
    op.drop_column('research_requirement', 'source_note_title')
    op.drop_column('research_requirement', 'source_document_title')
