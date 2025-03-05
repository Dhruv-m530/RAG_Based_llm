import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, FileText, Globe, Bot, Database, RefreshCw } from 'lucide-react';

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [urls, setUrls] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadLoading, setUploadLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || loading) return;
    
    setLoading(true);
    setAnswer('');
    setSources([]);
    
    try {
      const response = await fetch('http://0.0.0.0:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to get answer');
      }
      
      const data = await response.json();
      setAnswer(data.answer);
      setSources(data.sources);
    } catch (error) {
      console.error('Error:', error);
      setAnswer('Error: Failed to get a response. Please make sure the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUploadFiles = async () => {
    if (files.length === 0) return;
    
    setUploadLoading(true);
    setUploadStatus('Uploading files...');
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to upload files');
      }
      
      const data = await response.json();
      setUploadStatus(`Successfully processed ${files.length} files (${data.document_count} chunks)`);
      setFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus('Error: Failed to upload files. Please make sure the API server is running.');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleUploadUrls = async () => {
    if (!urls.trim()) return;
    
    setUploadLoading(true);
    setUploadStatus('Processing URLs...');
    
    const urlList = urls.split('\n').filter(url => url.trim()).map(url => url.trim());
    
    try {
      const response = await fetch('http://0.0.0.0:8000/process-urls', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls: urlList }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process URLs');
      }
      
      const data = await response.json();
      setUploadStatus(`Successfully processed ${urlList.length} URLs (${data.document_count} chunks)`);
      setUrls('');
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus('Error: Failed to process URLs. Please make sure the API server is running.');
    } finally {
      setUploadLoading(false);
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [answer, sources]);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-indigo-700 text-white p-4 shadow-md">
        <div className="container mx-auto flex items-center">
          <Bot className="h-8 w-8 mr-3" />
          <h1 className="text-2xl font-bold">Ollama RAG System</h1>
        </div>
      </header>
      
      <div className="container mx-auto p-4 flex flex-col md:flex-row gap-4 flex-grow">
        {/* Left panel - Document Upload */}
        <div className="w-full md:w-1/3 bg-white rounded-lg shadow-md p-4">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Knowledge Base
          </h2>
          
          <div className="mb-6">
            <h3 className="text-md font-medium mb-2 flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              Upload Documents
            </h3>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              multiple
              accept=".pdf,.docx,.doc"
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 mb-2"
            />
            <div className="flex items-center">
              <button
                onClick={handleUploadFiles}
                disabled={files.length === 0 || uploadLoading}
                className="flex items-center justify-center py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
              >
                {uploadLoading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                Upload Files
              </button>
              {files.length > 0 && (
                <span className="ml-2 text-sm text-gray-600">{files.length} file(s) selected</span>
              )}
            </div>
          </div>
          
          <div className="mb-6">
            <h3 className="text-md font-medium mb-2 flex items-center">
              <Globe className="h-4 w-4 mr-2" />
              Process URLs
            </h3>
            <textarea
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              placeholder="Enter URLs (one per line)"
              className="w-full p-2 border border-gray-300 rounded-md text-sm mb-2 h-24"
            />
            <button
              onClick={handleUploadUrls}
              disabled={!urls.trim() || uploadLoading}
              className="flex items-center justify-center py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
            >
              {uploadLoading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Globe className="h-4 w-4 mr-2" />}
              Process URLs
            </button>
          </div>
          
          {uploadStatus && (
            <div className={`text-sm p-3 rounded-md ${uploadStatus.includes('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
              {uploadStatus}
            </div>
          )}
        </div>
        
        {/* Right panel - Chat */}
        <div className="w-full md:w-2/3 bg-white rounded-lg shadow-md p-4 flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Ask Questions</h2>
          
          <div className="flex-grow overflow-auto mb-4 bg-gray-50 rounded-md p-4">
            {answer ? (
              <div>
                <div className="mb-4">
                  <div className="font-medium text-gray-800 mb-1">Your question:</div>
                  <div className="bg-indigo-50 p-3 rounded-md">{question}</div>
                </div>
                
                <div className="mb-4">
                  <div className="font-medium text-gray-800 mb-1">Answer:</div>
                  <div className="bg-white p-3 rounded-md border border-gray-200 whitespace-pre-line">
                    {answer}
                  </div>
                </div>
                
                {sources.length > 0 && (
                  <div>
                    <div className="font-medium text-gray-800 mb-1">Sources:</div>
                    <div className="bg-white border border-gray-200 rounded-md">
                      {sources.map((source, index) => (
                        <div key={index} className="p-3 border-b border-gray-200 last:border-b-0">
                          <div className="text-sm text-gray-600 mb-1">
                            <span className="font-medium">Source {index + 1}:</span> 
                            {source.metadata.file_name || source.metadata.source}
                          </div>
                          <div className="text-sm">{source.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center text-gray-500 h-full flex items-center justify-center">
                {loading ? (
                  <div className="flex flex-col items-center">
                    <RefreshCw className="h-8 w-8 animate-spin mb-2" />
                    <p>Thinking...</p>
                  </div>
                ) : (
                  <p>Ask a question to get started</p>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <form onSubmit={handleSubmit} className="flex">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="flex-grow p-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!question.trim() || loading}
              className="bg-indigo-600 text-white p-3 rounded-r-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? <RefreshCw className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </button>
          </form>
        </div>
      </div>
      
      <footer className="bg-gray-800 text-white p-4 text-center text-sm">
        <p>Ollama RAG System with LangChain - Powered by Local LLMs</p>
      </footer>
    </div>
  );
}

export default App;