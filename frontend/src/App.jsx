import React, { useState } from 'react';
import axios from 'axios';
import { Search, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SqlCodeBlock from './components/SqlCodeBlock';
import Expander from './components/Expander';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResults(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/query`, {
        query
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <main className="main-content">
        <header>
          <h1>AskTennis AI</h1>
          <p className="subtitle">Instant insights from historical tennis data</p>
        </header>

        <div className="search-container">
          <input
            className="search-input"
            type="text"
            placeholder="Ask a question about tennis matches (stats, head-to-head, rankings)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
            {loading ? <Loader2 className="animate-spin" /> : <Search />}
          </button>
        </div>

        {results ? (
          <div className="results-container">
            <div className="card">
              <h3>Answer</h3>
              <div className="answer-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{results.answer}</ReactMarkdown>
              </div>
            </div>

            {results.sql_queries && results.sql_queries.length > 0 && (
              <div className="section-container">
                <Expander label="SQL Queries">
                  {results.sql_queries.map((sql, i) => (
                    <SqlCodeBlock key={i} code={sql} />
                  ))}
                </Expander>
              </div>
            )}

            {/* {results.data && results.data.length > 0 && (
              <div className="card">
                <h3>Data</h3>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(results.data[0]).map(key => <th key={key}>{key}</th>)}
                      </tr>
                    </thead>
                    <tbody>
                      {results.data.map((row, i) => (
                        <tr key={i}>
                          {Object.values(row).map((val, j) => <td key={j}>{String(val)}</td>)}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )} */}
          </div>
        ) : (
          !loading && (
            <div className="welcome-container">
              <h3>Try asking:</h3>
              <div className="example-queries">
                <button onClick={() => { setQuery("Who has the most aces in a single match?"); }}>"Who has the most aces in a single match?"</button>
                <button onClick={() => { setQuery("Federer vs Nadal head to head on clay"); }}>"Federer vs Nadal head to head on clay"</button>
                <button onClick={() => { setQuery("Top 10 players in 2023"); }}>"Top 10 players in 2023"</button>
              </div>
            </div>
          )
        )}
      </main>
    </div>
  );
}

export default App;
