import React from 'react';

function DataQuality() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Data Quality</h2>
      {/* Data Validation iframe */}
      <div className="bg-gray-100 p-4 rounded-md shadow-md mb-6">
        <h3 className="text-lg font-bold mb-2">Data Validation</h3>
        <iframe
          src="https://iis-validations.netlify.app/"
          title="Data Validation"
          className="w-full h-[600px]"
          frameBorder="0"
        ></iframe>
      </div>
      <p className="text-gray-700">This is the Data Quality page.</p>
    </div>
  );
}

export default DataQuality;
