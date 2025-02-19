const express = require('express')
const cors = require('cors')
const app = express()

// 中间件
app.use(cors())
app.use(express.json())

// 模拟数据库
let words = [
          { id: 1, word: 'hello', translation: '你好' },
          { id: 2, word: 'world', translation: '世界' }
]

// 获取所有单词
app.get('/api/words', (req, res) => {
          res.json(words)
})

// 添加新单词
app.post('/api/words', (req, res) => {
          const { word, translation } = req.body
          const newWord = {
                    id: Date.now(), // 使用时间戳作为简单的ID
                    word,
                    translation
          }
          words.push(newWord)
          res.status(201).json(newWord)
})

// 删除单词
app.delete('/api/words/:id', (req, res) => {
          const id = parseInt(req.params.id)
          words = words.filter(word => word.id !== id)
          res.status(200).json({ message: '删除成功' })
})

// 启动服务器
const PORT = 3000
app.listen(PORT, () => {
          console.log(`服务器运行在 http://localhost:${PORT}`)
}) 