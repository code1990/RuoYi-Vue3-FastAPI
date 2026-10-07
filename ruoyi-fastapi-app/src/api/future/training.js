import request from "@/utils/request";

export const getTrainingList = () => request({ url: "/future/training/list", method: "get" });
export const submitTrainingDecision = (data) => request({ url: "/future/training/decision", method: "post", data });
export const getTrainingHistory = () => request({ url: "/future/training/history", method: "get" });
