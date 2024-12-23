import React, { useState, useEffect, useRef } from 'react';
 
const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [dates, setDates] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const ws = useRef(null);
 
  const handleStartRecording = () => {
    setIsRecording(true);
    setLoading(true);
    ws.current = new WebSocket('ws://localhost:8000/ws');
 
    ws.current.onopen = () => {
      console.log('WebSocket connection established');
    };
 
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);
 
      if (data.type === 'summary') {
        setTranscript(data.transcript);
        setSummary(data.summary);
        setDates(data.dates);
        setActionItems(data.action_items);
        setIsRecording(false);
        setLoading(false);
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.message);
        setIsRecording(false);
        setLoading(false);
      }
    };
 
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsRecording(false);
      setLoading(false);
    };
  };
 
  const handleStopRecording = () => {
    if (ws.current) {
      ws.current.send('STOP');
    }
    setIsRecording(false);
  };
 
  useEffect(() => {
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);
 
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'lavenderblush' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>AI-Meeting Notes Taker</h1>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <button
          onClick={isRecording ? handleStopRecording : handleStartRecording}
          style={{
            padding: '10px 20px',
            backgroundColor: isRecording ? 'red' : '#da78e9',
            color: '#fff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
          }}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </button>
      </div>
 
      <div style={{ display: 'flex', flex: 1, gap: '20px' }}>
        <div style={{ flex: 0.5, display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div
            style={{
              padding: '15px',
              border: '1px solid #ddd',
              borderRadius: '10px',
              backgroundColor: '#eae2ef ',
              flex: 0.5,
              overflow: 'auto'
            }}
          >
            <h2>AI Meeting Summary</h2>
            <p>{summary || 'No summary available'}</p>
          </div>
          <div style={{ display: 'flex', flex: 0.5, gap: '20px' }}>
            <div
              style={{
                flex: 1,
                padding: '15px',
                border: '1px solid #ddd',
                borderRadius: '10px',
                backgroundColor: '#eae2ef',
              }}
            >
              <h2>Dates Mentioned in the Conversation</h2>
              <ul>
                {dates.length > 0 ? dates.map((date, idx) => <li key={idx}>{date}</li>) : <li>No dates found</li>}
              </ul>
            </div>
            <div
              style={{
                flex: 1,
                padding: '15px',
                border: '1px solid #ddd',
                borderRadius: '10px',
                backgroundColor: '#eae2ef',
              }}
            >
              <h2>Action Items</h2>
              <ul>
                {actionItems.length > 0 ? actionItems.map((item, idx) => <li key={idx}>{item}</li>) : <li>No action items found</li>}
              </ul>
            </div>
          </div>
        </div>
        <div
          style={{
            flex: 0.5,
            padding: '15px',
            border: '1px solid #ddd',
            borderRadius: '10px',
            backgroundColor: '#ece2f2',
            overflowY: 'auto',
          }}
        >
          <h2>Transcript</h2>
          <p>{transcript || 'No transcript available'}</p>
        </div>
      </div>
 
      {loading && (
        <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
          <div
            style={{
              border: '5px solid #f3f3f3',
              borderTop: '5px solid green',
              borderRadius: '50%',
              width: '30px',
              height: '30px',
              animation: 'spin 1s linear infinite',
            }}
          ></div>
        </div>
      )}
 
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};
 
export default App;
 