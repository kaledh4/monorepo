import { useState, useEffect } from 'react'
import './App.css'

interface KnowledgeSummary {
  title: string;
  eli5: string;
  long_term: string;
}

interface KnowledgeData {
  timestamp: string;
  summaries?: KnowledgeSummary[];
  papers?: {
    [domain: string]: Array<{
      title: string;
      summary: string;
      date: string;
      link: string;
    }>;
  };
  news?: Array<{
    title: string;
    source: string;
    url: string;
    publishedAt: string;
  }>;
}

function App() {
  const [data, setData] = useState<KnowledgeData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Multi-path data fetching strategy (unified pattern)
    const dataPaths = [
      './data/latest.json',                          // Local data folder
      './latest.json',                                // Same directory
      '../data/the-library/latest.json',          // GitHub Pages structure
      '../../data/the-library/latest.json'        // Local dev structure
    ];

    async function fetchData() {
      let lastError: Error | null = null;

      for (const dataPath of dataPaths) {
        try {
          const response = await fetch(`${dataPath}?t=${Date.now()}`);
          if (response.ok) {
            const jsonData = await response.json();
            console.log(`Data loaded from: ${dataPath}`);
            setData(jsonData);
            setLoading(false);
            return;
          }
        } catch (err) {
          lastError = err as Error;
          console.debug(`Path ${dataPath} failed, trying next...`);
        }
      }

      console.error('Error fetching data from all paths:', lastError);
      setError('Failed to load knowledge data. Please try again later.');
      setLoading(false);
    }

    fetchData();
  }, [])

  if (loading) {
    return (
      <div className="container">
        <h1>Free Knowledge Dashboard</h1>
        <p style={{ textAlign: 'center', padding: '2rem' }}>Loading...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container">
        <h1>Free Knowledge Dashboard</h1>
        <p style={{ textAlign: 'center', padding: '2rem', color: '#dc3545' }}>
          {error || 'No data available'}
        </p>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>The Library - Alpha-Clarity Archive</h1>
      <p style={{ textAlign: 'center', opacity: 0.7, marginBottom: '2rem' }}>
        Updated: {new Date(data.timestamp).toLocaleString()}
      </p>

      <div className="grid">
        {data.summaries && data.summaries.length > 0 ? (
          data.summaries.map((item: KnowledgeSummary, i: number) => (
            <div className="card" key={i}>
              <h2>📚 {item.title}</h2>
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1rem', color: '#28a745' }}>👶 ELI5 Summary</h3>
                <p>{item.eli5}</p>
              </div>
              <div>
                <h3 style={{ fontSize: '1rem', color: '#007bff' }}>🔭 Why It Matters Long-Term</h3>
                <p>{item.long_term}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="card">
            <p>No summaries available yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
