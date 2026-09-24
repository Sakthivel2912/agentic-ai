/**
 * AI Council - Documents Page
 */
import React from 'react';

export const DocumentsPage: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Documents</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Document management will be displayed here.</p>
        <p className="text-sm text-gray-500 mt-2">Upload, manage, and index documents for RAG.</p>
      </div>
    </div>
  );
};
