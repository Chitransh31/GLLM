import React from 'react';
import { Settings, Eye, AlertTriangle, CheckCircle } from 'lucide-react';

const ParameterExtraction = ({
  onExtract,
  onVisualize,
  extractedParameters,
  missingParameters,
  decomposeTask,
  onDecomposeTaskChange,
  promptType,
  isLoading
}) => {
  const isStructured = promptType === 'Structured';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Settings className="h-5 w-5 mr-2 text-primary-600" />
        Parameter Extraction
      </h3>

      {/* Task Decomposition Option */}
      {isStructured && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Decompose Task Description
          </label>
          <select
            value={decomposeTask}
            onChange={(e) => onDecomposeTaskChange(e.target.value)}
            disabled={!isStructured || isLoading}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-50 disabled:text-gray-500"
          >
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
          <p className="mt-2 text-sm text-gray-500">
            Break down complex tasks into simpler sub-tasks for better processing
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <button
          onClick={onExtract}
          disabled={!isStructured || isLoading}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <Settings className="h-4 w-4" />
          <span>Extract Parameters</span>
        </button>
        
        <button
          onClick={onVisualize}
          disabled={!isStructured || !extractedParameters || isLoading}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <Eye className="h-4 w-4" />
          <span>Simulate Tool Path (2D)</span>
        </button>
      </div>

      {/* Extracted Parameters Display */}
      {extractedParameters && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
            Extracted Parameters
          </h4>
          <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap">
              {extractedParameters}
            </pre>
          </div>
        </div>
      )}

      {/* Missing Parameters Warning */}
      {missingParameters && missingParameters.length > 0 && (
        <div className="mb-6">
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <AlertTriangle className="h-4 w-4 mr-2 text-yellow-500" />
            Missing Parameters
          </h4>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <ul className="list-disc list-inside text-sm text-yellow-800 space-y-1">
              {missingParameters.map((param, index) => (
                <li key={index}>{param}</li>
              ))}
            </ul>
            <p className="mt-2 text-sm text-yellow-700">
              Consider adding these parameters to your task description for better results.
            </p>
          </div>
        </div>
      )}

      {/* Disabled State Message */}
      {!isStructured && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-700">
            Parameter extraction is only available in <strong>Structured</strong> prompt mode.
            Switch to Structured mode to use this feature.
          </p>
        </div>
      )}
    </div>
  );
};

export default ParameterExtraction;
