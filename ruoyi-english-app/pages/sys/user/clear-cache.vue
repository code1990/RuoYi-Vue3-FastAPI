<template>
	<view class="wrap">
		<u-gap height="20" bg-color="#f5f5f5"></u-gap>
		<u-cell-group :border="false">
			<u-cell-item title="Clear Cache" :arrow="false">
				<view slot="right-icon">
					{{ cacheSize }}
				</view>
			</u-cell-item>
		</u-cell-group>
		<view class="u-m-40">
			<u-button type="primary" @click="clearCache" :hair-line="false">Clear Cache</u-button>
		</view>
	</view>
</template>
<script>
/**
 * Copyright (c) 2013-Now http://aidex.vip All rights reserved.
 */
export default {
	data() {
		return {
			cacheSize: '0.00 MB'
		};
	},
	onShow() {
		this.loadCacheSize();
	},
	methods: {
		formatSize(size) {
			if (!size || size <= 0) {
				return '0.00 MB';
			}
			return `${(size / 1024 / 1024).toFixed(2)} MB`;
		},
		loadCacheSize() {
			let size = 0;
			try {
				const storageInfo = uni.getStorageInfoSync();
				size += storageInfo.currentSize * 1024;
			} catch (error) {}

			// #ifdef APP-PLUS
			if (typeof plus !== 'undefined' && plus.cache && plus.cache.calculate) {
				plus.cache.calculate((appSize) => {
					this.cacheSize = this.formatSize(size + appSize);
				});
				return;
			}
			// #endif

			this.cacheSize = this.formatSize(size);
		},
		clearStorageButKeepLifeData() {
			let lifeData = null;
			try {
				lifeData = uni.getStorageSync('lifeData');
				const storageInfo = uni.getStorageInfoSync();
				(storageInfo.keys || []).forEach((key) => {
					if (key !== 'lifeData') {
						uni.removeStorageSync(key);
					}
				});
				if (lifeData) {
					uni.setStorageSync('lifeData', lifeData);
				}
			} catch (error) {}
		},
		clearCache() {
			uni.showLoading({
				title: 'Clearing',
				mask: true
			});

			this.clearStorageButKeepLifeData();

			// #ifdef APP-PLUS
			if (typeof plus !== 'undefined' && plus.cache && plus.cache.clear) {
				plus.cache.clear(() => {
					uni.hideLoading();
					this.loadCacheSize();
					this.$u.toast('Cache cleared');
				});
				return;
			}
			// #endif

			uni.hideLoading();
			this.loadCacheSize();
			this.$u.toast('Cache cleared');
		}
	}
};
</script>
<style lang="scss">
@import '../home/index.scss';

page {
	background-color: #f8f8f8;
}

::v-deep .u-cell-title {
	padding: 25rpx 30rpx;
	font-size: 30rpx;
}
</style>
