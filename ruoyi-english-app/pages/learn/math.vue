<template>
  <view class="page"><view class="content">
    <view class="top"><text>第 {{ index + 1 }} / 10 题</text><text>累计答对 {{ correct }} 题</text></view>
    <view v-if="!finished"><view class="question" :class="feedback"><text>{{ question.left }}</text><text>{{ question.operator }}</text><text>{{ question.right }}</text><text>=</text><view class="result" @click="clearAnswer">{{ answer || '?' }}</view></view>
    <text class="hint">{{ message || '点数字填答案；点答案可清除' }}</text>
    <view v-if="feedback === 'right'" class="celebrate">⭐ 🎉 ⭐</view>
    <view class="keypad"><button v-for="number in numbers" :key="number" @click="input(number)">{{ number }}</button><button class="clear" @click="clearAnswer">清除</button><button class="confirm" @click="confirm">确认</button></view></view>
    <view v-else class="finish"><text>🎉</text><text>完成啦！</text><text>这轮答对 {{ roundCorrect }} / 10 题</text><button @click="restart">再玩一次</button></view>
  </view></view>
</template>

<script>
const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min

export default {
  data() { return { question: {}, answer: '', feedback: '', message: '', correct: 0, index: 0, roundCorrect: 0, finished: false, numbers: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] } },
  onLoad() { this.newQuestion() },
  onShow() { this.correct = (uni.getStorageSync('englishGarden_mathProgress') || {}).correct || 0 },
  methods: {
    newQuestion() {
      const plus = Math.random() < .5
      const right = random(1, 10)
      const left = plus ? random(1, 20 - right) : random(right, 20)
      this.question = { left, right, operator: plus ? '+' : '-', answer: plus ? left + right : left - right }
      this.answer = ''; this.feedback = ''; this.message = ''
    },
    input(number) { if (this.feedback || this.answer.length === 2) return; this.answer = this.answer === '0' ? String(number) : `${this.answer}${number}` },
    clearAnswer() { if (!this.feedback) this.answer = '' },
    confirm() {
      if (this.feedback) return
      if (!this.answer) { this.message = '先选一个答案吧'; return }
      if (Number(this.answer) === this.question.answer) {
        this.feedback = 'right'; this.message = '答对啦，真棒！'; this.save()
        setTimeout(() => { if (this.index === 9) this.finished = true; else { this.index++; this.newQuestion() } }, 1000)
      } else {
        this.feedback = 'wrong'; this.message = '再想一想'; setTimeout(() => { this.feedback = ''; this.message = '' }, 500)
      }
    },
    save() { const progress = uni.getStorageSync('englishGarden_mathProgress') || { correct: 0 }; progress.correct++; uni.setStorageSync('englishGarden_mathProgress', progress); this.correct = progress.correct; this.roundCorrect++ },
    restart() { this.index = 0; this.roundCorrect = 0; this.finished = false; this.newQuestion() }
  }
}
</script>

<style lang="scss" scoped>
.page{min-height:100vh;padding:48rpx 0;background:#f4fbff}.content{position:relative;width:82%;max-width:900px;margin:auto}.top{display:flex;justify-content:space-between;color:#4278aa;font-size:30rpx;font-weight:800}.question{position:relative;min-height:330rpx;margin-top:38rpx;display:flex;align-items:center;justify-content:center;gap:24rpx;border-radius:38rpx;background:#fff;box-shadow:0 12rpx 32rpx rgba(56,105,156,.12);font-size:72rpx;font-weight:800;color:#29475f}.result{min-width:120rpx;padding:12rpx 18rpx;text-align:center;color:#f07a53;border-bottom:8rpx solid #f7bf9e}.hint{display:block;min-height:48rpx;margin-top:24rpx;text-align:center;color:#60788f;font-size:30rpx;font-weight:700}.keypad{display:grid;grid-template-columns:repeat(5,1fr);gap:18rpx;margin-top:28rpx}.keypad button{height:94rpx;line-height:94rpx;border-radius:22rpx;background:#fff;color:#35546e;font-size:38rpx;font-weight:800;box-shadow:0 6rpx 16rpx rgba(56,105,156,.1)}.keypad button:active{transform:scale(.96)}.keypad .clear{grid-column:span 2;background:#ffe9df;color:#ca6249;font-size:30rpx}.keypad .confirm{grid-column:span 3;background:#67bc7b;color:#fff;font-size:32rpx}.celebrate{position:absolute;top:170rpx;left:0;right:0;text-align:center;font-size:70rpx;animation:pop .7s ease-out}.right{border:6rpx solid #70c881}.wrong{animation:shake .45s}.right .result{color:#3b9f54;border-color:#79ce88}.finish{margin-top:90rpx;text-align:center}.finish text{display:block}.finish text:first-child{font-size:160rpx}.finish text:nth-child(2){font-size:54rpx;font-weight:800}.finish text:nth-child(3){margin-top:18rpx;font-size:32rpx;color:#60788f}.finish button{width:320rpx;margin-top:45rpx;border-radius:50rpx;background:#67bc7b;color:#fff;font-size:32rpx}@keyframes pop{50%{transform:scale(1.3) translateY(-25rpx)}}@keyframes shake{25%,75%{transform:translateX(-14rpx)}50%{transform:translateX(14rpx)}}@media screen and (max-width:600px){.content{width:90%}.question{min-height:250rpx;font-size:54rpx;gap:16rpx}.keypad{grid-template-columns:repeat(3,1fr)}.keypad .clear{grid-column:span 1}.keypad .confirm{grid-column:span 2}}
</style>
