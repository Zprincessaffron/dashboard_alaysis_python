import React, { useState } from 'react';
import axios from 'axios';
import { Container, Row, Col, Form, Button, Card } from 'react-bootstrap';
import { Bar } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../App.css'; // Adjust path if needed
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register components needed for the chart
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const MonthlySales = () => {
  const [selectedMonth, setSelectedMonth] = useState('');
  const [totalSales, setTotalSales] = useState(null);
  const [byProductsChart, setByProductsChart] = useState('');
  const [quantityPieChart, setQuantityPieChart] = useState('');
  const [weeklySalesChart, setWeeklySalesChart] = useState(null); 
  const [salesComparison, setSalesComparison] = useState('');
  const [comparisonChartData, setComparisonChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
  
      // Fetch total sales
      const totalSalesResponse = await axios.get(
        `http://localhost:8000/sales/total/?selected_month=${selectedMonth}`
      );
      console.log("Total Sales Response:", totalSalesResponse.data);
      setTotalSales(totalSalesResponse.data.total_sales);
  
      // Fetch sales by products chart
      const byProductsResponse = await axios.get(
        `http://localhost:8000/sales/by-products/?selected_month=${selectedMonth}`
      );
      console.log("By Products Chart Response:", byProductsResponse.data);
      setByProductsChart(byProductsResponse.data.sales_by_products_chart);
  
      // Fetch quantity pie chart
      const quantityPieResponse = await axios.get(
        `http://localhost:8000/sales/quantity-pie/?selected_month=${selectedMonth}`
      );
      console.log("Quantity Pie Chart Response:", quantityPieResponse.data);
      setQuantityPieChart(quantityPieResponse.data.quantity_sales_pie_chart);
  
      // Fetch weekly sales chart
      const weeklySalesResponse = await axios.get(
        `http://localhost:8000/sales/weekly/?selected_month=${selectedMonth}`
      );
      console.log("Weekly Sales Response:", weeklySalesResponse.data);
      setWeeklySalesChart(weeklySalesResponse.data.weekly_sales_chart);

      // Fetch sales comparison
      const comparisonResponse = await axios.get(`http://localhost:8000/sales/comparison/?selected_month=${selectedMonth}`);
      setSalesComparison(comparisonResponse.data.sales_comparison_text);
  
      // Prepare comparison chart data
      const [comparisonMonth, previousMonth] = comparisonResponse.data.sales_comparison_text.split('\n').map(line => line.split(': ')[1].replace('$', '').trim());
      setComparisonChartData({
        labels: ['Current Month', 'Previous Month'],
        datasets: [
          {
            label: 'Sales Comparison',
            data: [parseFloat(comparisonMonth), parseFloat(previousMonth)],
            backgroundColor: ['rgba(54, 162, 235, 0.5)', 'rgba(255, 99, 132, 0.5)'],
            borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
            borderWidth: 1,
          },
        ],
      });

    } catch (error) {
      console.error('Error fetching data', error);
    }
  }; 

  return (
    <Container className="dashboard-container">
      <Row className="mb-4">
        <Col>
          <Card className="form-card">
            <Card.Body>
              <Form>
                <Form.Group controlId="formMonth">
                  <Form.Label>Select Month</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter month in YYYY-MM format"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}
                    className="form-control-lg"
                  />
                </Form.Group>
                <Button
                  variant="primary"
                  onClick={fetchData}
                  className="mt-3"
                  disabled={loading}
                >
                  {loading ? 'Loading...' : 'Fetch Data'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {error && <p className="error-message">{error}</p>}

      {/* Total Sales */}
      <Row className="chart-row">
        <Col lg={10} className="chart-col">
          <Card className="chart-card total-sales-card">
            <Card.Body>
              <h4>Total Sales</h4>
              {totalSales !== null && !isNaN(totalSales) ? (
                <p className="total-sales">${totalSales.toFixed(2)}</p>
              ) : (
                <p>No data available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Sales by Products & Quantity Pie Chart */}
      <Row className="chart-row">
        <Col lg={6} className="chart-col">
          <Card className="chart-card">
            <Card.Body>
              <h4>Sales by Products</h4>
              {byProductsChart ? (
                <img
                  src={`data:image/png;base64,${byProductsChart}`}
                  alt="Sales by Products"
                  className="chart-img"
                />
              ) : (
                <p>No chart available</p>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4} className="chart-col">
          <Card className="chart-card">
            <Card.Body>
              <h4>Quantity Pie Chart</h4>
              {quantityPieChart ? (
                <img
                  src={`data:image/png;base64,${quantityPieChart}`}
                  alt="Quantity Pie Chart"
                  className="chart-img"
                />
              ) : (
                <p>No chart available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Weekly Sales Chart */}
      <Row className="chart-row">
        <Col lg={6} className="chart-col">
          <Card className="chart-card long-chart-card">
            <Card.Body>
              <h4>Weekly Sales</h4>
              {weeklySalesChart ? (
                <img
                  src={`data:image/png;base64,${weeklySalesChart}`}
                  alt="Weekly Sales Chart"
                  className="chart-img"
                />
              ) : (
                <p>No chart available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      


      {/* Monthly Sales Comparison */}
      
        <Col lg={5} className="chart-col">
          <Card className="chart-card">
            <Card.Body>
              <h4>Monthly Sales Comparison</h4>
              <pre>{salesComparison}</pre>
              {comparisonChartData ? (
                <Bar
                  data={comparisonChartData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      tooltip: {
                        callbacks: {
                          label: (context) => `$${context.raw.toFixed(2)}`,
                        },
                      },
                    },
                  }}
                />
              ) : (
                <p>No comparison data available</p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default MonthlySales;
