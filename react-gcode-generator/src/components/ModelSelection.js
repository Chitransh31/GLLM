import React from 'react';
import { Cpu, Settings2, HelpCircle } from 'lucide-react';

const ModelSelection = ({ 
  selectedModel, 
  onModelChange, 
  promptType, 
  onPromptTypeChange, 
  modelOptions, 
  disabled 
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Cpu className="h-5 w-5 mr-2 text-primary-600" />
        Model Configuration
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
          >
            {modelOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="mt-2 text-sm text-gray-500">
            {modelOptions.find(opt => opt.value === selectedModel)?.description}
          </div>
        </div>

        {/* Prompt Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Prompt Type
          </label>
          <select
            value={promptType}
            onChange={(e) => onPromptTypeChange(e.target.value)}
            disabled={disabled}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
          >
            <option value="Structured">Structured</option>
            <option value="Unstructured">Unstructured</option>
          </select>
          <div className="mt-2 text-sm text-gray-500">
            {promptType === 'Structured' 
              ? 'Uses parameter extraction and structured processing' 
              : 'Direct text-to-G-code generation'
            }
          </div>
        </div>
      </div>

      {/* Model Information */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-start space-x-2">
          <HelpCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900">Model Selection Tips</h4>
            <ul className="mt-2 text-sm text-blue-800 space-y-1">
              <li>• <strong>Fine-tuned StarCoder:</strong> Best for G-code generation (requires HuggingFace access)</li>
              <li>• <strong>GPT-3.5:</strong> Most versatile (requires OpenAI API key)</li>
              <li>• <strong>DeepSeek-Coder-1B:</strong> Good balance of speed and accuracy</li>
              <li>• <strong>Zephyr-7b:</strong> Reliable fallback option</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelSelection;
