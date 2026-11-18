export const feizhuDemoResources = [
  { id: 'business-system', filename: '一人公司 AI 商业系统', size: 4964319599, isdir: 1, type: 'baidu', updatetime: '2026-11-17 06:46:07', category: 6, filelist: [{ isdir: 1, filename: '02_素材模板' }, { filename: '001_第一节：一人公司AI商业架构.mp4', size: 474569653, ext: 'mp4' }, { filename: '每日更新.md', size: 1416, ext: 'md' }, { filename: '风险提醒（必看）.txt', size: 606, ext: 'txt' }, { filename: '003_第三节：AI产品定位和产品塑造.mp4', size: 856591722, ext: 'mp4' }], haspwd: true, pwd: '演示提取码', valid: 1 },
  { id: 'flow-insight', filename: '《超越流量：商业模式新洞察》', size: 132118078, isdir: 1, type: 'baidu', updatetime: '2026-09-28 21:11:12', category: 6, filelist: [{ isdir: 1, filename: '《超越流量：商业模式新洞察》' }, { filename: '超越流量：商业模式新洞察.pdf', size: 47727624, ext: 'pdf' }, { filename: '超越流量：商业模式新洞察.mobi', size: 24878583, ext: 'mobi' }, { filename: '超越流量：商业模式新洞察.jpg', size: 342841, ext: 'jpg' }, { filename: '超越流量：商业模式新洞察.epub', size: 26493939, ext: 'epub' }], valid: 1 },
  { id: 'business-canvas', filename: '商业模式画布方法介绍_mp4', size: 16939419, isdir: 1, type: 'baidu', updatetime: '2026-10-11 20:29:00', category: 6, filelist: [{ filename: '商业模式沙龙.ppt', size: 7006208, ext: 'ppt' }, { isdir: 1, filename: '商业模式画布方法介绍_mp4' }, { filename: '商业模式画布方法介绍.mp4', size: 9933211, ext: 'mp4' }] },
  { id: 'business-capital', filename: '[明清时代商人及商业资本].傅衣凌.扫描版.pdf', size: 4197494, type: 'baidu', ext: 'pdf', updatetime: '2026-09-23 19:09:56', category: 4, filelist: [{ filename: '[明清时代商人及商业资本].傅衣凌.扫描版.pdf', size: 4197494, ext: 'pdf' }], valid: 1 },
  { id: 'business-survival', filename: '第二课：如何在商业公司里生存与发展', size: 120522713, isdir: 1, type: 'baidu', updatetime: '2026-10-22 22:35:05', category: 6, filelist: [{ isdir: 1, filename: '第二课：如何在商业公司里生存与发展' }, { filename: '第二课：如何在商业公司里生存与发展.mp4', size: 120522713, ext: 'mp4' }] },
  { id: 'business-nature', filename: '商业性质概论.mobi', size: 546168, type: 'baidu', ext: 'mobi', updatetime: '2026-04-04 19:26:10', category: 4, filelist: [{ filename: '商业性质概论.mobi', size: 546168, ext: 'mobi' }] },
  { id: 'marketing-guide', filename: '社交营销必备技能：从定位到成交', size: 86749132, isdir: 1, type: 'baidu', updatetime: '2026-10-19 11:30:00', category: 6, filelist: [{ filename: '01_建立正确的社交思维.mp4', size: 24403511, ext: 'mp4' }, { filename: '02_社交营销必备技能.pdf', size: 16002786, ext: 'pdf' }, { filename: '03_各平台营销实操.mp4', size: 46342835, ext: 'mp4' }] },
  { id: 'ai-positioning', filename: 'AI 时代商业定位与产品塑造', size: 32675091, type: 'baidu', ext: 'pdf', updatetime: '2026-10-09 09:15:34', category: 4, filelist: [{ filename: 'AI 时代商业定位与产品塑造.pdf', size: 32675091, ext: 'pdf' }] }
]

export const feizhuDemoTotal = 84012
export const feizhuPageSize = 15
export const feizhuPlatforms = [{ value: 'baidu', label: '百度网盘' }, { value: 'aliyun', label: '阿里云盘', disabled: true }, { value: 'quark', label: '夸克网盘', disabled: true }, { value: 'xunlei', label: '迅雷网盘', disabled: true }]

export function getDemoResources(page, keyword = '') {
  const normalized = keyword.trim().toLowerCase()
  const matched = normalized ? feizhuDemoResources.filter(item => `${item.filename} ${item.filelist.map(file => file.filename).join(' ')}`.toLowerCase().includes(normalized)) : feizhuDemoResources
  const source = matched.length ? matched : []
  if (!source.length) return { rows: [], total: 0 }
  const start = (page - 1) * feizhuPageSize
  return {
    rows: Array.from({ length: feizhuPageSize }, (_, index) => source[(start + index) % source.length]),
    total: normalized ? source.length : feizhuDemoTotal
  }
}

export function getDemoResource(id) {
  return feizhuDemoResources.find(item => item.id === id) || feizhuDemoResources[0]
}
