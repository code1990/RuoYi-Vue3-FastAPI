/**
 * Copyright (c) 2013-Now http://aidex.vip All rights reserved.
 */
const config = {
	productName: 'RuoYi UniApp Template',
	companyName: 'Your Company',
	productVersion: '1.0.0',
	appVersion: 1,
	adminPath: '',
	apiBaseUrl: {
		default: 'http://101.34.90.245:8088',
		h5: 'http://101.34.90.245:8088',
		app: 'http://101.34.90.245:8088'
	},
	buildProfile: {
		androidPackageName: 'com.example.ruoyiuniapp',
		iosBundleId: 'com.example.ruoyiuniapp'
	}
}

let platformCode = 'h5';
let runtimeBaseUrl = config.apiBaseUrl.h5 || config.apiBaseUrl.default;

// #ifdef APP-PLUS
platformCode = 'android';
runtimeBaseUrl = config.apiBaseUrl.app || config.apiBaseUrl.default;
// #endif

config.appCode = platformCode;
config.baseUrl = runtimeBaseUrl;

export default config;
