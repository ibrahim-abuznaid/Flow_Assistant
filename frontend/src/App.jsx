import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import './App.css'

// Code block with copy button component
const CodeBlock = ({ language, children }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(String(children).replace(/\n$/, ''))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="code-block-wrapper">
      <div className="code-block-header">
        <span className="code-language">{language}</span>
        <button onClick={handleCopy} className="copy-button">
          {copied ? '✓ Copied!' : '📋 Copy'}
        </button>
      </div>
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    </div>
  )
}

// Use environment variable or fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Generate a unique session ID
const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

function App() {
  const [messages, setMessages] = useState([])
  const [currentInput, setCurrentInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [currentStatus, setCurrentStatus] = useState(null)
  const [sessionId, setSessionId] = useState(() => generateSessionId())
  const [showSessions, setShowSessions] = useState(false)
  const [previousSessions, setPreviousSessions] = useState([])
  const [selectedSession, setSelectedSession] = useState(null)
  const [buildFlowMode, setBuildFlowMode] = useState(false)
  const messagesEndRef = useRef(null)
  const eventSourceRef = useRef(null)
  const abortControllerRef = useRef(null)

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch stats and sessions on mount
  useEffect(() => {
    fetchStats()
    fetchSessions()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`)
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchSessions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/sessions`)
      setPreviousSessions(response.data.sessions)
    } catch (error) {
      console.error('Error fetching sessions:', error)
    }
  }

  const loadSession = async (sessionIdToLoad) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/sessions/${sessionIdToLoad}`)
      setSelectedSession(response.data)
    } catch (error) {
      console.error('Error loading session:', error)
      alert('Error loading session')
    }
  }

  const closeSessionView = () => {
    setSelectedSession(null)
  }

  const deleteSession = async (sessionIdToDelete) => {
    if (!window.confirm('Are you sure you want to delete this session?')) {
      return
    }

    try {
      await axios.delete(`${API_BASE_URL}/sessions/${sessionIdToDelete}`)
      fetchSessions()
      if (selectedSession?.session_id === sessionIdToDelete) {
        setSelectedSession(null)
      }
      alert('Session deleted!')
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Error deleting session')
    }
  }

  const stopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setIsLoading(false)
      setCurrentStatus(null)
      setMessages(prev => [...prev, { 
        sender: 'assistant', 
        text: '⏸️ Generation stopped by user.' 
      }])
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

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController()

    try {
      // Use EventSource for streaming
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: sessionId,
          build_flow_mode: buildFlowMode
        }),
        signal: abortControllerRef.current.signal
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
      // Check if it was aborted by user
      if (error.name === 'AbortError') {
        console.log('Request aborted by user')
        return // Don't show error message, stopGeneration already handled it
      }

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
      abortControllerRef.current = null
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const resetConversation = async () => {
    if (!window.confirm('Are you sure you want to start a new session?')) {
      return
    }

    // Generate new session ID and clear messages
    setSessionId(generateSessionId())
    setMessages([])
    
    // Refresh sessions list to include the old session
    fetchSessions()
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>🤖 ActivePieces AI Assistant</h1>
          <p className="subtitle">Your intelligent guide to workflow automation</p>
          {stats && (
            <div className="stats">
              <span>{stats.total_pieces.toLocaleString()} Pieces</span>
              <span>{stats.total_actions.toLocaleString()} Actions</span>
              <span>{stats.total_triggers.toLocaleString()} Triggers</span>
            </div>
          )}
        </div>
        <div className="header-actions">
          <button 
            onClick={() => setShowSessions(!showSessions)} 
            className="sessions-btn" 
            title="View previous sessions"
          >
            📋 History ({previousSessions.length})
          </button>
          <button 
            onClick={resetConversation} 
            className="reset-btn" 
            title="Start new session"
          >
            🔄 New Session
          </button>
        </div>
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
                <div className="message-text">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '')
                        return !inline && match ? (
                          <CodeBlock language={match[1]}>
                            {children}
                          </CodeBlock>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        )
                      }
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                </div>
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
                  <button 
                    onClick={stopGeneration} 
                    className="stop-btn"
                    title="Stop generation"
                  >
                    ⏹️ Stop
                  </button>
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
          <div className="input-controls">
            <div className="mode-toggle">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={buildFlowMode}
                  onChange={(e) => setBuildFlowMode(e.target.checked)}
                  disabled={isLoading}
                />
                <span className="toggle-text">
                  🔧 Build Flow Mode {buildFlowMode && '(Active)'}
                </span>
              </label>
              {buildFlowMode && (
                <span className="mode-description">
                  Get comprehensive step-by-step flow building guides
                </span>
              )}
            </div>
          </div>
          <div className="input-box">
            <textarea
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={buildFlowMode ? "Describe the flow you want to build..." : "Ask me about ActivePieces... (Press Enter to send)"}
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
      </div>

      {/* Sessions Panel */}
      {showSessions && (
        <div className="sessions-panel">
          <div className="sessions-header">
            <h3>📋 Previous Sessions</h3>
            <button onClick={() => setShowSessions(false)} className="close-btn">✕</button>
          </div>
          <div className="sessions-list">
            {previousSessions.length === 0 ? (
              <p className="no-sessions">No previous sessions</p>
            ) : (
              previousSessions.map((session) => (
                <div key={session.session_id} className="session-item">
                  <div className="session-info" onClick={() => loadSession(session.session_id)}>
                    <div className="session-preview">{session.preview}...</div>
                    <div className="session-meta">
                      <span>{session.message_count} messages</span>
                      <span>{new Date(session.updated_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteSession(session.session_id)
                    }}
                    className="delete-session-btn"
                    title="Delete session"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Session Viewer Modal */}
      {selectedSession && (
        <div className="modal-overlay" onClick={closeSessionView}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Session Details</h3>
              <button onClick={closeSessionView} className="close-btn">✕</button>
            </div>
            <div className="modal-body">
              <div className="session-messages">
                {selectedSession.messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'assistant'}`}>
                    <div className="message-avatar">
                      {msg.role === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-content">
                      <div className="message-text">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({ node, inline, className, children, ...props }) {
                              const match = /language-(\w+)/.exec(className || '')
                              return !inline && match ? (
                                <CodeBlock language={match[1]}>
                                  {children}
                                </CodeBlock>
                              ) : (
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              )
                            }
                          }}
                        >
                          {msg.message}
                        </ReactMarkdown>
                      </div>
                      <div className="message-time">
                        {new Date(msg.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <footer className="footer">
        <p>Powered by OpenAI, LangChain & FastAPI</p>
      </footer>
    </div>
  )
}

export default App

