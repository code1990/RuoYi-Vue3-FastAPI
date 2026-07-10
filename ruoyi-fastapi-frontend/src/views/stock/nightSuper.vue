<template>
  <div class="stock-main-page">
    <div class="hero-panel">
      <div>
        <p class="hero-kicker">Night Super Cards</p>
        <h1 class="hero-title">Night Super</h1>
        <p class="hero-desc">
          New page for the backend shape: signalName plus cards[240|60|300].
        </p>
      </div>
      <div class="hero-actions">
        <el-date-picker
          v-model="tradeDateValue"
          type="date"
          value-format="YYYYMMDD"
          format="YYYY-MM-DD"
          placeholder="trade date"
          clearable
          @change="handleTradeDateChange"
        />
        <el-select v-model="limit" style="width: 120px" @change="loadCards">
          <el-option :value="3" label="top 3" />
          <el-option :value="10" label="top 10" />
        </el-select>
        <el-button :loading="loading" type="primary" @click="loadCards">Refresh</el-button>
      </div>
    </div>

    <div class="toolbar">
      <div class="toolbar-meta">
        <span>Trade Date: {{ displayTradeDate }}</span>
        <span>Rows: {{ rows.length }}</span>
      </div>
    </div>

    <el-skeleton v-if="loading && !rows.length" :rows="6" animated />

    <div v-else-if="rows.length" class="cards-grid">
      <el-card v-for="(row, rowIndex) in rows" :key="row.signalName || rowIndex" shadow="hover" class="selector-card">
        <template #header>
          <div class="card-header">
            <div>
              <div class="selector-name">{{ row.signalName || `signal ${rowIndex + 1}` }}</div>
              <div class="selector-subtitle">rankScore {{ formatNumber(row.rankScore) }}</div>
            </div>
            <el-tag effect="plain" type="success">
              {{ countExistingCards(row.cards) }}/{{ visibleDimensions.length }}
            </el-tag>
          </div>
        </template>

        <div class="dimension-list">
          <div
            v-for="dimension in visibleDimensions"
            :key="`${row.signalName}-${dimension.sourceType}`"
            class="dimension-item"
            :class="{ empty: !row.cards?.[dimension.sourceType]?.exists }"
          >
            <div class="dimension-label">{{ dimension.label }}</div>
            <template v-if="row.cards?.[dimension.sourceType]?.exists">
              <div class="dimension-value">
                {{ formatPercent(row.cards[dimension.sourceType].superRate) }}
              </div>
              <div class="dimension-note">
                ok {{ formatPercent(row.cards[dimension.sourceType].okRate) }} / total {{ formatNumber(row.cards[dimension.sourceType].totalCount) }}
              </div>
              <div class="dimension-note">
                updated {{ row.cards[dimension.sourceType].updatedAt || '--' }}
              </div>
            </template>
            <template v-else>
              <div class="dimension-empty">empty</div>
              <div class="dimension-note">
                {{ row.cards?.[dimension.sourceType]?.emptyReason || 'no data' }}
              </div>
            </template>
          </div>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="No night super data" />
  </div>
</template>

<script setup name="StockNightSuper">
import { computed, onMounted, ref } from 'vue'
import { getNightSuperCards } from '@/api/stock/nightSuper'

const loading = ref(false)
const tradeDateValue = ref('')
const responseTradeDate = ref('')
const limit = ref(3)
const rows = ref([])
const dimensions = ref([])

const fallbackDimensions = [
  { sourceType: '240', label: '240min' },
  { sourceType: '60', label: '60min' },
  { sourceType: '300', label: '60+240' }
]

const visibleDimensions = computed(() => (dimensions.value.length ? dimensions.value : fallbackDimensions))
const displayTradeDate = computed(() => responseTradeDate.value || tradeDateValue.value || 'latest')

function loadCards() {
  loading.value = true
  return getNightSuperCards({
    limit: limit.value,
    tradeDate: tradeDateValue.value || undefined
  })
    .then((response) => {
      const data = response?.data || {}
      responseTradeDate.value = String(data.tradeDate || '')
      dimensions.value = normalizeDimensions(data.dimensions)
      rows.value = Array.isArray(data.rows) ? data.rows.map(normalizeRow) : []
    })
    .finally(() => {
      loading.value = false
    })
}

function normalizeDimensions(input) {
  if (!Array.isArray(input) || !input.length) {
    return fallbackDimensions
  }
  return input.map((item) => ({
    sourceType: String(item.sourceType || item.key || ''),
    label: item.label || String(item.sourceType || item.key || '--')
  }))
}

function normalizeRow(row) {
  const cards = row.cards || {}
  return {
    signalName: row.signalName,
    rankScore: row.rankScore,
    cards: {
      '240': normalizeCard(cards['240'], '240'),
      '60': normalizeCard(cards['60'], '60'),
      '300': normalizeCard(cards['300'], '300')
    }
  }
}

function normalizeCard(card, sourceType) {
  if (!card) {
    return {
      exists: false,
      sourceType,
      emptyReason: 'no data'
    }
  }
  return {
    exists: !!card.exists,
    sourceType: String(card.sourceType || sourceType),
    label: card.label,
    tradeDate: card.tradeDate,
    signalName: card.signalName,
    totalCount: card.totalCount,
    okCount: card.okCount,
    okRate: card.okRate,
    superCount: card.superCount,
    superRate: card.superRate,
    targetPercent: card.targetPercent,
    superPercent: card.superPercent,
    windowDays: card.windowDays,
    updatedAt: card.updatedAt,
    emptyReason: card.emptyReason
  }
}

function countExistingCards(cards) {
  return visibleDimensions.value.filter((dimension) => !!cards?.[dimension.sourceType]?.exists).length
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

function formatNumber(value) {
  if (value === null || value === undefined || value === '') {
    return '--'
  }
  const numeric = Number(value)
  return Number.isNaN(numeric) ? String(value) : numeric
}

function handleTradeDateChange() {
  loadCards()
}

onMounted(() => {
  loadCards()
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
  flex-wrap: wrap;
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
