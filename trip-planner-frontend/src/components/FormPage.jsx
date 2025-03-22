// src/FormPage.jsx
import React, { useState } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Polyline, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Link } from 'react-router-dom';

// Fix Leaflet marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function FormPage() {
  const [formData, setFormData] = useState({
    current_location: '',
    pickup_location: '',
    dropoff_location: '',
    cycle_used: '',
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const baseUrl = ''

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    setLoading(true);
    e.preventDefault();
    setError(null);
    setResult(null);
    try {
      const response = await axios.post(`${baseUrl}/api/trip/`, formData);
        setLoading(false);
      setResult(response.data);
    } catch (err) {
        setLoading(false);
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Plan Your Trip</h1>
          <Link to="/">
            <button className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600 transition-all">
              Back to Home
            </button>
          </Link>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Current Location</label>
              <input
                type="text"
                name="current_location"
                value={formData.current_location}
                onChange={handleChange}
                className="mt-1 block w-full p-2 border rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Pickup Location</label>
              <input
                type="text"
                name="pickup_location"
                value={formData.pickup_location}
                onChange={handleChange}
                className="mt-1 block w-full p-2 border rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Dropoff Location</label>
              <input
                type="text"
                name="dropoff_location"
                value={formData.dropoff_location}
                onChange={handleChange}
                className="mt-1 block w-full p-2 border rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Cycle Used (hrs)</label>
              <input
                type="number"
                name="cycle_used"
                value={formData.cycle_used}
                onChange={handleChange}
                className="mt-1 block w-full p-2 border rounded-md"
                min="0"
                max="70"
                step="0.1"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="mt-4 w-full bg-blue-600 text-white p-2 cursor-pointer rounded-md hover:bg-blue-700 transition-all"
          >
            {loading ? 'Loading...' : 'Plan Trip'}
          </button>

        </form>

        {/* Loading */}
        {loading && <p className="text-gray-700 text-center mb-4">Loading...</p>}


        {/* Error */}
        {error && <p className="text-red-500 text-center mb-4">{error}</p>}

        {/* Results */}
        {result && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Trip Results</h2>

            {/* Route Instructions */}
            <div className="mb-6">
              <h3 className="text-xl font-medium">Route Instructions</h3>
              <ol className="list-decimal list-inside mt-2">
                {result.route_instructions.map((instr, idx) => (
                  <li key={idx} className="text-gray-700">{instr}</li>
                ))}
              </ol>
              <p className="mt-2">Total Distance: {result.total_distance.toFixed(1)} miles</p>
              <p>Total Time: {result.total_time.toFixed(1)} hours</p>
              <p className={result.compliance.includes('Warning') ? 'text-red-500' : 'text-green-500'}>
                {result.compliance}
              </p>
            </div>

            {/* Map */}
            <div className="mb-6">
              <h3 className="text-xl font-medium">Route Map</h3>
              <MapContainer
                bounds={result.coordinates}
                style={{ height: '400px', width: '100%' }}
                className="mt-2 rounded-md"
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                />
                <Polyline positions={result.coordinates} color="blue" />
                {result.coordinates.map((coord, idx) => (
                  <Marker key={idx} position={coord}>
                    <Popup>{idx === 0 ? 'Start' : idx === 1 ? 'Pickup' : 'Dropoff'}</Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>

            {/* Daily Logs */}
            <div>
              <h3 className="text-xl font-medium">Daily Logs</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                {result.eld_logs.map((log) => (
                  <div key={log.day} className="border p-4 rounded-md">
                    <h4 className="font-semibold">Day {log.day}</h4>
                    <p>Distance: {log.distance.toFixed(1)} miles</p>
                    <p>Drive Time: {log.drive_time.toFixed(1)} hours</p>
                    <p>Total Time: {log.total_time.toFixed(1)} hours</p>
                    <img
                      src={`${baseUrl}${log.image}`}
                      alt={`ELD Log Day ${log.day}`}
                      className="mt-2 w-full rounded-md"
                    />
                  </div>
                ))}
                
              </div>
              {result.daily_logs.map((log) => (<a
                      href={`${baseUrl}${log.pdf}`}
                      target='_blank'
                      rel='noreferrer'
                      download={`daily_log_day_${log.day}.pdf`}
                      className="mt-2 inline-block bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-all"
                    >
                      Download Daily Log (Day {log.day})
                    </a>))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FormPage;