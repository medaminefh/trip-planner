// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import FormPage from './components/FormPage';
import FeatureCard from './components/FeatureCard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/form" element={<FormPage />} />
      </Routes>
    </Router>
  );
}

function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white font-sans">
      {/* Hero Section */}
      <header className="relative flex flex-col items-center justify-center min-h-screen text-center px-4">
        <div className="animate-fade-in">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-800 mb-4">
            Plan Your Truck Trips with Ease
          </h1>
          <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            Trip Planner helps truck drivers and fleet managers create optimized routes, manage Hours of Service (HOS) compliance, and generate daily log sheets effortlessly.
          </p>
          <Link to="/form">
            <button className="bg-sky-800 text-white px-6 py-3 rounded-full text-lg font-semibold cursor-pointer hover:bg-blue-700 transition-all duration-300 shadow-lg">
              Try Me
            </button>
          </Link>
        </div>

        {/* Background Decorative Element */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <svg
            className="absolute bottom-0 left-0 w-full h-auto opacity-20"
            viewBox="0 0 1440 320"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill="#1D4ED8"
              fillOpacity="0.1"
              d="M0,224L48,213.3C96,203,192,181,288,176C384,171,480,181,576,192C672,203,768,213,864,202.7C960,192,1056,160,1152,149.3C1248,139,1344,149,1392,154.7L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            />
          </svg>
        </div>
      </header>

      {/* Features Section */}
      <section className="py-16 px-4">
        <h2 className="text-4xl font-bold text-center text-gray-800 mb-12 animate-slide-up">
          Why Choose Trip Planner?
        </h2>
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            title="Route Optimization"
            description="Calculate the best routes with accurate driving times, distances, and fuel stops."
            icon="🚚"
          />
          <FeatureCard
            title="HOS Compliance"
            description="Ensure compliance with Hours of Service regulations with automatic cycle tracking."
            icon="📅"
          />
          <FeatureCard
            title="Daily Logs"
            description="Generate detailed daily log sheets in PDF format for each trip day."
            icon="📜"
          />
        </div>
      </section>

      {/* Who It's For Section */}
      <section className="py-16 px-4 bg-gray-50">
        <h2 className="text-4xl font-bold text-center text-gray-800 mb-12 animate-slide-up">
          Who Is This For?
        </h2>
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-lg text-gray-600 mb-6">
            Trip Planner is designed for:
          </p>
          <ul className="text-left max-w-md mx-auto space-y-4">
            <li className="flex items-start">
              <span className="text-secondary text-2xl mr-2">•</span>
              <span>Truck drivers managing long-haul trips and HOS compliance.</span>
            </li>
            <li className="flex items-start">
              <span className="text-secondary text-2xl mr-2">•</span>
              <span>Fleet managers needing to plan routes and generate logs for their drivers.</span>
            </li>
            <li className="flex items-start">
              <span className="text-secondary text-2xl mr-2">•</span>
              <span>Logistics companies looking to streamline trip planning and documentation.</span>
            </li>
          </ul>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-gray-600">
        <p>&copy; 2025 Trip Planner. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;