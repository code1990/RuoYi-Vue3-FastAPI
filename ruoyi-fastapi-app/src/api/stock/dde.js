import request from "@/utils/request";

export const getDdeCalendar = (month) => request({ url: "/stock/dde/performance/calendar", method: "get", params: { month } });
export const listDdeSignals = (date) => request({ url: "/stock/dde/performance/list", method: "get", params: { startDate: date, endDate: date, pageNum: 1, pageSize: 200 } });
export const getDdeQuotes = (stockCodes) => request({ url: "/stock/dde/quote/list", method: "get", params: { stockCode: stockCodes.join(",") } });
