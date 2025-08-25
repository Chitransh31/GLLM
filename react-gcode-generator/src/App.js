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

function App() {
  // State management
  const [taskDescription, setTaskDescription] = useState('');
  const [selectedModel, setSelectedModel] = useState('Zephyr-7b');
  const [availableModels, setAvailableModels] = useState([]);
  const [decomposeTask, setDecomposeTask] = useState('Yes');
  const [promptType, setPromptType] = useState('Structured');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [extractedParameters, setExtractedParameters] = useState('');
  const [missingParameters, setMissingParameters] = useState([]);
  const [parsedParameters, setParsedParameters] = useState({});
  const [generatedGCode, setGeneratedGCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [backendStatus, setBackendStatus] = useState('unknown');
  const [debugMode, setDebugMode] = useState(false);

  // Check backend health on component mount
  useEffect(() => {
    checkBackendHealth();
    loadAvailableModels();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await apiService.healthCheck();
      setBackendStatus('healthy');
      toast.success('Backend connected successfully');
    } catch (error) {
      setBackendStatus('unhealthy');
      toast.error('Backend is not available. Please start the FastAPI server.');
    }
  };

  const loadAvailableModels = async () => {
    try {
      const response = await apiService.getAvailableModels();
      setAvailableModels(response.models);
    } catch (error) {
      console.error('Failed to load models:', error);
      // Fallback to default models
      setAvailableModels([
        { value: 'Zephyr-7b', label: 'Zephyr-7b', type: 'open', description: 'Reliable general-purpose model' },
        { value: 'GPT-3.5', label: 'GPT-3.5', type: 'api', description: 'Best overall performance (requires API key)' },
        { value: 'Fine-tuned StarCoder', label: 'Fine-tuned StarCoder', type: 'gated', description: 'Best for G-code (requires HF access)' },
        { value: 'CodeLlama', label: 'CodeLlama', type: 'open', description: 'Specialized code model' },
        { value: 'DeepSeek-Coder-1B', label: 'DeepSeek-Coder-1B', type: 'open', description: 'Lightweight and efficient' },
        { value: 'Phi-3-Mini', label: 'Phi-3-Mini', type: 'open', description: 'Microsoft\'s efficient model' }
      ]);
    }
  };

  const handleExtractParameters = async () => {
    if (!taskDescription.trim()) {
      toast.error('Please enter a task description');
      return;
    }

    try {
      setIsLoading(true);
      setCurrentStep(2);
      
      const response = await apiService.extractParameters({
        description: taskDescription,
        model: selectedModel,
        decomposeTask: decomposeTask,
        pdfFiles: uploadedFiles
      });
      
      setExtractedParameters(response.extractedParameters);
      setMissingParameters(response.missingParameters || []);
      
      // Parse parameters for visualization
      if (response.extractedParameters) {
        try {
          const parsedResponse = await apiService.parseParameters(response.extractedParameters);
          setParsedParameters(parsedResponse.parsedParameters);
        } catch (parseError) {
          console.error('Failed to parse parameters:', parseError);
        }
      }
      
      toast.success('Parameters extracted successfully!');
      setCurrentStep(3);
    } catch (error) {
      console.error('Parameter extraction error:', error);
      toast.error(`Failed to extract parameters: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateGCode = async () => {
    try {
      setIsLoading(true);
      setCurrentStep(4);
      
      const response = await apiService.generateGCode({
        description: taskDescription,
        model: selectedModel,
        promptType: promptType,
        extractedParameters: extractedParameters,
        pdfFiles: uploadedFiles
      });
      
      setGeneratedGCode(response.gcode);
      toast.success('G-code generated successfully!');
      setCurrentStep(5);
    } catch (error) {
      console.error('G-code generation error:', error);
      toast.error(`Failed to generate G-code: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (files) => {
    try {
      setIsLoading(true);
      const response = await apiService.uploadPDF(files);
      setUploadedFiles(response.files);
      toast.success(`Uploaded ${files.length} file(s) successfully`);
    } catch (error) {
      console.error('File upload error:', error);
      toast.error(`Failed to upload files: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const resetApplication = () => {
    setTaskDescription('');
    setExtractedParameters('');
    setMissingParameters([]);
    setParsedParameters({});
    setGeneratedGCode('');
    setUploadedFiles([]);
    setCurrentStep(1);
    toast.success('Application reset');
  };

  const downloadGCode = () => {
    if (!generatedGCode) {
      toast.error('No G-code to download');
      return;
    }
    
    const blob = new Blob([generatedGCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_program.nc';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('G-code downloaded successfully');
  };

  const getStepStatus = (step) => {
    if (currentStep > step) return 'completed';
    if (currentStep === step) return 'current';
    return 'pending';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Code className="h-8 w-8 text-primary-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-900">G-code Generator</h1>
            </div>
            <div className="flex items-center space-x-4">
              <StatusCard 
                status={backendStatus}
                isLoading={isLoading}
                currentStep={currentStep}
              />
              <button
                onClick={() => setDebugMode(!debugMode)}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                title="Toggle Debug Mode"
              >
                <Settings2 className="h-5 w-5" />
              </button>
              <button
                onClick={resetApplication}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[
              { number: 1, title: 'Task Description', icon: FileText },
              { number: 2, title: 'Parameter Extraction', icon: Settings },
              { number: 3, title: 'Visualization', icon: Eye },
              { number: 4, title: 'G-code Generation', icon: Code },
              { number: 5, title: 'Download', icon: Download }
            ].map(({ number, title, icon: Icon }, index) => {
              const status = getStepStatus(number);
              return (
                <div key={number} className="flex items-center">
                  <div className={`
                    flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors
                    ${status === 'completed' ? 'bg-green-500 border-green-500 text-white' : 
                      status === 'current' ? 'bg-primary-500 border-primary-500 text-white' : 
                      'bg-white border-gray-300 text-gray-400'}
                  `}>
                    {status === 'completed' ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : (
                      <Icon className="h-5 w-5" />
                    )}
                  </div>
                  <span className={`ml-2 text-sm font-medium ${
                    status === 'current' ? 'text-primary-600' : 'text-gray-500'
                  }`}>
                    {title}
                  </span>
                  {index < 4 && (
                    <div className={`w-16 h-0.5 mx-4 ${
                      getStepStatus(number + 1) === 'completed' ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Input and Configuration */}
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
              models={availableModels}
              decomposeTask={decomposeTask}
              onDecomposeTaskChange={setDecomposeTask}
              promptType={promptType}
              onPromptTypeChange={setPromptType}
              onFileUpload={handleFileUpload}
              uploadedFiles={uploadedFiles}
              disabled={isLoading}
            />

            {/* Parameter Extraction */}
            {currentStep >= 2 && (
              <ParameterExtraction
                extractedParameters={extractedParameters}
                missingParameters={missingParameters}
                onExtractParameters={handleExtractParameters}
                isLoading={isLoading}
                disabled={!taskDescription}
              />
            )}

            {/* G-code Generation */}
            {currentStep >= 4 && (
              <GCodeGeneration
                generatedGCode={generatedGCode}
                onGenerateGCode={handleGenerateGCode}
                onDownload={downloadGCode}
                isLoading={isLoading}
                disabled={!extractedParameters}
              />
            )}
          </div>

          {/* Right Column - Visualization and Debug */}
          <div className="space-y-6">
            {/* Visualization */}
            {currentStep >= 3 && parsedParameters && Object.keys(parsedParameters).length > 0 && (
              <GCodeVisualization
                parameters={parsedParameters}
                gcode={generatedGCode}
              />
            )}

            {/* Debug Panel */}
            {debugMode && (
              <DebugPanel
                sessionState={{
                  taskDescription,
                  selectedModel,
                  promptType,
                  extractedParameters,
                  parsedParameters,
                  generatedGCode,
                  missingParameters,
                  uploadedFiles: uploadedFiles.length,
                  currentStep,
                  backendStatus
                }}
              />
            )}
          </div>
        </div>

        {/* Loading Overlay */}
        {isLoading && <LoadingSpinner />}
      </main>
    </div>
  );
}

export default App;
