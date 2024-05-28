import React, { useEffect, useState } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";

function ProductionEvaluation() {
  const [metricsData, setMetricsData] = useState([]);
  const [productionModelMetrics, setProductionModelMetrics] = useState(null);
  const [latestMetrics, setLatestMetrics] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:3001/prodeval");
        const data = response.data.metrics;
        setMetricsData(data);

        // Extract the latest metrics
        const mostRecentMetrics = data[0];
        setLatestMetrics(mostRecentMetrics);

        // Extract the metrics for the production model
        setProductionModelMetrics(mostRecentMetrics);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  // Extracting data for each metric
  const mseData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.mse
  }));
  const evsData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.evs
  }));
  const maeData = metricsData.map((metric) => ({
    x: metric.end_time,
    y: metric.mae
  }));

  // Reverse the order of timestamps
  const reversedTimestamps = metricsData
    .map((metric) => metric.end_time)
    .reverse();

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Production Evaluation</h2>
      {/* Metrics for production model */}
      {productionModelMetrics && (
        <div className="bg-blue-200 p-4 rounded-md shadow-md mb-6">
          <h3 className="text-lg font-bold mb-2">Production Model Metrics</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-md shadow-md">
              <p className="font-bold">MSE:</p>
              <p>{latestMetrics.mse}</p>
            </div>
            <div className="bg-white p-4 rounded-md shadow-md">
              <p className="font-bold">EVS:</p>
              <p>{latestMetrics.evs}</p>
            </div>
            <div className="bg-white p-4 rounded-md shadow-md">
              <p className="font-bold">MAE:</p>
              <p>{latestMetrics.mae}</p>
            </div>
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          {/* MSE Chart */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-2">Mean Squared Error (MSE)</h3>
            <Line
              data={{
                labels: reversedTimestamps,
                datasets: [
                  {
                    label: "MSE",
                    data: mseData,
                    borderColor: "rgba(75, 192, 192, 1)",
                    fill: false
                  }
                ]
              }}
            />
          </div>
        </div>
        <div>
          {/* EVS Chart */}
          <div className="mb-8">
            <h3 className="text-lg font-bold mb-2">Explained Variance Score (EVS)</h3>
            <Line
              data={{
                labels: reversedTimestamps,
                datasets: [
                  {
                    label: "EVS",
                    data: evsData,
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
            <h3 className="text-lg font-bold mb-2">Mean Absolute Error (MAE)</h3>
            <Line
              data={{
                labels: reversedTimestamps,
                datasets: [
                  {
                    label: "MAE",
                    data: maeData,
                    borderColor: "rgba(54, 162, 235, 1)",
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

export default ProductionEvaluation;
