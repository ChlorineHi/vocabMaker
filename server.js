const express = require('express')
const cors = require('cors')
const app = express()

// 启用 CORS 和 JSON 解析
app.use(cors())
app.use(express.json())

// 模拟数据库
let words = []

// 获取所有单词
app.get('/words', (req, res) => {
  res.json(words)
})

// 添加新单词
app.post('/words', (req, res) => {
  const { word, meaning } = req.body
  const newWord = {
    id: Date.now(),
    word,
    meaning
  }
  words.push(newWord)
  res.json(newWord)
})

// 启动服务器
app.listen(3000, () => {
  console.log('服务器运行在 http://localhost:3000')
}) 