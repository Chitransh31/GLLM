import React from 'react';
import { FileText } from 'lucide-react';

const TaskDescriptionInput = ({ value, onChange, disabled }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <FileText className="h-5 w-5 mr-2 text-primary-600" />
        Task Description
      </h2>
      <p className="text-gray-600 mb-4">
        Describe your CNC machining task in natural language:
      </p>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Example: Mill a rectangular pocket in aluminum, 50mm x 30mm x 5mm deep, using a 6mm end mill at 1000mm/min feed rate..."
        className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none disabled:bg-gray-50 disabled:text-gray-500"
        rows={6}
      />
      <div className="mt-2 text-sm text-gray-500">
        Be as specific as possible including material, dimensions, tool specifications, and machining parameters.
      </div>
    </div>
  );
};

export default TaskDescriptionInput;
