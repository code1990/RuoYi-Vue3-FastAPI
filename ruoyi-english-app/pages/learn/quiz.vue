<template>
  <view class="page"><view class="content">
    <view class="top"><text>第 {{ index + 1 }} 关</text><text>⭐ {{ stars }}</text></view>
    <view v-if="!finished">
      <view class="question-card"><text class="emoji">{{ question.emoji }}</text><text class="ask">{{ question.ask }}</text></view>
      <view class="answers"><view v-for="(answer, answerIndex) in question.answers" :key="answer" class="answer" :class="answerClass(answerIndex)" @click="choose(answerIndex)">{{ answer }}</view></view>
      <text v-if="message" class="message">{{ message }}</text>
    </view>
    <view v-else class="finish"><text class="finish-icon">🎉</text><text class="finish-title">太厉害啦！</text><text class="finish-text">你完成了今天的英语闯关</text><button @click="restart">再玩一次</button></view>
  </view></view>
</template>
<script>
const questions = [
  { emoji: '🐶', ask: '这是什么？', answers: ['cat', 'dog', 'bird'], correct: 1 },
  { emoji: '🍌', ask: '请选择 banana', answers: ['苹果', '香蕉', '橙子'], correct: 1 },
  { emoji: '🌙', ask: '月亮的英文是？', answers: ['moon', 'sun', 'star'], correct: 0 },
  { emoji: '🚗', ask: '请选择 car', answers: ['汽车', '飞机', '火车'], correct: 0 }
]
export default { data() { return { questions, index: 0, selected: null, message: '', stars: 0, finished: false } }, computed: { question() { return this.questions[this.index] } }, onShow() { const p = uni.getStorageSync('englishGarden_progress') || {}; this.stars = p.stars || 0 }, methods: { answerClass(i) { if (this.selected === null) return ''; if (i === this.question.correct) return 'right'; return i === this.selected ? 'wrong' : '' }, choose(i) { if (this.selected !== null) return; this.selected = i; const ok = i === this.question.correct; this.message = ok ? '答对了，真棒！' : '没关系，再记一次吧！'; if (ok) this.save(); setTimeout(() => { if (this.index === this.questions.length - 1) this.finished = true; else { this.index++; this.selected = null; this.message = '' } }, 900) }, save() { const p = uni.getStorageSync('englishGarden_progress') || { stars: 0, streak: 1, correct: 0 }; p.stars = (p.stars || 0) + 1; p.correct = (p.correct || 0) + 1; uni.setStorageSync('englishGarden_progress', p); this.stars = p.stars }, restart() { this.index = 0; this.selected = null; this.message = ''; this.finished = false } } }
</script>
<style lang="scss" scoped>
.page { min-height: 100vh; padding: 48rpx 0; background: #f2f8ff; }.content { width: 82%; max-width: 900px; margin: auto; }.top { display: flex; justify-content: space-between; font-size: 30rpx; font-weight: 800; color: #4572a8; }.question-card { margin-top: 38rpx; min-height: 390rpx; display: flex; flex-direction: column; justify-content: center; align-items: center; background: white; border-radius: 38rpx; box-shadow: 0 12rpx 32rpx rgba(56,105,156,.12); }.emoji { font-size: 170rpx; }.ask { margin-top: 26rpx; font-size: 40rpx; font-weight: 800; }.answers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22rpx; margin-top: 36rpx; }.answer { min-height: 110rpx; box-sizing: border-box; background: white; border: 4rpx solid #d6e7f9; border-radius: 24rpx; display: flex; align-items: center; justify-content: center; font-size: 32rpx; font-weight: 700; }.answer:active { transform: scale(.97); }.right { background: #dff6e2; border-color: #62bf72; color: #28773a; }.wrong { background: #ffe2df; border-color: #ed796c; color: #aa3d35; }.message { display: block; text-align: center; margin-top: 28rpx; font-size: 33rpx; font-weight: 800; color: #ea7858; }.finish { margin-top: 80rpx; text-align: center; }.finish-icon { display: block; font-size: 180rpx; }.finish-title,.finish-text { display: block; }.finish-title { font-size: 52rpx; font-weight: 800; }.finish-text { margin: 16rpx; font-size: 30rpx; color: #667; }.finish button { margin-top: 35rpx; width: 360rpx; border-radius: 50rpx; background: #5f9fe8; color: white; font-size: 31rpx; }
@media screen and (max-width: 600px) { .answers { grid-template-columns: 1fr; }.question-card { min-height: 300rpx; } }
</style>
