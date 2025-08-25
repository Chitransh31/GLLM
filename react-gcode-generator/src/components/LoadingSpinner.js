import React from 'react';
import { Loader } from 'lucide-react';

const LoadingSpinner = ({ message = 'Loading...', size = 'medium' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-6 w-6',
    large: 'h-8 w-8'
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="relative">
        <Loader className={`${sizeClasses[size]} animate-spin text-primary-600`} />
      </div>
      <p className="mt-4 text-gray-600 text-sm">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
