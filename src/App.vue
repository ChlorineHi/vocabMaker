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
                                                  <div class="message-container" :data-time="formatTime(msg.timestamp)">
                                                            <div class="avatar">
                                                                      <img :src="msg.role === 'user' ? userAvatar : botAvatar">
                                                            </div>
                                                            <div class="message-content">
                                                                      <div class="sender">{{ msg.role === 'user' ? '我' : 'AI助手' }}</div>
                                                                      <div class="content" 
                                                                                v-html="formatMessage(msg.content)"
                                                                                :class="{ 'streaming': isStreaming && index === currentChat.messages.length - 1 }">
                                                                      </div>
                                                            </div>

                                                            <!-- 添加消息操作按钮 -->
                                                            <div class="message-actions">
                                                                      <button class="action-button" title="复制">
                                                                                <i class="copy-icon">📋</i>
                                                                      </button>
                                                                      <button class="action-button" title="分享">
                                                                                <i class="share-icon">↗️</i>
                                                                      </button>
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
                              streamingMessage: '',
                              isStreaming: false,
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

                                        const reader = response.body.getReader();
                                        let result = '';
                                        this.isStreaming = true;
                                        this.streamingMessage = '';

                                        while (true) {
                                                  const { done, value } = await reader.read();
                                                  
                                                  if (done) break;
                                                  
                                                  const chunk = new TextDecoder().decode(value);
                                                  const lines = chunk.split('\n');
                                                  
                                                  for (const line of lines) {
                                                            if (line.startsWith('data: ')) {
                                                                      try {
                                                                                const data = JSON.parse(line.slice(5));
                                                                                if (data.text) {
                                                                                          result += data.text;
                                                                                          // 直接调用打字机效果
                                                                                          await this.typeWriter(data.text);
                                                                                }
                                                                                if (data.error) {
                                                                                          console.error('AI响应错误:', data.error);
                                                                                          return '抱歉，发生了错误，请稍后重试。';
                                                                                }
                                                                      } catch (e) {
                                                                                console.error('解析响应数据失败:', e);
                                                                      }
                                                            }
                                                  }
                                        }
                                        
                                        this.isStreaming = false;
                                        return result;
                              } catch (error) {
                                        console.error('调用AI API失败:', error);
                                        this.isStreaming = false;
                                        return '抱歉，发生了错误，请稍后重试。';
                              }
                    },

                    async typeWriter(text) {
                              // 将文本分割成字符数组
                              const chars = Array.from(text);
                              
                              for (const char of chars) {
                                        this.streamingMessage += char;
                                        // 实时更新消息
                                        this.currentChat.messages[this.currentChat.messages.length - 1] = {
                                                  role: 'assistant',
                                                  content: this.streamingMessage
                                        };
                                        // 添加延迟，创建打字效果
                                        await new Promise(resolve => setTimeout(resolve, 20));
                                        // 自动滚动到底部
                                        await this.$nextTick();
                                        this.scrollToBottom();
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
                    },

                    formatTime(timestamp) {
                              if (!timestamp) return '';
                              const date = new Date(timestamp);
                              return date.toLocaleTimeString('zh-CN', {
                                        hour: '2-digit',
                                        minute: '2-digit'
                              });
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
          background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%);
}

/* 侧边栏样式 */
.sidebar {
          width: 280px;
          background: linear-gradient(180deg, #1a1c2d 0%, #2c2e3e 100%);
          color: #fff;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 20px;
          box-shadow: 4px 0 15px rgba(0, 0, 0, 0.1);
}

.logo {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 15px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          backdrop-filter: blur(10px);
}

.logo-emoji {
          font-size: 28px;
          filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));
}

.logo span {
          font-size: 18px;
          font-weight: 600;
}

.new-chat {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 14px;
          background: rgba(255, 255, 255, 0.08);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          border: 1px solid rgba(255, 255, 255, 0.1);
}

.new-chat:hover {
          background: rgba(255, 255, 255, 0.12);
          transform: translateY(-1px);
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
          padding: 30px;
          scroll-behavior: smooth;
          background: linear-gradient(to bottom, rgba(246, 249, 252, 0.8), rgba(255, 255, 255, 0.8));
}

.message {
          margin-bottom: 32px;
          opacity: 1;
          transform: none;
}

.message-container {
          display: flex;
          gap: 20px;
          max-width: 900px;
          margin-left: 24px;
          padding: 5px 0;
          position: relative;
}

.avatar {
          width: 45px;
          height: 45px;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
          transition: all 0.3s ease;
          position: relative;
}

.avatar::after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.3));
          opacity: 0;
          transition: opacity 0.3s ease;
}

.avatar:hover {
          transform: scale(1.05) translateY(-2px);
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.avatar:hover::after {
          opacity: 1;
}

.avatar img {
          width: 100%;
          height: 100%;
          object-fit: cover;
}

.message-content {
          flex: 1;
          position: relative;
          max-width: 80%;
}

.sender {
          font-size: 14px;
          font-weight: 500;
          color: #666;
          margin-bottom: 6px;
          opacity: 0.8;
          transition: opacity 0.3s ease;
}

.message:hover .sender {
          opacity: 1;
}

.content {
          padding: 18px 24px;
          border-radius: 16px;
          font-size: 15px;
          line-height: 1.6;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;
}

.message.user .content {
          background: linear-gradient(135deg, #10a37f 0%, #0d8c6d 100%);
          color: white;
          box-shadow: 0 4px 15px rgba(16, 163, 127, 0.2);
          margin-right: auto;
          margin-left: 0;
}

.message.user .content::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
          opacity: 0;
          transition: opacity 0.3s ease;
}

.message.user .content:hover::before {
          opacity: 1;
}

.message.assistant .content {
          background: white;
          border: 1px solid rgba(0, 0, 0, 0.08);
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
          margin-left: 0;
          margin-right: auto;
          white-space: pre-wrap;
          position: relative;
          padding-right: 8px;
}

.message.assistant .content::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(45deg, rgba(16, 163, 127, 0.03), transparent);
          opacity: 0;
          transition: opacity 0.3s ease;
}

.message.assistant .content:hover::before {
          opacity: 1;
}

/* 添加打字机光标效果 */
.message.assistant .content.streaming::after {
          content: '|';
          position: absolute;
          right: 0;
          bottom: 2px;
          color: #10a37f;
          font-weight: 400;
          animation: cursor-blink 0.8s infinite;
          height: 20px;
          line-height: 20px;
}

@keyframes cursor-blink {
          0%, 100% { opacity: 0; }
          50% { opacity: 1; }
}

/* 移除之前的打字机动画 */
.message.assistant .content {
          animation: none;
}

/* 添加消息出现的渐变效果 */
.message {
          opacity: 1;
          transform: none;
}

.message-container::after {
          content: attr(data-time);
          position: absolute;
          bottom: -20px;
          font-size: 12px;
          color: #999;
          opacity: 0;
          transition: opacity 0.3s ease;
}

.message:hover .message-container::after {
          opacity: 1;
}

.message-actions {
          position: absolute;
          right: -40px;
          top: 50%;
          transform: translateY(-50%);
          opacity: 0;
          transition: all 0.3s ease;
          display: flex;
          flex-direction: row;
          gap: 4px;
          background: rgba(255, 255, 255, 0.9);
          padding: 4px;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message:hover .message-actions {
          opacity: 1;
          right: 10px;
          transform: translateY(-50%);
}

.action-button {
          width: 28px;
          height: 28px;
          border-radius: 6px;
          border: none;
          background: transparent;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
          color: #666;
}

.action-button:hover {
          transform: translateY(-1px);
          background: rgba(0, 0, 0, 0.05);
          color: #10a37f;
}

.message.user .message-actions {
          background: rgba(255, 255, 255, 0.9);
}

.message.user .action-button {
          color: rgba(255, 255, 255, 0.9);
}

.message.user .action-button:hover {
          background: rgba(255, 255, 255, 0.2);
          color: white;
}

.input-area {
          padding: 30px;
          background: rgba(255, 255, 255, 0.8);
          backdrop-filter: blur(10px);
          border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.input-container {
          display: flex;
          gap: 15px;
          max-width: 900px;
          margin: 0 auto;
}

.input-area textarea {
          flex: 1;
          padding: 16px 20px;
          border: 1px solid rgba(0, 0, 0, 0.1);
          border-radius: 12px;
          resize: none;
          font-size: 15px;
          line-height: 1.6;
          transition: all 0.3s ease;
          background: white;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.input-area textarea:focus {
          outline: none;
          border-color: #10a37f;
          box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.15);
}

.send-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 50px;
          height: 50px;
          border: none;
          background: linear-gradient(135deg, #10a37f 0%, #0d8c6d 100%);
          color: #fff;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 15px rgba(16, 163, 127, 0.2);
}

.send-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(16, 163, 127, 0.3);
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
          animation: typing 0.05s steps(1), fadeIn 0.5s ease;
}

@keyframes typing {
          from { opacity: 0.8; }
          to { opacity: 1; }
}

@keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
}
</style>