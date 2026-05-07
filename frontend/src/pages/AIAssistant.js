import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { aiAssistantService } from '../services/ai';
import '../App.css';

function AIAssistant({ onLogout }) {
  const navigate = useNavigate();
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    try {
      setLoading(true);
      setError('');
      const result = await aiAssistantService.askAssistant(question);
      setResponse(result);
      setConversationHistory([
        ...conversationHistory,
        { question, response: result },
      ]);
      setQuestion('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get response from AI');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="page">
      <nav className="nav-bar">
        <h1>AI Assistant</h1>
        <ul className="nav-links">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/cases">Cases</Link></li>
          <li><Link to="/deadlines">Deadlines</Link></li>
          <li><Link to="/ai-assistant">AI Assistant</Link></li>
          <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
        </ul>
      </nav>

      <div className="container">
        <h2>AI Legal Assistant</h2>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Instructions */}
        <div className="card">
          <h3>How to Ask</h3>
          <p>Ask about your legal cases, clients, and deadlines. Examples:</p>
          <ul>
            <li><strong>Case Duration:</strong> "How long has this case been going?" or "Case duration for CASE-2024-0012"</li>
            <li><strong>Client Cases:</strong> "How many cases do we have from Ahmed?" or "Cases from this client"</li>
            <li><strong>Deadline Status:</strong> "Has this case reached the deadline?" or "When is the deadline for CASE-2024-0012?"</li>
          </ul>
        </div>

        {/* Query Form */}
        <div className="card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="question">Your Question</label>
              <textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about cases, deadlines, or clients..."
                rows="4"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !question.trim()}
            >
              {loading ? 'Processing...' : 'Ask AI'}
            </button>
          </form>
        </div>

        {/* Response */}
        {response && (
          <div className="card">
            <h3>Response</h3>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Query Type:</strong>
              <p>{response.query_type}</p>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <strong>Answer:</strong>
              <p style={{ whiteSpace: 'pre-wrap', backgroundColor: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
                {response.answer}
              </p>
            </div>

            {response.data && Object.keys(response.data).length > 0 && (
              <div>
                <strong>Data Details:</strong>
                <pre style={{ backgroundColor: '#f5f5f5', padding: '1rem', borderRadius: '4px', overflow: 'auto', marginTop: '0.5rem' }}>
                  {JSON.stringify(response.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Conversation History */}
        {conversationHistory.length > 0 && (
          <div className="card">
            <h3>Conversation History</h3>
            {conversationHistory.map((item, idx) => (
              <div key={idx} style={{ marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid #ecf0f1' }}>
                <div style={{ backgroundColor: '#e3f2fd', padding: '1rem', borderRadius: '4px', marginBottom: '0.5rem' }}>
                  <strong>Q:</strong> {item.question}
                </div>
                <div style={{ backgroundColor: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
                  <strong>A:</strong>
                  <p style={{ whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>{item.response.answer}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AIAssistant;
