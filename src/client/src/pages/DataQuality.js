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
          className="w-full h-[400px] md:h-[600px] rounded-md shadow-md"
          frameBorder="0"
        ></iframe>
      </div>
      
      {/* Data Test iframe */}
      <div className="bg-gray-100 p-4 rounded-md shadow-md mb-6">
        <h3 className="text-lg font-bold mb-2">Data Test</h3>
        <iframe
          src="https://datatestbtcrnn.netlify.app/"
          title="Data Test"
          className="w-full h-[400px] md:h-[600px] rounded-md shadow-md"
          frameBorder="0"
        ></iframe>
      </div>

    </div>
  );
}

export default DataQuality;
