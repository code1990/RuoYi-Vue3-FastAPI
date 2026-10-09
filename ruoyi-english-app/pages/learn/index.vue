<template>
  <view class="page">
    <view class="hero">
      <view>
        <text class="hello">你好，小小英语家！</text>
        <text class="subtitle">今天也来认识几个新朋友吧</text>
      </view>
      <text class="mascot">🦊</text>
    </view>

    <view class="content">
      <view class="streak-card">
        <view><text class="streak-title">连续学习 {{ streak }} 天</text><text class="streak-note">每学习一次，就会点亮一颗星星</text></view>
        <text class="stars">{{ stars }} ⭐</text>
      </view>

      <text class="section-title">今天玩什么？</text>
      <view class="activity-grid">
        <view class="activity purple" @click="go('/pages/learn/scenes')">
          <text class="activity-icon">🗺️</text><text class="activity-title">场景探险</text><text class="activity-desc">去海洋馆和花园玩</text>
        </view>
        <view class="activity orange" @click="go('/pages/learn/words')">
          <text class="activity-icon">🔤</text><text class="activity-title">单词小课堂</text><text class="activity-desc">听一听，说一说</text>
        </view>
        <view class="activity blue" @click="go('/pages/learn/quiz')">
          <text class="activity-icon">🎯</text><text class="activity-title">闯关小游戏</text><text class="activity-desc">选出正确答案</text>
        </view>
        <view class="activity green" @click="go('/pages/learn/progress')">
          <text class="activity-icon">🏆</text><text class="activity-title">我的成长</text><text class="activity-desc">看看收集的星星</text>
        </view>
      </view>

      <view class="tip"><text>💡 </text><text>小提示：点一下英文单词，可以听到它的读音哦！</text></view>
    </view>
  </view>
</template>

<script>
export default {
  data() { return { stars: 0, streak: 1 } },
  onShow() { const p = uni.getStorageSync('englishGarden_progress') || {}; this.stars = p.stars || 0; this.streak = p.streak || 1 },
  methods: { go(url) { uni.navigateTo({ url }) } }
}
</script>

<style lang="scss" scoped>
.page { min-height: 100vh; background: #fff9ed; }
.hero { min-height: 290rpx; padding: 86rpx 9% 48rpx; background: linear-gradient(125deg, #ffbf69, #ff855f); color: #fff; display: flex; align-items: center; justify-content: space-between; }
.hello { font-size: 52rpx; font-weight: 800; display: block; }.subtitle { margin-top: 16rpx; display: block; font-size: 28rpx; opacity: .94; }.mascot { font-size: 150rpx; }
.content { width: 86%; max-width: 1100px; margin: -24rpx auto 60rpx; }.streak-card { background: #fff; border-radius: 28rpx; padding: 30rpx 36rpx; box-shadow: 0 12rpx 32rpx rgba(103,72,29,.12); display: flex; align-items: center; justify-content: space-between; }.streak-title,.streak-note { display: block; }.streak-title { font-size: 33rpx; font-weight: 700; }.streak-note { font-size: 24rpx; color: #888; margin-top: 8rpx; }.stars { font-size: 35rpx; font-weight: 700; color: #f89b2e; }
.section-title { display: block; font-size: 38rpx; font-weight: 800; margin: 54rpx 0 24rpx; }.activity-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24rpx; }.activity { min-height: 260rpx; border-radius: 30rpx; padding: 35rpx; box-sizing: border-box; display: flex; flex-direction: column; box-shadow: 0 10rpx 20rpx rgba(91,65,34,.08); }.activity:active { transform: scale(.98); }.activity-icon { font-size: 76rpx; }.activity-title { margin-top: 24rpx; font-size: 32rpx; font-weight: 800; }.activity-desc { margin-top: 10rpx; font-size: 25rpx; color: #64616b; }.orange { background: #ffe0b0; }.blue { background: #d8edff; }.green { background: #dff5dc; }.purple{background:#eadfff}.tip { margin-top: 42rpx; background: #fff; border-radius: 22rpx; padding: 25rpx 30rpx; font-size: 26rpx; color: #64616b; }
@media screen and (max-width: 600px) { .activity-grid { grid-template-columns: 1fr; }.activity { min-height: 190rpx; }.mascot { font-size: 110rpx; } }
</style>
