import React, { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  codeSuggestions?: string[];
  tips?: string[];
  nextSteps?: string[];
}

interface PortfolioChatProps {
  sessionId: string;
  resumeData: any;
  onCopyCode?: (code: string) => void;
}

const PortfolioChat: React.FC<PortfolioChatProps> = ({ sessionId, resumeData, onCopyCode }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'quick-tips'>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize chat session
  useEffect(() => {
    initializeChat();
  }, [sessionId]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const initializeChat = async () => {
    try {
      const response = await api.post('/api/chat/portfolio/initialize', { 
        session_id: sessionId, 
        user_data: resumeData 
      });

      if (response.status === 200) {
        const data = response.data;
        const assistantMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: data.message,
          timestamp: new Date()
        };
        setMessages([assistantMessage]);
        setInitialized(true);
      }
    } catch (error) {
      console.error('Chat initialization error:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/api/chat/portfolio/improve', {
        session_id: sessionId,
        message: input,
        user_data: resumeData
      });

      if (response.status === 200) {
        const data = response.data;
        const assistantMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          codeSuggestions: data.code_suggestions,
          tips: data.design_tips,
          nextSteps: data.next_steps
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getQuickTips = async () => {
    setLoading(true);
    try {
      const response = await api.post('/api/chat/portfolio/quick-tips', {
        session_id: sessionId,
        user_data: resumeData
      });

      if (response.status === 200) {
        const data = response.data;
        const tipMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: data.tips || 'Loading quick tips...',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, tipMessage]);
      }
    } catch (error) {
      console.error('Error fetching tips:', error);
    } finally {
      setLoading(false);
    }
  };

  const focusAreas = ['Hero Section', 'Colors & Typography', 'Animations', 'Responsiveness', 'Layout'];

  const handleFocusArea = async (area: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: `Help me improve my ${area}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    setLoading(true);
    try {
      const response = await api.post('/api/chat/portfolio/focus-suggestions', {
        session_id: sessionId,
        focus_area: area
      });

      if (response.status === 200) {
        const data = response.data;
        const assistantMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: data.suggestions,
          timestamp: new Date(),
          codeSuggestions: data.code_snippets
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error getting suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="portfolio-chat">
      <style jsx>{`
        .portfolio-chat {
          display: flex;
          flex-direction: column;
          height: 100%;
          background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
          border-radius: 16px;
          border: 1px solid rgba(102, 126, 234, 0.2);
          overflow: hidden;
        }

        .chat-header {
          padding: 1.5rem;
          background: rgba(102, 126, 234, 0.1);
          border-bottom: 1px solid rgba(102, 126, 234, 0.2);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chat-title {
          font-size: 1.3rem;
          font-weight: 700;
          background: linear-gradient(135deg, #667eea, #00d4ff);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .chat-tabs {
          display: flex;
          gap: 1rem;
        }

        .chat-tab {
          background: none;
          border: none;
          color: rgba(255, 255, 255, 0.6);
          cursor: pointer;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          font-weight: 600;
          transition: all 0.3s;
        }

        .chat-tab.active {
          background: rgba(102, 126, 234, 0.2);
          color: #667eea;
        }

        .chat-tab:hover {
          color: #667eea;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .message {
          display: flex;
          gap: 1rem;
          animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .message.user {
          justify-content: flex-end;
        }

        .message-bubble {
          max-width: 75%;
          padding: 1rem;
          border-radius: 12px;
          word-wrap: break-word;
        }

        .message.assistant .message-bubble {
          background: rgba(102, 126, 234, 0.15);
          border: 1px solid rgba(102, 126, 234, 0.3);
          color: rgba(255, 255, 255, 0.9);
        }

        .message.user .message-bubble {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
        }

        .code-suggestion {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(102, 126, 234, 0.3);
          border-radius: 8px;
          padding: 1rem;
          margin-top: 0.5rem;
          font-family: 'Courier New', monospace;
          font-size: 0.85rem;
          overflow-x: auto;
          position: relative;
        }

        .code-copy-btn {
          position: absolute;
          top: 0.5rem;
          right: 0.5rem;
          background: #667eea;
          border: none;
          color: white;
          padding: 0.4rem 0.8rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.8rem;
          transition: all 0.3s;
        }

        .code-copy-btn:hover {
          background: #764ba2;
        }

        .tips-list {
          list-style: none;
          padding: 0;
          margin-top: 0.5rem;
        }

        .tips-list li {
          padding: 0.5rem 0;
          color: rgba(255, 255, 255, 0.8);
        }

        .tips-list li::before {
          content: '✨ ';
          color: #667eea;
          margin-right: 0.5rem;
        }

        .focus-areas {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 0.8rem;
          margin-top: 1rem;
        }

        .focus-btn {
          background: rgba(102, 126, 234, 0.2);
          border: 1px solid rgba(102, 126, 234, 0.3);
          color: #667eea;
          padding: 0.6rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s;
          font-size: 0.85rem;
        }

        .focus-btn:hover {
          background: rgba(102, 126, 234, 0.3);
          border-color: #667eea;
        }

        .input-container {
          padding: 1.5rem;
          border-top: 1px solid rgba(102, 126, 234, 0.2);
          background: rgba(15, 15, 30, 0.5);
        }

        .input-wrapper {
          display: flex;
          gap: 0.8rem;
        }

        .chat-input {
          flex: 1;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(102, 126, 234, 0.3);
          border-radius: 8px;
          padding: 0.8rem;
          color: white;
          font-size: 0.95rem;
          transition: all 0.3s;
        }

        .chat-input:focus {
          outline: none;
          border-color: #667eea;
          background: rgba(255, 255, 255, 0.08);
          box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
        }

        .chat-input::placeholder {
          color: rgba(255, 255, 255, 0.4);
        }

        .send-btn {
          background: linear-gradient(135deg, #667eea, #764ba2);
          border: none;
          color: white;
          padding: 0.8rem 1.5rem;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 700;
          transition: all 0.3s;
        }

        .send-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }

        .send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading-indicator {
          display: flex;
          gap: 0.4rem;
          align-items: center;
        }

        .loading-dot {
          width: 8px;
          height: 8px;
          background: #667eea;
          border-radius: 50%;
          animation: pulse 1.5s ease-in-out infinite;
        }

        .loading-dot:nth-child(2) {
          animation-delay: 0.2s;
        }

        .loading-dot:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 1;
            transform: scale(1.2);
          }
        }

        .tips-button {
          background: rgba(0, 212, 255, 0.2);
          border: 1px solid rgba(0, 212, 255, 0.3);
          color: #00d4ff;
          padding: 0.6rem 1rem;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s;
          font-size: 0.85rem;
        }

        .tips-button:hover {
          background: rgba(0, 212, 255, 0.3);
          border-color: #00d4ff;
        }

        @media (max-width: 768px) {
          .portfolio-chat {
            height: 100%;
            border-radius: 12px;
          }

          .chat-header {
            padding: 1rem;
            flex-wrap: wrap;
            gap: 1rem;
          }

          .chat-title {
            font-size: 1.1rem;
            flex: 0 0 100%;
          }

          .chat-tabs {
            flex: 0 0 100%;
            gap: 0.5rem;
          }

          .chat-tab {
            padding: 0.4rem 0.8rem;
            font-size: 0.85rem;
          }

          .messages-container {
            padding: 1rem;
            gap: 0.8rem;
          }

          .message-bubble {
            max-width: 90%;
            padding: 0.8rem;
            font-size: 0.9rem;
          }

          .code-suggestion {
            padding: 0.8rem;
            margin-top: 0.5rem;
            font-size: 0.75rem;
            max-width: 100%;
            overflow-x: auto;
          }

          .code-copy-btn {
            padding: 0.3rem 0.6rem;
            font-size: 0.7rem;
          }

          .focus-areas {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
          }

          .focus-btn {
            padding: 0.5rem 0.8rem;
            font-size: 0.75rem;
          }

          .input-container {
            padding: 1rem;
          }

          .input-wrapper {
            gap: 0.5rem;
            flex-wrap: wrap;
          }

          .chat-input {
            flex: 1;
            min-width: 200px;
            padding: 0.7rem;
            font-size: 0.9rem;
          }

          .send-btn {
            padding: 0.7rem 1rem;
            font-size: 0.9rem;
            white-space: nowrap;
          }

          .tips-button {
            padding: 0.5rem 0.8rem;
            font-size: 0.75rem;
          }
        }

        @media (max-width: 480px) {
          .portfolio-chat {
            border-radius: 8px;
          }

          .chat-header {
            padding: 0.8rem;
          }

          .chat-title {
            font-size: 1rem;
          }

          .messages-container {
            padding: 0.8rem;
            gap: 0.6rem;
          }

          .message-bubble {
            padding: 0.6rem;
            font-size: 0.85rem;
          }

          .focus-areas {
            grid-template-columns: 1fr;
          }

          .input-wrapper {
            flex-direction: column;
          }

          .chat-input,
          .send-btn {
            width: 100%;
          }

          .tips-list {
            font-size: 0.8rem;
          }
        }
      `}</style>

      <div className="chat-header">
        <div className="chat-title">✨ Portfolio AI Assistant</div>
        <div className="chat-tabs">
          <button
            className={`chat-tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            Chat
          </button>
          <button
            className={`chat-tab ${activeTab === 'quick-tips' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('quick-tips');
              getQuickTips();
            }}
          >
            Quick Tips
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-bubble">
              <p>{msg.content}</p>

              {msg.tips && msg.tips.length > 0 && (
                <ul className="tips-list">
                  {msg.tips.map((tip, idx) => (
                    <li key={idx}>{tip}</li>
                  ))}
                </ul>
              )}

              {msg.codeSuggestions && msg.codeSuggestions.length > 0 && (
                <div className="code-suggestion">
                  <button
                    className="code-copy-btn"
                    onClick={() => {
                      navigator.clipboard.writeText(msg.codeSuggestions![0]);
                      alert('Code copied to clipboard!');
                    }}
                  >
                    Copy
                  </button>
                  <pre>{msg.codeSuggestions[0]}</pre>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message">
            <div className="message-bubble">
              <div className="loading-indicator">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            </div>
          </div>
        )}

        {messages.length === 1 && activeTab === 'chat' && (
          <div className="message">
            <div className="message-bubble">
              <p style={{ marginBottom: '1rem' }}>
                I can help you improve specific areas of your portfolio. Click on a focus area or describe what you'd like to change:
              </p>
              <div className="focus-areas">
                {focusAreas.map(area => (
                  <button
                    key={area}
                    className="focus-btn"
                    onClick={() => handleFocusArea(area)}
                  >
                    {area}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {activeTab === 'chat' && (
        <div className="input-container">
          <div className="input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask me anything about your portfolio design..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => {
                if (e.key === 'Enter' && !loading) {
                  sendMessage();
                }
              }}
              disabled={loading}
            />
            <button
              className="send-btn"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioChat;
