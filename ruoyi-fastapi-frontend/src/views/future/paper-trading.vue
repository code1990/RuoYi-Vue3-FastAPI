<template>
  <div class="paper-page" v-loading="loading">
    <el-alert title="线上模拟交易：使用实时行情计算，资金、持仓和成交记录按登录账户保存；不连接真实交易所。" type="warning" :closable="false" show-icon />
    <el-row :gutter="16" class="summary">
      <el-col :span="8"><el-card><div>账户权益</div><b>¥ {{ money(account.equity) }}</b></el-card></el-col>
      <el-col :span="8"><el-card><div>可用资金</div><b>¥ {{ money(account.cash) }}</b></el-card></el-col>
      <el-col :span="8"><el-card><div>浮动盈亏</div><b :class="account.unrealizedPnl >= 0 ? 'rise' : 'fall'">{{ signed(account.unrealizedPnl) }}</b></el-card></el-col>
    </el-row>
    <el-card class="trade"><template #header>模拟开仓</template><el-form inline><el-form-item label="合约"><el-select v-model="form.contractCode" filterable placeholder="选择实时合约" style="width:260px"><el-option v-for="item in quotes" :key="item.contractCode" :label="`${item.contractName} ${item.contractCode}`" :value="item.contractCode" /></el-select></el-form-item><el-form-item label="方向"><el-radio-group v-model="form.side"><el-radio-button label="多">开多</el-radio-button><el-radio-button label="空">开空</el-radio-button></el-radio-group></el-form-item><el-form-item label="手数"><el-input-number v-model="form.quantity" :min="1" :max="100" /></el-form-item><el-button type="primary" @click="open">提交模拟订单</el-button></el-form></el-card>
    <el-card class="table"><template #header>当前持仓</template><el-table :data="account.positions" empty-text="暂无持仓，提交模拟订单后在此查看"><el-table-column prop="contractName" label="合约" /><el-table-column prop="side" label="方向"><template #default="{ row }"><span :class="row.side === '多' ? 'rise' : 'fall'">{{ row.side }}</span></template></el-table-column><el-table-column prop="quantity" label="手数" /><el-table-column label="均价 / 最新"><template #default="{ row }">{{ price(row.averagePrice) }} / {{ price(row.lastPrice) }}</template></el-table-column><el-table-column label="浮动盈亏"><template #default="{ row }"><span :class="row.unrealizedPnl >= 0 ? 'rise' : 'fall'">{{ signed(row.unrealizedPnl) }}</span></template></el-table-column><el-table-column label="操作" width="100"><template #default="{ row }"><el-button link type="danger" @click="close(row.positionId)">平仓</el-button></template></el-table-column></el-table></el-card>
    <el-card class="table"><template #header>最近成交</template><el-table :data="orders" empty-text="暂无成交记录"><el-table-column prop="createTime" label="时间" min-width="165" /><el-table-column prop="contractName" label="合约" /><el-table-column label="操作"><template #default="{ row }">{{ row.action }}{{ row.side }}</template></el-table-column><el-table-column prop="quantity" label="手数" /><el-table-column label="成交价"><template #default="{ row }">{{ price(row.price) }}</template></el-table-column><el-table-column label="已实现盈亏"><template #default="{ row }"><span v-if="row.realizedPnl !== null" :class="row.realizedPnl >= 0 ? 'rise' : 'fall'">{{ signed(row.realizedPnl) }}</span><span v-else>—</span></template></el-table-column></el-table></el-card>
  </div>
</template>
<script setup name="FuturePaperTrading">
import { reactive, ref } from 'vue'
import { listFutureQuote } from '@/api/future/market'
import { closePaperPosition, getPaperAccount, openPaperPosition } from '@/api/future/paper-trading'
const loading = ref(false); const quotes = ref([]); const orders = ref([]); const account = reactive({ cash: 0, equity: 0, unrealizedPnl: 0, positions: [] }); const form = reactive({ contractCode: '', side: '多', quantity: 1 })
const money = value => Number(value || 0).toFixed(2); const price = money; const signed = value => `${Number(value || 0) >= 0 ? '+' : ''}${money(value)}`
async function load() { loading.value = true; try { const [accountRes, quoteRes, orderRes] = await Promise.all([getPaperAccount(), listFutureQuote({ scope: 'domestic', pageNum: 1, pageSize: 100 }), getPaperOrders()]); Object.assign(account, accountRes.data); quotes.value = quoteRes.data.rows || []; orders.value = orderRes.data || []; if (!form.contractCode) form.contractCode = quotes.value[0]?.contractCode || '' } finally { loading.value = false } }
async function open() { if (!form.contractCode) return ElMessage.warning('请选择合约'); await openPaperPosition(form); ElMessage.success('模拟开仓成功'); load() }
async function close(positionId) { await closePaperPosition(positionId); ElMessage.success('已模拟平仓'); load() }
load()
</script>
<style scoped>.paper-page{padding:20px}.summary{margin:16px 0}.summary b{display:block;font-size:25px;margin-top:10px}.trade,.table{margin-top:16px}.rise{color:#f56c6c}.fall{color:#67c23a}</style>
