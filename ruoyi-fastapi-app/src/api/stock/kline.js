import request from "@/utils/request";

export const getStockKline = (params) => request({ url: "/stock/kline", method: "get", params });
export const getStockProfile = (stockCode) => request({ url: "/stock/company-compare/profile", method: "get", silent: true, params: { stockCode } });
