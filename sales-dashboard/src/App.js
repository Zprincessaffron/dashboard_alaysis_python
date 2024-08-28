import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MonthlySales from './components/MonthlySales';
import AnnualSales from './components/AnnualSales';
import HalfYearlySales from './components/HalfYearlySales';
import QuarterlySales from './components/QuarterlySales';
import Home from './components/Home'; // Import the Home component
import './App.css'; // Ensure your CSS file is included

const App = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} /> {/* Home route */}
          <Route path="/monthly" element={<MonthlySales />} />
          <Route path="/annual" element={<AnnualSales />} />
          <Route path="/halfyearly" element={<HalfYearlySales />} />
          <Route path="/quarterly" element={<QuarterlySales />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
