import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { closePaperPosition, getFutureQuotes, getPaperAccount, getPaperOrders, openPaperPosition } from "@/api/future/paper-trading";

const seedQuotes = [
  { code: "IF2606", name: "沪深300", price: 3842.6, change: 0.68, multiplier: 300 },
  { code: "AU2606", name: "沪金", price: 986.42, change: -0.31, multiplier: 1000 },
  { code: "RB2610", name: "螺纹钢", price: 3186, change: 1.22, multiplier: 10 },
];

export const useTradingStore = defineStore("trading", () => {
  const cash = ref(0); const equity = ref(0); const unrealizedPnl = ref(0); const positions = ref([]); const orders = ref([]); const quotes = ref(seedQuotes); const selectedCode = ref(seedQuotes[0].code);
  const selectedQuote = computed(() => quotes.value.find((item) => item.code === selectedCode.value) || quotes.value[0]);
  const selectContract = (code) => { selectedCode.value = code; };
  async function refreshQuotes() { await sync(); }
  async function sync() {
    const [account, orderRows, quoteRows] = await Promise.all([getPaperAccount(), getPaperOrders(), getFutureQuotes()]);
    cash.value = account.data.cash; equity.value = account.data.equity; unrealizedPnl.value = account.data.unrealizedPnl; positions.value = account.data.positions; orders.value = orderRows.data;
    quotes.value = quoteRows.data.rows.map((item) => ({ code: item.contractCode, name: item.contractName, price: item.lastPx, change: item.pxChangeRate, multiplier: 1 }));
    if (!quotes.value.some((item) => item.code === selectedCode.value)) selectedCode.value = quotes.value[0]?.code || "";
  }
  async function openPosition(side, quantity) { await openPaperPosition({ contractCode: selectedCode.value, side, quantity: Number(quantity) }); await sync(); }
  async function closePosition(id) { await closePaperPosition(id); await sync(); }
  return { cash, equity, unrealizedPnl, positions, orders, quotes, selectedQuote, refreshQuotes, selectContract, sync, openPosition, closePosition };
});
