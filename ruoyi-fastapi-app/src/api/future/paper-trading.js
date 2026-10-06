import request from "@/utils/request";

export const getPaperAccount = () => request({ url: "/future/paper-trading/account", method: "get" });
export const getPaperOrders = () => request({ url: "/future/paper-trading/orders", method: "get" });
export const openPaperPosition = (data) => request({ url: "/future/paper-trading/open", method: "post", data });
export const closePaperPosition = (positionId) => request({ url: `/future/paper-trading/positions/${positionId}/close`, method: "post" });
export const getFutureQuotes = () => request({ url: "/future/quote/list", method: "get", params: { scope: "domestic", pageNum: 1, pageSize: 20 } });
