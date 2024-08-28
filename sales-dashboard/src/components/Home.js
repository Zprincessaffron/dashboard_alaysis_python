// src/components/Home.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const [selectedAnalysis, setSelectedAnalysis] = useState('');
  const navigate = useNavigate();

  const handleChange = (event) => {
    setSelectedAnalysis(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (selectedAnalysis) {
      navigate(selectedAnalysis);
    }
  };

  return (
    <div>
      <h1>Choose Analysis</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="analysis">Select Analysis Type:</label>
        <select id="analysis" value={selectedAnalysis} onChange={handleChange}>
          <option value="">--Select--</option>
          <option value="/monthly">Monthly Sales</option>
          <option value="/annual">Annual Sales</option>
          <option value="/halfyearly">Half-Yearly Sales</option>
          <option value="/quarterly">Quarterly Sales</option>
        </select>
        <button type="submit">Go</button>
      </form>
    </div>
  );
};

export default Home;
