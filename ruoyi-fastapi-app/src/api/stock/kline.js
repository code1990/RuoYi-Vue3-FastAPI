import request from "@/utils/request";

export const getStockKline = (params) => request({ url: "/stock/kline", method: "get", params });
