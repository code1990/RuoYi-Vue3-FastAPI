import request from "@/utils/request";

export const getFutureKline = (params) => request({ url: "/future/kline", method: "get", params });
