import React, { useState } from 'react';
import axios from 'axios';
import { Bar, Line } from 'react-chartjs-2';
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

const HalfYearlySales = () => {
    const [selectedHalfYear, setSelectedHalfYear] = useState('');
    const [totalSales, setTotalSales] = useState(null);
    const [salesByProductsChart, setSalesByProductsChart] = useState(null);
    const [quantitySalesPieChart, setQuantitySalesPieChart] = useState(null);
    const [comparisonText, setComparisonText] = useState('');
    const [monthlySalesData, setMonthlySalesData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFetchData = async () => {
        setLoading(true);
        setError(null);

        try {
            // Fetch total half-yearly sales
            const totalSalesRes = await axios.get(`http://localhost:8000/sales/halfyearly/total/?selected_halfyear=${selectedHalfYear}`);
            setTotalSales(totalSalesRes.data.total_sales);

            // Fetch sales by products
            const salesByProductsRes = await axios.get(`http://localhost:8000/sales/halfyearly/by-products/?selected_halfyear=${selectedHalfYear}`);
            setSalesByProductsChart(salesByProductsRes.data.sales_by_products_chart);

            // Fetch quantity sales pie chart
            const quantitySalesPieRes = await axios.get(`http://localhost:8000/sales/halfyearly/quantity-pie/?selected_halfyear=${selectedHalfYear}`);
            setQuantitySalesPieChart(quantitySalesPieRes.data.quantity_sales_pie_chart);

            // Fetch comparison text
            const comparisonRes = await axios.get(`http://localhost:8000/sales/halfyearly/comparison/?selected_halfyear=${selectedHalfYear}`);
            setComparisonText(comparisonRes.data.sales_comparison_text);

            // Fetch monthly sales data
            const monthlySalesRes = await axios.get(`http://localhost:8000/sales/halfyearly/monthly-comparison/?selected_halfyear=${selectedHalfYear}`);
            setMonthlySalesData(monthlySalesRes.data);

        } catch (err) {
            setError('Failed to fetch data. Please check the backend and data availability.');
        }

        setLoading(false);
    };

    return (
        <div>
            <h1>Half-Yearly Sales Dashboard</h1>
            <div>
                <label>Select Half-Year (e.g., 2011-H1 or 2011-H2): </label>
                <input
                    type="text"
                    value={selectedHalfYear}
                    onChange={(e) => setSelectedHalfYear(e.target.value)}
                    placeholder="YYYY-H1 or YYYY-H2"
                />
                <button onClick={handleFetchData}>Fetch Data</button>
            </div>

            {loading && <p>Loading data...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {totalSales !== null && (
                <div>
                    <h2>Total Sales for {selectedHalfYear}: ${totalSales.toFixed(2)}</h2>
                </div>
            )}

            {salesByProductsChart && (
                <div>
                    <h2>Sales by Products</h2>
                    <img src={`data:image/png;base64,${salesByProductsChart}`} alt="Sales by Products Chart" />
                </div>
            )}

            {quantitySalesPieChart && (
                <div>
                    <h2>Quantity Sales Pie Chart</h2>
                    <img src={`data:image/png;base64,${quantitySalesPieChart}`} alt="Quantity Sales Pie Chart" />
                </div>
            )}

            {comparisonText && (
                <div style={{ marginBottom: '20px' }}>
                    <h2>Sales Comparison</h2>
                    <pre>{comparisonText}</pre>
                </div>
            )}

            {monthlySalesData && monthlySalesData.chart_data && (
                <div>
                    <h2>Monthly Sales Comparison for {selectedHalfYear}</h2>
                    
                    {/* Total Monthly Sales Line Chart */}
                    <Line
                        data={{
                            labels: monthlySalesData.chart_data.months,
                            datasets: [
                                {
                                    label: 'Total Sales',
                                    data: monthlySalesData.chart_data.sales.Total,
                                    borderColor: 'rgba(75, 192, 192, 1)',
                                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                    fill: true,
                                    tension: 0.1,
                                }
                            ]
                        }}
                        options={{
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Month'
                                    }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Total Sales ($)'
                                    },
                                    beginAtZero: true
                                }
                            },
                            plugins: {
                                datalabels: {
                                    display: false
                                }
                            }
                        }}
                    />
                    
                    {/* Monthly Sales Comparison by Product Column Chart */}
                    <Bar
                        data={{
                            labels: monthlySalesData.chart_data.months,
                            datasets: [
                                {
                                    label: 'Sales - S-P1',
                                    data: monthlySalesData.chart_data.sales['S-P1'],
                                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                    borderColor: 'rgba(255, 99, 132, 1)',
                                    borderWidth: 1
                                },
                                {
                                    label: 'Sales - S-P2',
                                    data: monthlySalesData.chart_data.sales['S-P2'],
                                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                    borderColor: 'rgba(54, 162, 235, 1)',
                                    borderWidth: 1
                                },
                                {
                                    label: 'Sales - S-P3',
                                    data: monthlySalesData.chart_data.sales['S-P3'],
                                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                                    borderColor: 'rgba(255, 206, 86, 1)',
                                    borderWidth: 1
                                },
                                {
                                    label: 'Sales - S-P4',
                                    data: monthlySalesData.chart_data.sales['S-P4'],
                                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                    borderColor: 'rgba(75, 192, 192, 1)',
                                    borderWidth: 1
                                }
                            ]
                        }}
                        options={{
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'top',
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(tooltipItem) {
                                            return `${tooltipItem.dataset.label}: $${tooltipItem.raw.toFixed(2)}`;
                                        }
                                    }
                                }
                            },
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Month'
                                    }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Sales ($)'
                                    },
                                    beginAtZero: true
                                }
                            }
                        }}
                    />
                </div>
            )}
        </div>
    );
};

export default HalfYearlySales;
