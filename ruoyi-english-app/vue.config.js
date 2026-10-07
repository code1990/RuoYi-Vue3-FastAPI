/**
 * Copyright (c) 2013-Now http://aidex.vip All rights reserved.
 */
module.exports = { configureWebpack: { devServer: { port: 8080, proxy: { '/prod-api': { target: 'http://101.34.90.245', changeOrigin: true } } } }, productionSourceMap: false }
