import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { 
  ScanSearch, 
  MessageSquareText, 
  Sparkles, 
  History, 
  Send, 
  Loader2,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import './App.css';

function App() {
  const [productName, setProductName] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const resultRef = useRef(null);

  useEffect(() => { fetchReviews(); }, []);

  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [result]);

  const fetchReviews = async () => {
    try {
      const res = await axios.get('http://localhost:6543/api/reviews');
      setHistory(res.data);
    } catch (err) { console.error(err); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!productName || !reviewText) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post('http://localhost:6543/api/analyze-review', {
        product_name: productName, review_text: reviewText
      });
      setResult(response.data);
      fetchReviews();
    } catch (err) { alert("Failed to analyze. Check backend connection."); }
    finally { setLoading(false); }
  };

  return (
    <div className="web-wrapper">
      
      {/* 1. NAVBAR */}
      <nav className="navbar">
        <div className="nav-container">
          {/* Hanya Logo & Nama Brand */}
          <div className="nav-brand">
            <ScanSearch size={24} />
            <span>ReviewSense.ai</span>
          </div>
          {/* Bagian nav-links sudah dihapus */}
        </div>
      </nav>

      {/* 2. MAIN CONTENT */}
      <main className="main-content">
        
        {/* Page Header (Hero) */}
        <div className="page-header">
          <h1 className="page-title">Analyze Customer Feedback</h1>
          <p className="page-subtitle">
            Leverage AI to understand sentiment and extract key insights from product reviews instantly.
          </p>
        </div>

        <div className="app-grid">
          
          {/* KOLOM KIRI: Form Input */}
          <div className="web-card">
            <div className="card-title">
              <MessageSquareText size={20} className="text-blue-600" />
              Start New Analysis
            </div>

            <form onSubmit={handleSubmit}>
              <div>
                <label className="form-label">Product Name</label>
                <input 
                  type="text"
                  className="form-input"
                  placeholder="e.g. Sony WH-1000XM5"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="form-label">Customer Review</label>
                <textarea 
                  className="form-input"
                  placeholder="Paste the customer review here..."
                  value={reviewText}
                  onChange={(e) => setReviewText(e.target.value)}
                  required
                />
              </div>

              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
                {loading ? 'Analyzing...' : 'Analyze Review'}
              </button>
            </form>

            {/* HASIL ANALISIS MUNCUL DI SINI */}
            {result && (
              <div className="result-box" ref={resultRef}>
                <div style={{display:'flex', justifyContent:'space-between', marginBottom:'1rem'}}>
                  <span style={{color:'var(--text-secondary)', fontSize:'0.9rem'}}>Result for: <strong>{result.product_name}</strong></span>
                  <span style={{fontSize:'0.8rem', color:'var(--text-secondary)'}}>Conf: {(result.confidence * 100).toFixed(0)}%</span>
                </div>

                <div style={{display:'flex', alignItems:'center', gap:'10px', marginBottom:'1.5rem'}}>
                  {result.sentiment === 'POSITIVE' ? 
                    <CheckCircle size={32} color="#166534" /> : 
                    <AlertCircle size={32} color="#991b1b" />
                  }
                  <div>
                    <div style={{fontSize:'0.8rem', color:'var(--text-secondary)'}}>Detected Sentiment</div>
                    <div className={`sentiment-badge ${result.sentiment}`}>
                      {result.sentiment}
                    </div>
                  </div>
                </div>

                <div className="key-points">
                  <strong style={{fontSize:'0.9rem', display:'flex', alignItems:'center', gap:'6px'}}>
                    <Sparkles size={16} color="orange" /> Key Takeaways
                  </strong>
                  <ul>
                    {result.key_points.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* KOLOM KANAN: History */}
          <div className="web-card">
            <div className="card-title">
              <History size={20} />
              Recent Analysis
            </div>
            
            <div className="history-list">
              {history.length === 0 ? (
                <p style={{textAlign:'center', color:'#94a3b8', padding:'2rem'}}>No history yet.</p>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="history-card">
                    <div style={{display:'flex', justifyContent:'space-between', marginBottom:'6px'}}>
                      <h4>{item.product_name}</h4>
                      <span style={{
                        fontSize:'0.7rem', fontWeight:'bold', 
                        color: item.sentiment === 'POSITIVE' ? '#166534' : '#991b1b'
                      }}>
                        {item.sentiment}
                      </span>
                    </div>
                    <p>"{item.review_text}"</p>
                    <small style={{display:'block', marginTop:'8px', color:'#cbd5e1', fontSize:'0.7rem'}}>
                      {new Date(item.created_at).toLocaleDateString()}
                    </small>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      </main>

      {/* 3. FOOTER */}
      <footer className="footer">
        <p>&copy; 2025 ReviewSense Inc. Powered by Hugging Face & Gemini AI.</p>
      </footer>

    </div>
  );
}

export default App;