import request from "@/utils/request";

export const getMarginCalendar = (month, mode, windowDays) => request({ url: "/stock/margin/calendar", method: "get", params: { month, mode, windowDays } });
export const listMarginModels = (params) => request({ url: "/stock/margin/long-model/list", method: "get", params });
export const listMarginSingle = (params) => request({ url: "/stock/margin/long-performance/list", method: "get", params });
export const listMarginCombo = (params) => request({ url: "/stock/margin/combo/list", method: "get", params });
