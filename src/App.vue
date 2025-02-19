<template>
          <div class="chat-container">
                    <!-- 左侧边栏 -->
                    <div class="sidebar">
                              <div class="logo">
                                        <span class="logo-emoji">🤖</span>
                                        <span>AI Assistant</span>
                              </div>
                              
                              <div class="new-chat" @click="createNewChat">
                                        <i class="plus-icon">+</i>
                                        新建对话
                              </div>

                              <!-- 历史对话列表 -->
                              <div class="history-list">
                                        <div v-for="(chat, index) in chatHistory" :key="index"
                                                  @click="selectChat(index)"
                                                  :class="{ 'active': currentChatIndex === index }"
                                                  class="history-item">
                                                  <i class="chat-icon">💬</i>
                                                  <span class="chat-title">{{ chat.title }}</span>
                                        </div>
                              </div>
                    </div>

                    <!-- 主聊天区域 -->
                    <div class="main-chat">
                              <!-- 顶部导航 -->
                              <div class="chat-header">
                                        <h2>{{ currentChat.title }}</h2>
                                        <div class="actions">
                                                  <button class="clear-btn" @click="clearChat">
                                                            <i class="clear-icon">🗑️</i>
                                                            清空对话
                                                  </button>
                                        </div>
                              </div>

                              <!-- 聊天记录 -->
                              <div class="chat-messages" ref="messageContainer">
                                        <div v-for="(msg, index) in currentChat.messages" :key="index"
                                                  :class="['message', msg.role]">
                                                  <div class="message-container">
                                                            <div class="avatar">
                                                                      <img :src="msg.role === 'user' ? userAvatar : botAvatar">
                                                            </div>
                                                            <div class="message-content">
                                                                      <div class="sender">{{ msg.role === 'user' ? '我' : 'AI助手' }}</div>
                                                                      <div class="content" v-html="formatMessage(msg.content)"></div>
                                                            </div>
                                                  </div>
                                        </div>
                              </div>

                              <!-- 输入框区域 -->
                              <div class="input-area">
                                        <div class="input-container">
                                                  <textarea v-model="userInput" @keyup.enter.exact.prevent="sendMessage" @keyup.enter.shift.exact.prevent="userInput += '\n'" placeholder="输入消息，Enter发送，Shift+Enter换行..." rows="1" ref="inputBox"></textarea>
                                                  <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim()">
                                                            <i class="send-icon">📤</i>
                                                  </button>
                                        </div>
                              </div>
                    </div>
          </div>
</template>

<script>
import axios from 'axios'

export default {
          name: 'App',
          data() {
                    return {
                              userInput: '',
                              currentChatIndex: 0,
                              userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user',
                              botAvatar: 'https://api.dicebear.com/7.x/bottts/svg?seed=bot',
                              chatHistory: [{
                                        title: '新对话',
                                        messages: []
                              }],
                    }
          },
          computed: {
                    currentChat() {
                              return this.chatHistory[this.currentChatIndex]
                    }
          },
          methods: {
                    createNewChat() {
                              this.chatHistory.unshift({
                                        title: '新对话',
                                        messages: []
                              })
                              this.currentChatIndex = 0
                              this.userInput = ''
                    },

                    selectChat(index) {
                              this.currentChatIndex = index
                    },

                    async sendMessage() {
                              if (!this.userInput.trim()) return

                              // 添加用户消息
                              this.currentChat.messages.push({
                                        role: 'user',
                                        content: this.userInput
                              })

                              const userMessage = this.userInput
                              this.userInput = ''

                              // 添加一个空的AI响应消息占位
                              this.currentChat.messages.push({
                                        role: 'assistant',
                                        content: '正在思考...'
                              })

                              try {
                                        await this.getAIResponse(userMessage)
                              } catch (error) {
                                        console.error('获取AI响应失败:', error)
                                        this.currentChat.messages[this.currentChat.messages.length - 1].content = 
                                                  '抱歉，发生了错误，请稍后重试。'
                              }

                              // 更新第一条消息为对话标题
                              if (this.currentChat.messages.length === 2) {
                                        this.currentChat.title = userMessage.slice(0, 20) + '...'
                              }

                              this.$nextTick(() => {
                                        this.scrollToBottom()
                              })
                    },

                    async getAIResponse(message) {
                              try {
                                        const response = await fetch('http://127.0.0.1:5000/api/generate', {
                                                  method: 'POST',
                                                  headers: {
                                                            'Content-Type': 'application/json',
                                                            'Accept': 'text/event-stream'
                                                  },
                                                  credentials: 'include',
                                                  body: JSON.stringify({
                                                            prompt: message
                                                  })
                                        })

                                        if (!response.ok) {
                                                  throw new Error(`HTTP error! status: ${response.status}`);
                                        }

                                        // 创建一个新的 ReadableStream
                                        const reader = response.body.getReader()
                                        let result = ''

                                        while (true) {
                                                  const { done, value } = await reader.read()
                                                  
                                                  if (done) break
                                                  
                                                  // 将 Uint8Array 转换为文本
                                                  const chunk = new TextDecoder().decode(value)
                                                  const lines = chunk.split('\n')
                                                  
                                                  for (const line of lines) {
                                                            if (line.startsWith('data: ')) {
                                                                      try {
                                                                                const data = JSON.parse(line.slice(5))
                                                                                if (data.text) {
                                                                                          result += data.text
                                                                                          // 实时更新消息
                                                                                          this.currentChat.messages[this.currentChat.messages.length - 1] = {
                                                                                                    role: 'assistant',
                                                                                                    content: result
                                                                                          }
                                                                                }
                                                                                if (data.error) {
                                                                                          console.error('AI响应错误:', data.error)
                                                                                          return '抱歉，发生了错误，请稍后重试。'
                                                                                }
                                                                      } catch (e) {
                                                                                console.error('解析响应数据失败:', e)
                                                                      }
                                                            }
                                                  }
                                        }
                                        
                                        return result
                              } catch (error) {
                                        console.error('调用AI API失败:', error)
                                        return '抱歉，发生了错误，请稍后重试。'
                              }
                    },

                    formatMessage(message) {
                              // 可以添加markdown渲染等格式化逻辑
                              return message
                    },

                    scrollToBottom() {
                              const container = this.$refs.messageContainer
                              container.scrollTop = container.scrollHeight
                    },

                    // 添加清空对话方法
                    clearChat() {
                              if(confirm('确定要清空当前对话吗？')) {
                                        this.currentChat.messages = []
                              }
                    }
          },
          mounted() {
          }
}
</script>

<style>
/* 全局样式 */
* {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
}

body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
          line-height: 1.6;
          color: #333;
}

/* 容器样式 */
.chat-container {
          display: flex;
          height: 100vh;
          background: #f7f7f8;
}

/* 侧边栏样式 */
.sidebar {
          width: 260px;
          background: #202123;
          color: #fff;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 16px;
}

.logo {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
}

.logo-emoji {
          font-size: 24px;
          margin-right: 8px;
}

.logo span {
          font-size: 18px;
          font-weight: 600;
}

.new-chat {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          background: #343541;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
}

.new-chat:hover {
          background: #40414f;
}

.plus-icon {
          font-size: 20px;
}

.history-list {
          flex: 1;
          overflow-y: auto;
}

.history-item {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
}

.history-item:hover {
          background: #343541;
}

.history-item.active {
          background: #343541;
}

.chat-icon {
          font-size: 16px;
}

.chat-title {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
}

/* 主聊天区域样式 */
.main-chat {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: #fff;
}

.chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          border-bottom: 1px solid #e5e5e5;
          background: #fff;
}

.chat-header h2 {
          font-size: 18px;
          font-weight: 600;
}

.clear-btn {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 8px 12px;
          border: none;
          background: #f0f0f0;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.3s ease;
}

.clear-btn:hover {
          background: #e5e5e5;
}

.chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
}

.message {
          margin-bottom: 24px;
}

.message-container {
          display: flex;
          gap: 16px;
          max-width: 800px;
          margin: 0 auto;
}

.avatar {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          overflow: hidden;
}

.avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
}

.message-content {
          flex: 1;
}

.sender {
          font-size: 14px;
          color: #666;
          margin-bottom: 4px;
}

.content {
          padding: 12px 16px;
          background: #f7f7f8;
          border-radius: 8px;
          font-size: 15px;
}

.input-area {
          padding: 24px;
          background: #fff;
          border-top: 1px solid #e5e5e5;
}

.input-container {
          display: flex;
          gap: 12px;
          max-width: 800px;
          margin: 0 auto;
}

.input-area textarea {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #e5e5e5;
          border-radius: 8px;
          resize: none;
          font-size: 15px;
          line-height: 1.5;
          transition: all 0.3s ease;
}

.input-area textarea:focus {
          outline: none;
          border-color: #10a37f;
          box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
}

.send-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          border: none;
          background: #10a37f;
          color: #fff;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
}

.send-btn:hover {
          background: #0d8c6d;
}

.send-btn:disabled {
          background: #e5e5e5;
          cursor: not-allowed;
}

/* 滚动条样式 */
::-webkit-scrollbar {
          width: 8px;
}

::-webkit-scrollbar-track {
          background: transparent;
}

::-webkit-scrollbar-thumb {
          background: #c1c1c1;
          border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
          background: #a8a8a8;
}

/* 添加打字机效果 */
.message.assistant .content {
          white-space: pre-wrap;
          animation: typing 0.05s steps(1);
}

@keyframes typing {
          from { opacity: 0.8; }
          to { opacity: 1; }
}
</style>