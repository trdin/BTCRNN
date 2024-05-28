// src/pages/Evaluation.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";

function Evaluation() {
  const [metricsData, setMetricsData] = useState([]);
  const [productionModelMetrics, setProductionModelMetrics] = useState(null);
  const [latestMetrics, setLatestMetrics] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:3001/eval");
        const data = response.data.metrics;
        setMetricsData(data);

        data.sort((a, b) => new Date(b.end_time) - new Date(a.end_time));

        // Extract the metrics with the most recent date (the first item after sorting)
        const mostRecentMetrics = data[0];
        setLatestMetrics(mostRecentMetrics);

        // Find the last metrics for the production model
        const productionModelLastMetrics =
          response.data.current_production_model_metrics;
        setProductionModelMetrics(productionModelLastMetrics);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  // Extracting data for each metric
  const mseProductionData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.MSE_production
  }));
  const mseStagingData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.MSE_staging
  }));

  const evsProductionData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.EVS_production
  }));
  const evsStagingData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.EVS_staging
  }));

  const maeProductionData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.MAE_production
  }));
  const maeStagingData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.MAE_staging
  }));

  // Reverse the order of timestamps
  const reversedTimestamps = metricsData
    .map((metric) => metric.end_time)
    .reverse();

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Evaluation</h2>
      {/* Metrics for production model */}
      {productionModelMetrics && (
        <div className="bg-blue-200 p-4 rounded-md shadow-md mb-6">
        <h3 className="text-lg font-bold mb-2">Production Model Metrics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-md shadow-md">
            <p className="font-bold">Loss:</p>
            <p>{productionModelMetrics.loss}</p>
          </div>
          <div className="bg-white p-4 rounded-md shadow-md">
            <p className="font-bold">Validation Loss:</p>
            <p>{productionModelMetrics.validation_loss}</p>
          </div>
          <div className="bg-white p-4 rounded-md shadow-md">
            <p className="font-bold">MSE:</p>
            <p>{latestMetrics.MSE_production}</p>
          </div>
          <div className="bg-white p-4 rounded-md shadow-md">
            <p className="font-bold">EVS:</p>
            <p>{latestMetrics.EVS_production}</p>
          </div>
          <div className="bg-white p-4 rounded-md shadow-md">
            <p className="font-bold">MAE:</p>
            <p>{latestMetrics.MAE_production}</p>
          </div>
        </div>
      </div>
      
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          {/* MSE Chart */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-2">Mean Squared Error (MSE)</h3>
            <Line
              data={{
                labels: reversedTimestamps,
                datasets: [
                  {
                    label: "Production",
                    data: mseProductionData,
                    borderColor: "rgba(75, 192, 192, 1)",
                    fill: false
                  },
                  {
                    label: "Staging",
                    data: mseStagingData,
                    borderColor: "rgba(255, 99, 132, 1)",
                    fill: false
                  }
                ]
              }}
            />
          </div>

          {/* EVS Chart */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-2">
              Explained Variance Score (EVS)
            </h3>
            <Line
              data={{
                labels: reversedTimestamps,
                datasets: [
                  {
                    label: "Production",
                    data: evsProductionData,
                    borderColor: "rgba(75, 192, 192, 1)",
                    fill: false
                  },
                  {
                    label: "Staging",
                    data: evsStagingData,
                    borderColor: "rgba(255, 99, 132, 1)",
                    fill: false
                  }
                ]
              }}
            />
          </div>
        </div>

        <div>
          {/* MAE Chart */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-2">
              Mean Absolute Error (MAE)
            </h3>
            <Line
              data={{
                labels: reversedTimestamps,
                datasets: [
                  {
                    label: "Production",
                    data: maeProductionData,
                    borderColor: "rgba(75, 192, 192, 1)",
                    fill: false
                  },
                  {
                    label: "Staging",
                    data: maeStagingData,
                    borderColor: "rgba(255, 99, 132, 1)",
                    fill: false
                  }
                ]
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Evaluation;
