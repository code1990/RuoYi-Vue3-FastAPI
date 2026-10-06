import request from "@/utils/request";

export const getFutureRelations = () => request({ url: "/future/relation/list", method: "get" });
