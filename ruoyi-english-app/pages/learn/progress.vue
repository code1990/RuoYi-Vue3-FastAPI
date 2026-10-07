<template>
  <view class="page"><view class="content">
    <view class="hero"><text class="trophy">🏆</text><text class="name">我的英语成长</text><text class="cheer">每天进步一点点，你真棒！</text></view>
    <view class="stats"><view><text class="number">{{ progress.stars }}</text><text>收集星星</text></view><view><text class="number">{{ progress.correct }}</text><text>答对题目</text></view><view><text class="number">{{ progress.streak }}</text><text>连续学习</text></view></view>
    <view class="badge"><text class="badge-title">我的小徽章</text><view class="badges"><view :class="{ locked: progress.stars < 1 }">🌱<text>启程</text></view><view :class="{ locked: progress.stars < 5 }">🌟<text>小能手</text></view><view :class="{ locked: progress.stars < 10 }">👑<text>英语王</text></view></view></view>
    <button class="clear" @click="clearProgress">重新开始</button>
  </view></view>
</template>
<script>
export default { data() { return { progress: { stars: 0, correct: 0, streak: 1 } } }, onShow() { this.progress = Object.assign(this.progress, uni.getStorageSync('englishGarden_progress') || {}) }, methods: { clearProgress() { uni.showModal({ title: '重新开始？', content: '已获得的星星会清零哦。', success: res => { if (res.confirm) { this.progress = { stars: 0, correct: 0, streak: 1 }; uni.setStorageSync('englishGarden_progress', this.progress) } } }) } } }
</script>
<style lang="scss" scoped>
.page { min-height: 100vh; padding: 45rpx 0; background: #fff9ed; }.content { width: 82%; max-width: 900px; margin: auto; }.hero { text-align: center; }.trophy,.name,.cheer { display: block; }.trophy { font-size: 150rpx; }.name { font-size: 48rpx; font-weight: 800; }.cheer { margin-top: 15rpx; color: #777; font-size: 28rpx; }.stats { margin-top: 40rpx; padding: 35rpx 20rpx; display: grid; grid-template-columns: repeat(3, 1fr); text-align: center; background: white; border-radius: 30rpx; box-shadow: 0 10rpx 25rpx rgba(89,66,31,.1); }.stats view text { display: block; font-size: 25rpx; color: #777; }.number { font-size: 52rpx !important; color: #f28b37 !important; font-weight: 800; margin-bottom: 8rpx; }.badge { margin-top: 35rpx; background: #fff0d4; border-radius: 30rpx; padding: 34rpx; }.badge-title { font-size: 32rpx; font-weight: 800; }.badges { display: flex; justify-content: space-around; margin-top: 30rpx; }.badges view { text-align: center; font-size: 76rpx; }.badges text { display: block; margin-top: 8rpx; font-size: 25rpx; }.locked { filter: grayscale(1); opacity: .32; }.clear { margin-top: 52rpx; background: transparent; color: #9a8572; font-size: 27rpx; }
</style>
