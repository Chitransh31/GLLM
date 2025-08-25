import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Settings, 
  Play, 
  FileText, 
  Download, 
  Upload, 
  Eye,
  Cpu,
  AlertCircle,
  CheckCircle,
  Loader,
  Code,
  Settings2,
  BarChart3
} from 'lucide-react';
import TaskDescriptionInput from './components/TaskDescriptionInput';
import ModelSelection from './components/ModelSelection';
import ParameterExtraction from './components/ParameterExtraction';
import GCodeGeneration from './components/GCodeGeneration';
import GCodeVisualization from './components/GCodeVisualization';
import DebugPanel from './components/DebugPanel';
import StatusCard from './components/StatusCard';
import LoadingSpinner from './components/LoadingSpinner';
import apiService from './services/api';
import GCodeVisualization from './components/GCodeVisualization';
import DebugPanel from './components/DebugPanel';
import StatusCard from './components/StatusCard';
import LoadingSpinner from './components/LoadingSpinner';

function App() {
  // Application state
  const [taskDescription, setTaskDescription] = useState('');
  const [selectedModel, setSelectedModel] = useState('GPT-3.5');
  const [promptType, setPromptType] = useState('Structured');
  const [pdfFiles, setPdfFiles] = useState([]);
  const [extractedParameters, setExtractedParameters] = useState(null);
  const [parsedParameters, setParsedParameters] = useState(null);
  const [generatedGCode, setGeneratedGCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [decomposeTask, setDecomposeTask] = useState('Yes');
  const [missingParameters, setMissingParameters] = useState([]);
  const [sessionState, setSessionState] = useState({});

  // Model options
  const modelOptions = [
    { value: 'Zephyr-7b', label: 'Zephyr-7b', description: 'Reliable general-purpose model' },
    { value: 'GPT-3.5', label: 'GPT-3.5', description: 'Best overall performance (requires API key)' },
    { value: 'Fine-tuned StarCoder', label: 'Fine-tuned StarCoder', description: 'Best for G-code (requires HF access)' },
    { value: 'CodeLlama', label: 'CodeLlama', description: 'Specialized code model' },
    { value: 'DeepSeek-Coder-1B', label: 'DeepSeek-Coder-1B', description: 'Lightweight and efficient' },
    { value: 'Phi-3-Mini', label: 'Phi-3-Mini', description: 'Microsoft\'s efficient model' }
  ];

  // Update session state whenever main state changes
  useEffect(() => {
    setSessionState({
      taskDescription,
      selectedModel,
      promptType,
      extractedParameters,
      parsedParameters,
      generatedGCode,
      missingParameters,
      pdfFilesCount: pdfFiles.length
    });
  }, [taskDescription, selectedModel, promptType, extractedParameters, parsedParameters, generatedGCode, missingParameters, pdfFiles]);

  // Handle parameter extraction
  const handleExtractParameters = async () => {
    if (!taskDescription.trim()) {
      toast.error('Please enter a task description first');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call to extract parameters
      const response = await fetch('/api/extract-parameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: taskDescription,
          model: selectedModel,
          decomposeTask: decomposeTask,
          pdfFiles: pdfFiles
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to extract parameters');
      }

      const data = await response.json();
      setExtractedParameters(data.extractedParameters);
      setMissingParameters(data.missingParameters || []);
      
      toast.success('Parameters extracted successfully!');
    } catch (error) {
      console.error('Error extracting parameters:', error);
      toast.error('Failed to extract parameters. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle visualization
  const handleVisualize = async () => {
    if (!extractedParameters) {
      toast.error('Please extract parameters first');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call to parse parameters and generate visualization data
      const response = await fetch('/api/parse-parameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          extractedParameters: extractedParameters
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to parse parameters');
      }

      const data = await response.json();
      setParsedParameters(data.parsedParameters);
      
      toast.success('Visualization generated successfully!');
    } catch (error) {
      console.error('Error parsing parameters:', error);
      toast.error('Failed to generate visualization. Please check your parameters.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle G-code generation
  const handleGenerateGCode = async () => {
    if (!taskDescription.trim()) {
      toast.error('Please enter a task description first');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate API call to generate G-code
      const response = await fetch('/api/generate-gcode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description: taskDescription,
          model: selectedModel,
          promptType: promptType,
          extractedParameters: extractedParameters,
          pdfFiles: pdfFiles
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate G-code');
      }

      const data = await response.json();
      setGeneratedGCode(data.gcode);
      
      toast.success('G-code generated successfully!');
    } catch (error) {
      console.error('Error generating G-code:', error);
      toast.error('Failed to generate G-code. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle file download
  const handleDownloadGCode = () => {
    if (!generatedGCode) {
      toast.error('No G-code to download');
      return;
    }

    const blob = new Blob([generatedGCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_gcode.nc';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('G-code downloaded successfully!');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-600 rounded-lg">
                <Settings className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">G-code Generator</h1>
                <p className="text-gray-600">AI-powered CNC machining assistant</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <StatusCard 
                icon={Cpu} 
                label="Model" 
                value={selectedModel}
                color="blue"
              />
              <StatusCard 
                icon={FileText} 
                label="Prompt Type" 
                value={promptType}
                color="green"
              />
              <button
                onClick={() => setDebugMode(!debugMode)}
                className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors ${
                  debugMode 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Debug</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column - Input & Configuration */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Task Description */}
            <TaskDescriptionInput
              value={taskDescription}
              onChange={setTaskDescription}
              disabled={isLoading}
            />

            {/* Model Selection */}
            <ModelSelection
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
              promptType={promptType}
              onPromptTypeChange={setPromptType}
              modelOptions={modelOptions}
              disabled={isLoading}
            />

            {/* PDF Upload */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Upload className="h-5 w-5 mr-2 text-primary-600" />
                Knowledge Base (RAG)
              </h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-2">Upload PDF files for additional knowledge</p>
                <input
                  type="file"
                  multiple
                  accept=".pdf"
                  onChange={(e) => setPdfFiles(Array.from(e.target.files))}
                  className="hidden"
                  id="pdf-upload"
                />
                <label
                  htmlFor="pdf-upload"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 cursor-pointer"
                >
                  Choose Files
                </label>
                {pdfFiles.length > 0 && (
                  <p className="mt-2 text-sm text-gray-600">
                    {pdfFiles.length} file(s) selected
                  </p>
                )}
              </div>
            </div>

            {/* Parameter Extraction */}
            <ParameterExtraction
              onExtract={handleExtractParameters}
              onVisualize={handleVisualize}
              extractedParameters={extractedParameters}
              missingParameters={missingParameters}
              decomposeTask={decomposeTask}
              onDecomposeTaskChange={setDecomposeTask}
              promptType={promptType}
              isLoading={isLoading}
            />

            {/* G-Code Generation */}
            <GCodeGeneration
              onGenerate={handleGenerateGCode}
              onDownload={handleDownloadGCode}
              generatedGCode={generatedGCode}
              isLoading={isLoading}
            />

          </div>

          {/* Right Column - Visualization & Output */}
          <div className="space-y-6">
            
            {/* Visualization */}
            <GCodeVisualization
              parsedParameters={parsedParameters}
              generatedGCode={generatedGCode}
            />

            {/* Status Panel */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Task Description</span>
                  <div className="flex items-center">
                    {taskDescription ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Parameters Extracted</span>
                  <div className="flex items-center">
                    {extractedParameters ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">G-code Generated</span>
                  <div className="flex items-center">
                    {generatedGCode ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-gray-400" />
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <LoadingSpinner message="Processing..." />
              </div>
            )}

          </div>
        </div>

        {/* Debug Panel */}
        {debugMode && (
          <div className="mt-8">
            <DebugPanel sessionState={sessionState} />
          </div>
        )}
      </main>

      <Toaster position="top-right" />
    </div>
  );
}

export default App;
