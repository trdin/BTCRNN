import React from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import Evaluation from './Evaluation';
import ProductionEvaluation from './ProductionEvaluation';
import DataQuality from './DataQuality';

function AdminPanel() {
  return (
    <div className="flex h-full">
      <nav className="w-1/5 bg-gray-800 text-white p-5">
        <ul className="space-y-4">
          <li>
            <Link to="evaluation" className="block p-2 hover:bg-gray-700 rounded">Evaluation</Link>
          </li>
          <li>
            <Link to="production-evaluation" className="block p-2 hover:bg-gray-700 rounded">Production Evaluation</Link>
          </li>
          <li>
            <Link to="data-quality" className="block p-2 hover:bg-gray-700 rounded">Data Quality</Link>
          </li>
        </ul>
      </nav>
      <div className="flex-1 p-10 bg-gray-100">
        <Routes>
          <Route path="evaluation" element={<Evaluation />} />
          <Route path="production-evaluation" element={<ProductionEvaluation />} />
          <Route path="data-quality" element={<DataQuality />} />
        </Routes>
      </div>
    </div>
  );
}

export default AdminPanel;
