import { useState } from 'react'
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import './App.css'

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [deadCode, setDeadCode] = useState([]);
  const [mostCalled, setMostCalled] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const fetchAnalysisData = async () => {
    const deadCodeRes = await fetch('http://127.0.0.1:8000/dead-code');
    const deadCodeData = await deadCodeRes.json();
    setDeadCode(deadCodeData.dead_code);

    const mostCalledRes = await fetch('http://127.0.0.1:8000/most-called');
    const mostCalledData = await mostCalledRes.json();
    setMostCalled(mostCalledData.most_called);

    const graphRes = await fetch('http://127.0.0.1:8000/graph');
    const graphData = await graphRes.json();

    const deadNodeNames = new Set(deadCodeData.dead_code.map(n => n.name));

    const flowNodes = graphData.nodes.map((node, index) => ({
      id: String(node.id),
      data: { label: `${node.type}: ${node.name}` },
      position: {
        x: (index % 4) * 220,
        y: Math.floor(index / 4) * 120
      },
      style: {
        background: deadNodeNames.has(node.name) ? '#ffcccc' : '#cce5ff',
        border: '1px solid #333',
        borderRadius: '8px',
        padding: '10px',
        fontSize: '13px'
      }
    }));

    const flowEdges = graphData.edges.map((edge, index) => ({
      id: `e${index}`,
      source: String(edge.source),
      target: String(edge.target),
      animated: true,
      style: { stroke: '#555' }
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
    setAnalyzed(true);
  };

  const analyzeCodebase = async () => {
    setLoading(true);
    setStatusMessage('');
    try {
      await fetchAnalysisData();
    } catch (error) {
      alert("Backend se connect nahi ho paya. Kya uvicorn server chal raha hai?");
      console.error(error);
    }
    setLoading(false);
  };

  const analyzeGithubRepo = async () => {
    if (!repoUrl.trim()) {
      alert("Pehle GitHub repo URL daalo");
      return;
    }
    setLoading(true);
    setStatusMessage('Cloning aur analyzing... thoda time lagega');
    try {
      const res = await fetch('http://127.0.0.1:8000/analyze-github', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl })
      });
      const data = await res.json();

      if (data.status === 'error') {
        setStatusMessage(`Error: ${data.message}`);
        setLoading(false);
        return;
      }

      setStatusMessage(data.message);
      await fetchAnalysisData();
    } catch (error) {
      setStatusMessage("Backend se connect nahi ho paya.");
      console.error(error);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '40px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center' }}>CodeLens</h1>
      <p style={{ textAlign: 'center' }}>AI-Powered Codebase Analysis Platform</p>

      <div style={{ textAlign: 'center', marginBottom: '15px' }}>
        <input
          type="text"
          placeholder="https://github.com/user/repo.git"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          style={{ padding: '8px', width: '400px', fontSize: '14px', marginRight: '10px' }}
        />
        <button onClick={analyzeGithubRepo} disabled={loading} style={{ padding: '9px 18px', fontSize: '14px', cursor: 'pointer' }}>
          {loading ? 'Working...' : 'Analyze GitHub Repo'}
        </button>
      </div>

      {statusMessage && (
        <p style={{ textAlign: 'center', color: statusMessage.startsWith('Error') ? 'red' : 'green', fontSize: '13px' }}>
          {statusMessage}
        </p>
      )}

      <div style={{ textAlign: 'center', marginBottom: '30px', color: '#888', fontSize: '13px' }}>
        --- OR ---
      </div>

      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <button onClick={analyzeCodebase} disabled={loading} style={{ padding: '10px 20px', fontSize: '16px', cursor: 'pointer' }}>
          {loading ? 'Analyzing...' : 'Analyze Existing Local Data'}
        </button>
      </div>

      {analyzed && (
        <div>
          <h2>Dependency Graph</h2>
          <p style={{ fontSize: '13px', color: '#666' }}>
            <span style={{ background: '#ffcccc', padding: '2px 8px', borderRadius: '4px' }}>Red</span> = Dead code (unused) &nbsp;
            <span style={{ background: '#cce5ff', padding: '2px 8px', borderRadius: '4px' }}>Blue</span> = Used
          </p>
          <div style={{ height: '400px', border: '1px solid #ccc', borderRadius: '8px', marginBottom: '30px' }}>
            <ReactFlow nodes={nodes} edges={edges} fitView>
              <Background />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </div>

          <h2>Dead Code (Unused Functions/Classes)</h2>
          {deadCode.length === 0 ? (
            <p>Koi dead code nahi mila!</p>
          ) : (
            <ul>
              {deadCode.map((node, idx) => (
                <li key={idx}>
                  <strong>{node.type}</strong>: {node.name} (line {node.start_line})
                </li>
              ))}
            </ul>
          )}

          <h2>Most Called Functions</h2>
          <ul>
            {mostCalled.map((item, idx) => (
              <li key={idx}>
                {item.name}: called {item.count} times
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
