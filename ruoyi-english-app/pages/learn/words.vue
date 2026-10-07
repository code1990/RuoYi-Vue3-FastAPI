<template>
  <view class="page"><view class="content">
    <view class="progress"><text>第 {{ index + 1 }} / {{ words.length }} 个单词</text><view class="bar"><view :style="{ width: ((index + 1) / words.length * 100) + '%' }"></view></view></view>
    <view class="word-card" @click="speak(current.word)"><text class="emoji">{{ current.emoji }}</text><text class="word">{{ current.word }}</text><text class="sound">🔊 点我听一听</text><text class="meaning">{{ current.meaning }}</text></view>
    <view class="example"><text class="example-title">跟着读</text><text>{{ current.sentence }}</text></view>
    <view class="actions"><button class="known" @click="next">我会啦 ✓</button><button class="next" @click="next">下一个 →</button></view>
  </view></view>
</template>
<script>
const words = [
  { word: 'apple', meaning: '苹果', emoji: '🍎', sentence: 'I like apples.' },
  { word: 'cat', meaning: '小猫', emoji: '🐱', sentence: 'The cat is cute.' },
  { word: 'sun', meaning: '太阳', emoji: '☀️', sentence: 'The sun is bright.' },
  { word: 'book', meaning: '书', emoji: '📚', sentence: 'This is my book.' },
  { word: 'happy', meaning: '开心', emoji: '😊', sentence: 'I am happy today.' }
]
export default { data() { return { words, index: 0 } }, computed: { current() { return this.words[this.index] } }, methods: { speak(text) { if (typeof speechSynthesis !== 'undefined') { speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance(text)) } else { uni.showToast({ title: text + '（请跟着读）', icon: 'none' }) } }, next() { if (this.index < this.words.length - 1) this.index++; else { uni.showToast({ title: '真棒！学完啦', icon: 'success' }); this.addStar() } }, addStar() { const p = uni.getStorageSync('englishGarden_progress') || { stars: 0, streak: 1, correct: 0 }; p.stars = (p.stars || 0) + 1; uni.setStorageSync('englishGarden_progress', p) } } }
</script>
<style lang="scss" scoped>
.page { min-height: 100vh; padding: 45rpx 0; background: #fff9ed; }.content { width: 82%; max-width: 900px; margin: auto; }.progress { font-size: 26rpx; color: #777; }.bar { height: 16rpx; margin-top: 16rpx; background: #f0dfca; border-radius: 10rpx; overflow: hidden; }.bar view { height: 100%; background: #ff9b55; border-radius: inherit; transition: width .3s; }.word-card { margin-top: 44rpx; padding: 60rpx 30rpx; text-align: center; border-radius: 36rpx; background: #fff; box-shadow: 0 12rpx 30rpx rgba(86,55,15,.12); }.emoji { font-size: 150rpx; display: block; }.word { display: block; margin-top: 20rpx; font-size: 68rpx; font-weight: 800; color: #ff7c55; }.sound { display: block; margin-top: 18rpx; font-size: 27rpx; color: #778; }.meaning { display: block; margin-top: 24rpx; font-size: 34rpx; font-weight: 700; }.example { margin-top: 30rpx; background: #fff0d9; padding: 27rpx 34rpx; border-radius: 24rpx; font-size: 30rpx; }.example-title { font-weight: 800; margin-right: 22rpx; }.actions { margin-top: 38rpx; display: flex; gap: 25rpx; }.actions button { flex: 1; font-size: 31rpx; border-radius: 52rpx; }.known { color: #4a9c61; background: #e0f6e4; }.next { color: white; background: #ff805b; }
</style>
