import { useState, useRef, useEffect } from 'react';
import api from '../api/client';

function ChatWidget({ assessmentId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendMessage = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg = { role: 'user', content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Build history from previous messages (exclude current)
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await api.post('/ai/chat', {
        assessment_id: assessmentId,
        message: trimmed,
        history,
      });

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.data.reply },
      ]);
    } catch (err) {
      const detail = err.response?.data?.detail || 'AI is unavailable right now.';
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: detail },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!assessmentId) return null;

  return (
    <>
      {/* Toggle Button */}
      <button
        className={`chat-toggle ${isOpen ? 'open' : ''}`}
        id="chat-toggle-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close AI chat' : 'Open AI chat'}
        type="button"
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat Panel */}
      <div className={`chat-panel ${isOpen ? 'open' : ''}`}>
        <div className="chat-panel-header">
          <div className="chat-panel-header-info">
            <span className="chat-panel-avatar">🤖</span>
            <div>
              <h4 className="chat-panel-title">HeartGuard AI</h4>
              <span className="chat-panel-status">
                {loading ? 'Thinking…' : 'Online'}
              </span>
            </div>
          </div>
          <button
            className="chat-panel-close"
            onClick={() => setIsOpen(false)}
            type="button"
            aria-label="Close chat"
          >
            ✕
          </button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-empty">
              <span className="chat-empty-icon">💬</span>
              <p>Ask me anything about your assessment.</p>
              <div className="chat-suggestions">
                {[
                  'What does my risk score mean?',
                  'Which factors are most concerning?',
                  'What lifestyle changes should I prioritize?',
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    className="chat-suggestion-chip"
                    onClick={() => {
                      setInput(suggestion);
                      inputRef.current?.focus();
                    }}
                    type="button"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              className={`chat-message ${msg.role}`}
              key={idx}
            >
              {msg.role === 'assistant' && (
                <span className="chat-message-avatar">🤖</span>
              )}
              <div className="chat-message-bubble">
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <span className="chat-message-avatar">🤖</span>
              <div className="chat-message-bubble typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={sendMessage}>
          <input
            ref={inputRef}
            id="chat-input"
            className="chat-input"
            type="text"
            placeholder="Ask about your results…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            maxLength={2000}
          />
          <button
            type="submit"
            className="chat-send-btn"
            id="chat-send-btn"
            disabled={loading || !input.trim()}
          >
            ↑
          </button>
        </form>
      </div>
    </>
  );
}

export default ChatWidget;
