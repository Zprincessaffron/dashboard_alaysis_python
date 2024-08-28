import React, { useState } from 'react';
import axios from 'axios';
import { Bar, Line } from 'react-chartjs-2';
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

const AnnualSales = () => {
    const [selectedYear, setSelectedYear] = useState('');
    const [totalSales, setTotalSales] = useState(null);
    const [salesByProductsChart, setSalesByProductsChart] = useState(null);
    const [quantitySalesPieChart, setQuantitySalesPieChart] = useState(null);
    const [salesComparisonText, setSalesComparisonText] = useState('');
    const [monthlySalesData, setMonthlySalesData] = useState(null);
    const [monthlyProductSalesData, setMonthlyProductSalesData] = useState(null);
    const [annualComparisonChart, setAnnualComparisonChart] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFetchData = async () => {
        setLoading(true);
        setError(null);

        try {
            // Fetch total sales
            const totalSalesRes = await axios.get(`http://localhost:8000/sales/annual/total/?selected_year=${selectedYear}`);
            setTotalSales(totalSalesRes.data.total_sales);

            // Fetch sales by products (bar chart)
            const salesByProductsRes = await axios.get(`http://localhost:8000/sales/annual/by-products/?selected_year=${selectedYear}`);
            setSalesByProductsChart(salesByProductsRes.data.sales_by_products_chart);

            // Fetch quantity pie chart
            const quantitySalesPieRes = await axios.get(`http://localhost:8000/sales/annual/quantity-pie/?selected_year=${selectedYear}`);
            setQuantitySalesPieChart(quantitySalesPieRes.data.quantity_sales_pie_chart);

            // Fetch sales comparison text and chart
            const salesComparisonRes = await axios.get(`http://localhost:8000/sales/annual/comparison/?selected_year=${selectedYear}`);
            setSalesComparisonText(salesComparisonRes.data.sales_comparison_text);
            setAnnualComparisonChart(salesComparisonRes.data.comparison_chart_data);

            // Fetch monthly comparison data for line chart
            const monthlySalesRes = await axios.get(`http://localhost:8000/sales/annual/monthly-comparison/?selected_year=${selectedYear}`);
            setMonthlySalesData(monthlySalesRes.data.chart_data);
            setMonthlyProductSalesData(monthlySalesRes.data.chart_data);

        } catch (err) {
            setError('Failed to fetch data. Please check the backend and data availability.');
        }

        setLoading(false);
    };

    return (
        <div>
            <h1>Sales Dashboard</h1>
            <div>
                <label>Select Year: </label>
                <input 
                    type="text" 
                    value={selectedYear} 
                    onChange={(e) => setSelectedYear(e.target.value)} 
                    placeholder="YYYY" 
                />
                <button onClick={handleFetchData}>Fetch Data</button>
            </div>

            {loading && <p>Loading data...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {totalSales && (
                <div>
                    <h2>Total Sales for {selectedYear}: ${totalSales}</h2>
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

            {salesComparisonText && annualComparisonChart && (
                <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1, marginRight: '20px' }}>
                    <h2>Annual Sales Comparison</h2>
                        <Bar
                            data={{
                                labels: annualComparisonChart.years, // X-axis labels (years)
                                datasets: [{
                                    label: 'Total Sales',
                                    data: annualComparisonChart.total_sales, // Total sales data
                                    backgroundColor: 'rgba(75, 192, 192, 0.5)', // Color for bars
                                    borderColor: 'rgba(75, 192, 192, 1)', // Border color for bars
                                    borderWidth: 1, // Border width
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                }]
                            }}
                            options={{
                                responsive: true,
                                plugins: {
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                },
                                scales: {
                                    x: {
                                        title: {
                                            display: true,
                                            text: 'Year',
                                        },
                                    },
                                    y: {
                                        title: {
                                            display: true,
                                            text: 'Total Sales',
                                        },
                                        beginAtZero: true,
                                    },
                                },
                            }}
                        />
                    </div>
                    <div style={{ flex: 1 }}>
                        <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{salesComparisonText}</pre>
                    </div>
                </div>
            )}

            {monthlySalesData && (
                <div>
                    <h2>Monthly Sales Comparison (Total Sales)</h2>
                    <Line
                        data={{
                            labels: monthlySalesData.months, // X-axis labels (months)
                            datasets: [{
                                label: 'Total Sales',
                                data: monthlySalesData.sales.Total, // Total sales data
                                borderColor: 'rgba(75, 192, 192, 1)', // Line color
                                backgroundColor: 'rgba(75, 192, 192, 0.2)', // Area under the line color
                                fill: true, // Fill area under the line
                                datalabels: {
                                    color: 'black',
                                    display: true,
                                    anchor: 'end',
                                    align: 'top',
                                    formatter: (value) => `$${value.toFixed(2)}`
                                }
                            }]
                        }}
                        options={{
                            responsive: true,
                            plugins: {
                                datalabels: {
                                    color: 'black',
                                    display: true,
                                    anchor: 'end',
                                    align: 'top',
                                    formatter: (value) => `$${value.toFixed(2)}`
                                }
                            },
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Month',
                                    },
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Total Sales',
                                    },
                                    beginAtZero: true,
                                },
                            },
                        }}
                    />
                </div>
            )}

            {monthlyProductSalesData && (
                <div>
                    <h2>Monthly Product Sales Comparison</h2>
                    <Bar
                        data={{
                            labels: monthlyProductSalesData.months, // X-axis labels (months)
                            datasets: [
                                {
                                    label: 'S-P1',
                                    data: monthlyProductSalesData.sales['S-P1'], // Data for S-P1
                                    backgroundColor: 'rgba(255, 99, 132, 0.5)', // Color for S-P1
                                    borderColor: 'rgba(255, 99, 132, 1)', // Border color for S-P1
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                },
                                {
                                    label: 'S-P2',
                                    data: monthlyProductSalesData.sales['S-P2'], // Data for S-P2
                                    backgroundColor: 'rgba(54, 162, 235, 0.5)', // Color for S-P2
                                    borderColor: 'rgba(54, 162, 235, 1)', // Border color for S-P2
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                },
                                {
                                    label: 'S-P3',
                                    data: monthlyProductSalesData.sales['S-P3'], // Data for S-P3
                                    backgroundColor: 'rgba(255, 206, 86, 0.5)', // Color for S-P3
                                    borderColor: 'rgba(255, 206, 86, 1)', // Border color for S-P3
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                },
                                {
                                    label: 'S-P4',
                                    data: monthlyProductSalesData.sales['S-P4'], // Data for S-P4
                                    backgroundColor: 'rgba(153, 102, 255, 0.5)', // Color for S-P4
                                    borderColor: 'rgba(153, 102, 255, 1)', // Border color for S-P4
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                }
                            ]
                        }}
                        options={{
                            responsive: true,
                            plugins: {
                                datalabels: {
                                    color: 'black',
                                    display: true,
                                    anchor: 'end',
                                    align: 'top',
                                    formatter: (value) => `$${value.toFixed(2)}`
                                }
                            },
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Month',
                                    },
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Total Sales',
                                    },
                                    beginAtZero: true,
                                },
                            },
                        }}
                    />
                </div>
            )}
        </div>
    );
};

export default AnnualSales;
