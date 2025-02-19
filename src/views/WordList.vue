<template>
  <div class="word-list-container">
    <!-- 添加单词表单 -->
    <div class="add-word-form">
      <h2>添加新单词</h2>
      <input v-model="newWord.word" placeholder="请输入单词">
      <input v-model="newWord.translation" placeholder="请输入翻译">
      <button @click="addWord">添加</button>
    </div>

    <!-- 单词列表 -->
    <div class="words-table">
      <h2>单词列表</h2>
      <table>
        <thead>
          <tr>
            <th>单词</th>
            <th>翻译</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="word in words" :key="word.id">
            <td>{{ word.word }}</td>
            <td>{{ word.translation }}</td>
            <td>
              <button @click="deleteWord(word.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      words: [],
      newWord: {
        word: '',
        translation: ''
      }
    }
  },
  methods: {
    // 获取所有单词
    async fetchWords() {
      try {
        const response = await axios.get('http://localhost:3000/api/words')
        this.words = response.data
      } catch (error) {
        console.error('获取单词失败:', error)
      }
    },
    // 添加新单词
    async addWord() {
      try {
        await axios.post('http://localhost:3000/api/words', this.newWord)
        this.newWord.word = ''
        this.newWord.translation = ''
        await this.fetchWords()
      } catch (error) {
        console.error('添加单词失败:', error)
      }
    },
    // 删除单词
    async deleteWord(id) {
      try {
        await axios.delete(`http://localhost:3000/api/words/${id}`)
        await this.fetchWords()
      } catch (error) {
        console.error('删除单词失败:', error)
      }
    }
  },
  mounted() {
    this.fetchWords()
  }
}
</script>

<style scoped>
.word-list-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.add-word-form {
  margin-bottom: 30px;
}

.add-word-form input {
  margin-right: 10px;
  padding: 8px;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
}
</style> 