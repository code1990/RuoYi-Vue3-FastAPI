import request from "@/utils/request";

export const listMarginModels = () => request({ url: "/stock/margin/long-model/list", method: "get", params: { pageNum: 1, pageSize: 30 } });
