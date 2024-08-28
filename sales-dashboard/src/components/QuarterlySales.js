import React, { useState } from 'react';
import axios from 'axios';
import { Bar, Line } from 'react-chartjs-2';
import Chart from 'chart.js/auto';
import ChartDataLabels from 'chartjs-plugin-datalabels';

const QuarterlySales = () => {
    const [selectedQuarter, setSelectedQuarter] = useState('');
    const [monthlySalesData, setMonthlySalesData] = useState(null);
    const [comparisonText, setComparisonText] = useState('');
    const [salesByProductsChart, setSalesByProductsChart] = useState(null);
    const [quantitySalesPieChart, setQuantitySalesPieChart] = useState(null);
    const [totalQuarterlySales, setTotalQuarterlySales] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFetchData = async () => {
        setLoading(true);
        setError(null);
    
        try {
            // Fetch total quarterly sales
            const totalQuarterlySalesRes = await axios.get(`http://localhost:8000/sales/quarterly/total/?selected_quarter=${selectedQuarter}`);
            setTotalQuarterlySales(totalQuarterlySalesRes.data.total_sales);
    
            // Fetch sales by products (bar chart)
            const salesByProductsRes = await axios.get(`http://localhost:8000/sales/quarterly/by-products/?selected_quarter=${selectedQuarter}`);
            setSalesByProductsChart(salesByProductsRes.data.sales_by_products_chart);
    
            // Fetch quantity pie chart
            const quantitySalesPieRes = await axios.get(`http://localhost:8000/sales/quarterly/quantity-pie/?selected_quarter=${selectedQuarter}`);
            setQuantitySalesPieChart(quantitySalesPieRes.data.quantity_sales_pie_chart);
    
            // Fetch quarterly sales comparison text (removed the bar chart part)
            const comparisonRes = await axios.get(`http://localhost:8000/sales/quarterly/comparison/?selected_quarter=${selectedQuarter}`);
            const { sales_comparison_text } = comparisonRes.data;
            
            setComparisonText(sales_comparison_text);
    
            // Fetch monthly sales comparison chart
            const monthlySalesRes = await axios.get(`http://localhost:8000/sales/quarterly/monthly-comparison/?selected_quarter=${selectedQuarter}`);
            setMonthlySalesData(monthlySalesRes.data.monthly_sales_data);
    
        } catch (err) {
            setError('Failed to fetch data. Please check the backend and data availability.');
        }
    
        setLoading(false);
    };
    

    return (
        <div>
            <h1>Sales Dashboard</h1>
            <div>
                <label>Select Quarter: </label>
                <input 
                    type="text" 
                    value={selectedQuarter} 
                    onChange={(e) => setSelectedQuarter(e.target.value)} 
                    placeholder="YYYY-Q1" 
                />
                <button onClick={handleFetchData}>Fetch Data</button>
            </div>

            {loading && <p>Loading data...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {totalQuarterlySales !== null && (
                <div>
                    <h2>Total Sales for {selectedQuarter}: ${totalQuarterlySales}</h2>
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
                <div style={{ marginBottom: '20px', position: 'relative' }}>
                    <h2>Quarterly Sales Comparison</h2>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{comparisonText}</pre>
                </div>
            )}
      
            {monthlySalesData && monthlySalesData.months && (
                <div>
                    <h2>Monthly Sales Comparison for {selectedQuarter}</h2>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        <Bar
                            data={{
                                labels: monthlySalesData.months.map(month => `Month ${month}`),
                                datasets: [
                                    {
                                        label: 'S-P1',
                                        data: monthlySalesData['S-P1'] || [],
                                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                                        borderColor: 'rgba(75, 192, 192, 1)',
                                        borderWidth: 1,
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
                                        data: monthlySalesData['S-P2'] || [],
                                        backgroundColor: 'rgba(153, 102, 255, 0.5)',
                                        borderColor: 'rgba(153, 102, 255, 1)',
                                        borderWidth: 1,
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
                                        data: monthlySalesData['S-P3'] || [],
                                        backgroundColor: 'rgba(255, 159, 64, 0.5)',
                                        borderColor: 'rgba(255, 159, 64, 1)',
                                        borderWidth: 1,
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
                                        data: monthlySalesData['S-P4'] || [],
                                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                                        borderColor: 'rgba(255, 99, 132, 1)',
                                        borderWidth: 1,
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
                                plugins: {
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                }
                            }}
                        />
                        <Line
                            data={{
                                labels: monthlySalesData.months.map(month => `Month ${month}`),
                                datasets: [
                                    {
                                        label: 'Total Sales',
                                        data: monthlySalesData['Total'] || [],
                                        borderColor: 'rgba(75, 192, 192, 1)',
                                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                        fill: true,
                                        tension: 0.1,
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
                                plugins: {
                                    datalabels: {
                                        color: 'black',
                                        display: true,
                                        anchor: 'end',
                                        align: 'top',
                                        formatter: (value) => `$${value.toFixed(2)}`
                                    }
                                }
                            }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default QuarterlySales;
