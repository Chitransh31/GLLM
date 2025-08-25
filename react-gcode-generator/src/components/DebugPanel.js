import React from 'react';
import { BarChart3, Code, Database } from 'lucide-react';

const DebugPanel = ({ sessionState }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <BarChart3 className="h-5 w-5 mr-2 text-primary-600" />
        Debug Information
      </h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Session State */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <Database className="h-4 w-4 mr-2 text-blue-500" />
            Session State
          </h4>
          <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-xs text-gray-700 whitespace-pre-wrap">
              {JSON.stringify(sessionState, null, 2)}
            </pre>
          </div>
        </div>

        {/* Application Info */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <Code className="h-4 w-4 mr-2 text-green-500" />
            Application Info
          </h4>
          <div className="space-y-3">
            <div className="bg-blue-50 rounded-lg p-3">
              <h5 className="font-medium text-blue-900 mb-2">Environment</h5>
              <div className="text-sm text-blue-800 space-y-1">
                <div>React Version: {React.version}</div>
                <div>Environment: {process.env.NODE_ENV}</div>
                <div>Timestamp: {new Date().toISOString()}</div>
              </div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-3">
              <h5 className="font-medium text-green-900 mb-2">API Status</h5>
              <div className="text-sm text-green-800 space-y-1">
                <div>Backend: Connected</div>
                <div>Model: {sessionState.selectedModel || 'Not selected'}</div>
                <div>Mode: {sessionState.promptType || 'Not set'}</div>
              </div>
            </div>

            <div className="bg-yellow-50 rounded-lg p-3">
              <h5 className="font-medium text-yellow-900 mb-2">Processing Status</h5>
              <div className="text-sm text-yellow-800 space-y-1">
                <div>Task Description: {sessionState.taskDescription ? 'Set' : 'Empty'}</div>
                <div>Parameters: {sessionState.extractedParameters ? 'Extracted' : 'Not extracted'}</div>
                <div>G-Code: {sessionState.generatedGCode ? 'Generated' : 'Not generated'}</div>
                <div>PDF Files: {sessionState.pdfFilesCount || 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Debug Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="font-medium text-gray-900 mb-3">Debug Actions</h4>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => console.log('Session State:', sessionState)}
            className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
          >
            Log Session State
          </button>
          <button
            onClick={() => {
              const debugData = {
                sessionState,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent
              };
              navigator.clipboard.writeText(JSON.stringify(debugData, null, 2));
            }}
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            Copy Debug Info
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            Reset Application
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebugPanel;
