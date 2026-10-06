import { createPinia } from "pinia";
import { useUserStore } from "./modules/user";
import { useConfigStore } from "./modules/config";
import { useTradingStore } from "./modules/trading";

const pinia = createPinia();

export default pinia;

export { useUserStore, useConfigStore, useTradingStore };
