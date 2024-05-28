import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import axios from "axios";
import Chart from "chart.js/auto";

function Home() {
  const [chartData, setChartData] = useState({});
  const [loading, setLoading] = useState(true);
  const [predictionData, setPredictionData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch BTC data
        const btcResponse = await axios.get(`${process.env.REACT_APP_API_URL}/btc`);
        const btcData = btcResponse.data;

        // Fetch prediction data
        const predictResponse = await axios.get(`${process.env.REACT_APP_API_URL}/predict`);
        const predictData = predictResponse.data;

        setPredictionData(predictData);

        // Combine BTC data and prediction data
        const combinedData = [...btcData, ...predictData];

        // Set chart data
        setChartData({
          labels: combinedData.map((entry) => entry.timestamp),
          datasets: [
            {
              label: "Prediction",
              data: predictData.map((entry) => ({
                x: entry.timestamp,
                y: entry.price
              })),
              borderColor: "red",
              fill: true
            },
            {
              label: "Bitcoin Price (USD)",
              data: combinedData.map((entry) => ({
                x: entry.timestamp,
                y: entry.price
              })),
              borderColor: "rgba(75,192,192,1)",
              fill: false
            }
          ]
        });
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold underline">BITCOIN PREDICTION</h1>
      <div style={{ display: "flex" }}>
        <div style={{ width: "50%" }}>
          {loading ? <p>Loading...</p> : <Line data={chartData} />}
        </div>
        <div style={{ width: "50%" }}>
          <h2 className="text-3xl font-bold underline">Model Prediction</h2>
          {predictionData.map((prediction, index) => (
            <div className="text-xl font-bold " key={index}>
              <p>Prediction BTC PRICE: {prediction.price}</p>
              <p>Timestamp: {prediction.timestamp}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;
