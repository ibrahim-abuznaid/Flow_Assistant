import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

// Use environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [currentInput, setCurrentInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [currentStatus, setCurrentStatus] = useState(null)
  const messagesEndRef = useRef(null)
  const eventSourceRef = useRef(null)

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch stats on mount
  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`)
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const sendMessage = async () => {
    if (!currentInput.trim() || isLoading) return

    const userMessage = currentInput.trim()
    
    // Add user message to UI
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }])
    setCurrentInput('')
    setIsLoading(true)
    setCurrentStatus('🚀 Starting...')

    try {
      // Use EventSource for streaming
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'status') {
                setCurrentStatus(data.message)
              } else if (data.type === 'done') {
                setCurrentStatus(null)
                setMessages(prev => [...prev, { 
                  sender: 'assistant', 
                  text: data.reply 
                }])
              } else if (data.type === 'error') {
                setCurrentStatus(null)
                setMessages(prev => [...prev, { 
                  sender: 'assistant', 
                  text: `Error: ${data.message}` 
                }])
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error)
      
      let errorMessage = 'Sorry, there was an error processing your request.'
      
      if (error.message) {
        errorMessage = `Error: ${error.message}`
      }

      setMessages(prev => [...prev, { 
        sender: 'assistant', 
        text: errorMessage 
      }])
      setCurrentStatus(null)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const resetConversation = async () => {
    if (!window.confirm('Are you sure you want to clear the conversation history?')) {
      return
    }

    try {
      await axios.post(`${API_BASE_URL}/reset`)
      setMessages([])
      alert('Conversation history cleared!')
    } catch (error) {
      console.error('Error resetting conversation:', error)
      alert('Error clearing conversation history')
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🤖 ActivePieces AI Assistant</h1>
          <p className="subtitle">Your intelligent guide to workflow automation</p>
          {stats && (
            <div className="stats">
              <span>{stats.total_pieces} Pieces</span>
              <span>{stats.total_actions} Actions</span>
              <span>{stats.total_triggers} Triggers</span>
            </div>
          )}
        </div>
        <button onClick={resetConversation} className="reset-btn" title="Clear conversation">
          🗑️ Clear
        </button>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>👋 Welcome!</h2>
              <p>I'm your ActivePieces AI assistant. I can help you with:</p>
              <ul>
                <li>Finding integrations, actions, and triggers</li>
                <li>Building workflows and automations</li>
                <li>Understanding ActivePieces features</li>
                <li>Troubleshooting automation challenges</li>
              </ul>
              <p className="prompt">Ask me anything about ActivePieces!</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>
              <div className="message-avatar">
                {msg.sender === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.text}</div>
              </div>
            </div>
          ))}

          {isLoading && (
            <>
              {currentStatus && (
                <div className="status-indicator">
                  <div className="status-icon">
                    <div className="pulse-ring"></div>
                    <div className="pulse-dot"></div>
                  </div>
                  <div className="status-text">{currentStatus}</div>
                </div>
              )}
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <textarea
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me about ActivePieces... (Press Enter to send)"
            disabled={isLoading}
            rows={1}
          />
          <button 
            onClick={sendMessage} 
            disabled={!currentInput.trim() || isLoading}
            className="send-btn"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </div>

      <footer className="footer">
        <p>Powered by OpenAI, LangChain & FastAPI</p>
      </footer>
    </div>
  )
}

export default App

