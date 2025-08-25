import React from 'react';
import { Play, Download, Code, FileText } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const GCodeGeneration = ({ onGenerate, onDownload, generatedGCode, isLoading }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Code className="h-5 w-5 mr-2 text-primary-600" />
        G-Code Generation
      </h3>

      {/* Generation Button */}
      <div className="mb-6">
        <button
          onClick={onGenerate}
          disabled={isLoading}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2 text-lg font-medium"
        >
          <Play className="h-5 w-5" />
          <span>Generate G-code</span>
        </button>
        <p className="mt-2 text-sm text-gray-500">
          Generate CNC machine code based on your task description and parameters
        </p>
      </div>

      {/* Generated G-Code Display */}
      {generatedGCode && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900 flex items-center">
              <FileText className="h-4 w-4 mr-2 text-green-500" />
              Generated G-Code
            </h4>
            <button
              onClick={onDownload}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Download</span>
            </button>
          </div>

          <div className="gcode-container">
            <SyntaxHighlighter
              language="gcode"
              style={vscDarkPlus}
              showLineNumbers={true}
              customStyle={{
                margin: 0,
                borderRadius: '8px',
                fontSize: '14px'
              }}
            >
              {generatedGCode}
            </SyntaxHighlighter>
          </div>

          {/* G-Code Statistics */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {generatedGCode.split('\n').length}
              </div>
              <div className="text-sm text-gray-500">Lines</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {(generatedGCode.match(/G0[0-9]/g) || []).length}
              </div>
              <div className="text-sm text-gray-500">G-Commands</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {Math.round(generatedGCode.length / 1024 * 100) / 100}
              </div>
              <div className="text-sm text-gray-500">KB</div>
            </div>
          </div>
        </div>
      )}

      {/* No G-Code Message */}
      {!generatedGCode && !isLoading && (
        <div className="text-center py-8 text-gray-500">
          <Code className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>No G-code generated yet</p>
          <p className="text-sm">Click "Generate G-code" to create CNC machine code</p>
        </div>
      )}
    </div>
  );
};

export default GCodeGeneration;
