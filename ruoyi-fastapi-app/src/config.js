// APP 打包后不能使用 localhost；生产构建连接已部署的 FastAPI 服务。
const baseUrl =
  process.env.NODE_ENV === "production"
    ? "http://101.34.90.245/prod-api"
    : "http://localhost:9099";

// 应用全局配置
export default {
  baseUrl,
  // 应用信息
  appInfo: {
    // 应用名称
    name: "期货模拟交易",
    // 应用版本
    version: "1.9.0",
    // 应用logo
    logo: "/static/logo.png",
    // 官方网站
    site_url: "https://vfadmin.insistence.tech",
    // 政策协议
    agreements: [
      {
        title: "隐私政策",
        url: "https://ruoyi.vip/protocol.html",
      },
      {
        title: "用户服务协议",
        url: "https://ruoyi.vip/protocol.html",
      },
    ],
  },
};
