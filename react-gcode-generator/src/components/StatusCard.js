import React from 'react';

const StatusCard = ({ icon: Icon, label, value, color = 'blue' }) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    gray: 'bg-gray-50 text-gray-700 border-gray-200'
  };

  return (
    <div className={`px-4 py-2 rounded-lg border ${colorClasses[color]} flex items-center space-x-2`}>
      <Icon className="h-4 w-4" />
      <div>
        <div className="text-xs font-medium opacity-75">{label}</div>
        <div className="text-sm font-semibold">{value}</div>
      </div>
    </div>
  );
};

export default StatusCard;
