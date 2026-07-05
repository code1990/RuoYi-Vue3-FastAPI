<template>
  <div class="stock-main-page">
    <div class="hero-panel">
      <div>
        <p class="hero-kicker">Night Super Cards</p>
        <h1 class="hero-title">三日超额选股卡片</h1>
        <p class="hero-desc">
          统一展示 240min、60min、60+240 交集三个维度。默认显示前 3 个选股器，可展开查看最近 10 个。
        </p>
      </div>
      <div class="hero-actions">
        <el-date-picker
          v-model="tradeDateValue"
          type="date"
          value-format="YYYYMMDD"
          format="YYYY-MM-DD"
          placeholder="选择交易日"
          clearable
          @change="handleTradeDateChange"
        />
        <el-button :loading="loading" type="primary" @click="loadCards(visibleLimit)">
          刷新
        </el-button>
      </div>
    </div>

    <div class="toolbar">
      <div class="toolbar-meta">
        <span>交易日：{{ displayTradeDate }}</span>
        <span>当前展示：{{ cardRows.length }}</span>
      </div>
      <el-button link type="primary" @click="toggleExpanded">
        {{ expanded ? '收起到前 3 个' : '展开最近 10 个选股器' }}
      </el-button>
    </div>

    <el-skeleton v-if="loading && !cardRows.length" :rows="6" animated />

    <div v-else-if="cardRows.length" class="cards-grid">
      <el-card
        v-for="row in cardRows"
        :key="row.selectorKey"
        shadow="hover"
        class="selector-card"
      >
        <template #header>
          <div class="card-header">
            <div>
              <div class="selector-name">{{ row.selectorName }}</div>
              <div class="selector-subtitle">选股器 {{ row.rank }}</div>
            </div>
            <el-tag effect="plain" type="success">
              {{ row.filledCount }}/{{ dimensions.length }}
            </el-tag>
          </div>
        </template>

        <div class="dimension-list">
          <div
            v-for="dimension in dimensions"
            :key="`${row.selectorKey}-${dimension.sourceType}`"
            class="dimension-item"
            :class="{ empty: !row.values[dimension.sourceType] }"
          >
            <div class="dimension-label">{{ dimension.label }}</div>
            <template v-if="row.values[dimension.sourceType]">
              <div class="dimension-value">
                {{ formatPercent(row.values[dimension.sourceType].premium3dPct) }}
              </div>
              <div class="dimension-note">
                {{ row.values[dimension.sourceType].selectorName || row.selectorName }}
              </div>
            </template>
            <template v-else>
              <div class="dimension-empty">空</div>
              <div class="dimension-note">该维度暂无数据</div>
            </template>
          </div>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="当前没有返回三日超额卡片数据" />
  </div>
</template>

<script setup name="StockNightSuperMain">
import { computed, onMounted, ref } from 'vue'
import { getNightSuperCards } from '@/api/stock/nightSuper'

const loading = ref(false)
const expanded = ref(false)
const tradeDateValue = ref('')
const dimensions = ref([])
const cardRows = ref([])
const responseTradeDate = ref('')

const visibleLimit = computed(() => (expanded.value ? 10 : 3))
const displayTradeDate = computed(() => responseTradeDate.value || tradeDateValue.value || '最新')

function loadCards(limit = 3) {
  loading.value = true
  return getNightSuperCards({
    limit,
    tradeDate: tradeDateValue.value || undefined
  })
    .then((response) => {
      const data = response?.data || {}
      dimensions.value = Array.isArray(data.dimensions) ? data.dimensions : []
      responseTradeDate.value = data.tradeDate || ''
      cardRows.value = buildCardRows(Array.isArray(data.rows) ? data.rows : [], dimensions.value)
    })
    .finally(() => {
      loading.value = false
    })
}

function buildCardRows(rows, dimensionDefs) {
  const grouped = new Map()

  rows.forEach((item, index) => {
    const selectorName = item.selectorName || item.xgName || `选股器${index + 1}`
    const selectorKey = item.selectorKey || item.xgCode || item.xgName || `${selectorName}-${index}`

    if (!grouped.has(selectorKey)) {
      grouped.set(selectorKey, {
        selectorKey,
        selectorName,
        rank: grouped.size + 1,
        values: {}
      })
    }

    grouped.get(selectorKey).values[item.sourceType] = item
  })

  return Array.from(grouped.values()).map((row) => ({
    ...row,
    filledCount: dimensionDefs.filter((dimension) => !!row.values[dimension.sourceType]).length
  }))
}

function formatPercent(value) {
  if (value === null || value === undefined || value === '') {
    return '--'
  }
  const numeric = Number(value)
  if (Number.isNaN(numeric)) {
    return String(value)
  }
  return `${numeric.toFixed(2)}%`
}

function toggleExpanded() {
  expanded.value = !expanded.value
  loadCards(visibleLimit.value)
}

function handleTradeDateChange() {
  loadCards(visibleLimit.value)
}

onMounted(() => {
  loadCards(visibleLimit.value)
})
</script>

<style lang="scss" scoped>
.stock-main-page {
  min-height: calc(100vh - 84px);
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.1), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.hero-panel {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
  margin-bottom: 18px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.hero-kicker {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-title {
  margin: 0;
  color: #0f172a;
  font-size: 32px;
  line-height: 1.2;
}

.hero-desc {
  max-width: 760px;
  margin: 12px 0 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.75;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.toolbar-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  color: #475569;
  font-size: 13px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}

.selector-card {
  border: none;
  border-radius: 22px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.selector-name {
  color: #0f172a;
  font-size: 18px;
  font-weight: 700;
}

.selector-subtitle {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

.dimension-list {
  display: grid;
  gap: 12px;
}

.dimension-item {
  padding: 16px 18px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.88), rgba(255, 255, 255, 0.96));
}

.dimension-item.empty {
  border-style: dashed;
  border-color: rgba(148, 163, 184, 0.34);
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.96), rgba(255, 255, 255, 0.96));
}

.dimension-label {
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dimension-value {
  margin-top: 10px;
  color: #0f172a;
  font-size: 26px;
  font-weight: 700;
}

.dimension-empty {
  margin-top: 10px;
  color: #94a3b8;
  font-size: 22px;
  font-weight: 700;
}

.dimension-note {
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .stock-main-page {
    padding: 16px;
  }

  .hero-panel {
    flex-direction: column;
    padding: 22px 18px;
    border-radius: 18px;
  }

  .hero-title {
    font-size: 26px;
  }

  .hero-actions,
  .toolbar {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-meta {
    gap: 10px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
