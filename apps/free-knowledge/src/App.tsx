import { useState, useEffect } from 'react'
import './App.css'

interface KnowledgeData {
  timestamp: string;
  papers: {
    [domain: string]: Array<{
      title: string;
      summary: string;
      date: string;
      link: string;
    }>;
  };
  news: Array<{
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
      '../data/free-knowledge/latest.json',          // GitHub Pages structure
      '../../data/free-knowledge/latest.json'        // Local dev structure
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
      <h1>Free Knowledge Dashboard</h1>
      <p style={{ textAlign: 'center', opacity: 0.7, marginBottom: '2rem' }}>
        Updated: {new Date(data.timestamp).toLocaleString()}
      </p>

      <div className="grid">
        <div className="card">
          <h2>📰 Latest News</h2>
          {data.news && data.news.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data.news.map((item, i) => (
                <li key={i} style={{ marginBottom: '1rem', padding: '0.5rem', borderLeft: '3px solid #007bff' }}>
                  <a href={item.url} target="_blank" rel="noreferrer" style={{ fontWeight: 'bold', color: '#007bff' }}>
                    {item.title}
                  </a>
                  <p style={{ fontSize: '0.85em', opacity: 0.7, margin: '0.25rem 0 0 0' }}>
                    {item.source} • {item.publishedAt}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p>No news available</p>
          )}
        </div>

        {data.papers && Object.keys(data.papers).map(domain => (
          <div className="card" key={domain}>
            <h2>📚 {domain}</h2>
            {data.papers[domain] && data.papers[domain].length > 0 ? (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {data.papers[domain].map((paper, i) => (
                  <li key={i} style={{ marginBottom: '1rem', padding: '0.5rem', borderLeft: '3px solid #28a745' }}>
                    <a href={paper.link} target="_blank" rel="noreferrer" style={{ fontWeight: 'bold', color: '#28a745' }}>
                      {paper.title}
                    </a>
                    <p style={{ fontSize: '0.85em', margin: '0.5rem 0 0 0' }}>{paper.summary}</p>
                    <p style={{ fontSize: '0.75em', opacity: 0.7, margin: '0.25rem 0 0 0' }}>
                      Published: {paper.date}
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No papers available</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default App
