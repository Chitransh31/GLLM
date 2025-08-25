import React from 'react';
import Plot from 'react-plotly.js';
import { BarChart3, Eye, AlertCircle } from 'lucide-react';

const GCodeVisualization = ({ parsedParameters, generatedGCode }) => {
  // Generate 2D tool path visualization
  const generateToolPathPlot = () => {
    if (!parsedParameters) return null;

    try {
      // Mock data for demonstration - in real app this would come from parsed parameters
      const mockToolPath = [
        { x: 0, y: 0 },
        { x: 50, y: 0 },
        { x: 50, y: 30 },
        { x: 0, y: 30 },
        { x: 0, y: 0 }
      ];

      const workpieceData = {
        x: [0, 50, 50, 0, 0],
        y: [0, 0, 30, 30, 0],
        mode: 'lines',
        line: { color: 'black', width: 3 },
        name: 'Workpiece',
        fill: 'toself',
        fillcolor: 'rgba(128, 128, 128, 0.3)'
      };

      const toolPathData = {
        x: mockToolPath.map(point => point.x),
        y: mockToolPath.map(point => point.y),
        mode: 'lines+markers',
        line: { color: 'red', width: 2 },
        marker: { color: 'red', size: 6 },
        name: 'Tool Path'
      };

      return {
        data: [workpieceData, toolPathData],
        layout: {
          title: 'CNC Tool Path Visualization (2D)',
          xaxis: { title: 'X (mm)', range: [-5, 55] },
          yaxis: { title: 'Y (mm)', range: [-5, 35] },
          showlegend: true,
          width: 400,
          height: 300,
          margin: { t: 50, r: 20, b: 50, l: 50 }
        }
      };
    } catch (error) {
      console.error('Error generating tool path plot:', error);
      return null;
    }
  };

  // Generate G-code statistics visualization
  const generateGCodeStats = () => {
    if (!generatedGCode) return null;

    try {
      const lines = generatedGCode.split('\n');
      const gCommands = (generatedGCode.match(/G\d+/g) || []).length;
      const mCommands = (generatedGCode.match(/M\d+/g) || []).length;
      const coordinates = (generatedGCode.match(/[XYZ]\d+/g) || []).length;

      const data = [{
        x: ['G-Commands', 'M-Commands', 'Coordinates', 'Total Lines'],
        y: [gCommands, mCommands, coordinates, lines.length],
        type: 'bar',
        marker: {
          color: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']
        }
      }];

      return {
        data,
        layout: {
          title: 'G-Code Statistics',
          xaxis: { title: 'Command Type' },
          yaxis: { title: 'Count' },
          width: 400,
          height: 300,
          margin: { t: 50, r: 20, b: 50, l: 50 }
        }
      };
    } catch (error) {
      console.error('Error generating G-code stats:', error);
      return null;
    }
  };

  const toolPathPlot = generateToolPathPlot();
  const statsPlot = generateGCodeStats();

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <BarChart3 className="h-5 w-5 mr-2 text-primary-600" />
        Visualization
      </h3>

      <div className="space-y-6">
        {/* Tool Path Visualization */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <Eye className="h-4 w-4 mr-2 text-blue-500" />
            Tool Path (2D)
          </h4>
          
          {toolPathPlot ? (
            <div className="border border-gray-200 rounded-lg p-4">
              <Plot
                data={toolPathPlot.data}
                layout={toolPathPlot.layout}
                config={{ responsive: true, displayModeBar: false }}
              />
              <p className="text-sm text-gray-600 mt-2">
                Red line shows the tool path, gray area represents the workpiece.
              </p>
            </div>
          ) : parsedParameters ? (
            <div className="border border-gray-200 rounded-lg p-6 text-center">
              <AlertCircle className="h-8 w-8 mx-auto text-yellow-500 mb-2" />
              <p className="text-gray-600">Error generating visualization</p>
            </div>
          ) : (
            <div className="border border-gray-200 rounded-lg p-6 text-center">
              <BarChart3 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No visualization data available</p>
              <p className="text-sm text-gray-400">Extract parameters first to generate visualization</p>
            </div>
          )}
        </div>

        {/* G-Code Statistics */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <BarChart3 className="h-4 w-4 mr-2 text-green-500" />
            G-Code Analysis
          </h4>
          
          {statsPlot ? (
            <div className="border border-gray-200 rounded-lg p-4">
              <Plot
                data={statsPlot.data}
                layout={statsPlot.layout}
                config={{ responsive: true, displayModeBar: false }}
              />
            </div>
          ) : generatedGCode ? (
            <div className="border border-gray-200 rounded-lg p-6 text-center">
              <AlertCircle className="h-8 w-8 mx-auto text-yellow-500 mb-2" />
              <p className="text-gray-600">Error generating statistics</p>
            </div>
          ) : (
            <div className="border border-gray-200 rounded-lg p-6 text-center">
              <BarChart3 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No G-code to analyze</p>
              <p className="text-sm text-gray-400">Generate G-code first to see statistics</p>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        {generatedGCode && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h5 className="font-medium text-gray-900 mb-2">Quick Stats</h5>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">File Size:</span>
                <span className="ml-2 font-medium">{(generatedGCode.length / 1024).toFixed(2)} KB</span>
              </div>
              <div>
                <span className="text-gray-600">Estimated Time:</span>
                <span className="ml-2 font-medium">~{Math.round(generatedGCode.split('\n').length / 10)} min</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GCodeVisualization;
