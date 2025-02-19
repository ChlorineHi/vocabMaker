import { createStore } from 'vuex'

export default createStore({
  state: {
    chatHistory: [],
    currentChatIndex: 0
  },
  mutations: {
    ADD_CHAT(state, chat) {
      state.chatHistory.unshift(chat)
    },
    SET_CURRENT_CHAT(state, index) {
      state.currentChatIndex = index
    },
    ADD_MESSAGE(state, { chatIndex, message }) {
      state.chatHistory[chatIndex].messages.push(message)
    }
  }
}) 