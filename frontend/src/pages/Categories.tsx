import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Spinner } from 'react-bootstrap';
import { Pie } from 'react-chartjs-2';
import { getCategoryDistribution } from '../services/api';
import { Category } from '../types';

const Categories: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const response = await getCategoryDistribution();
        setCategories(response.data.categories);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching category distribution:', err);
        setError('Failed to load category data. Please try again later.');
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  // Prepare chart data
  const chartData = {
    labels: categories.map(cat => cat.name),
    datasets: [
      {
        data: categories.map(cat => cat.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(153, 102, 255, 0.7)',
          'rgba(255, 159, 64, 0.7)',
          'rgba(201, 203, 207, 0.7)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(201, 203, 207, 1)'
        ],
        borderWidth: 1
      }
    ]
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <div className="alert alert-danger">{error}</div>
      </Container>
    );
  }

  const totalInquiries = categories.reduce((sum, cat) => sum + cat.count, 0);

  return (
    <Container fluid>
      <h1 className="mb-4">Inquiry Categories</h1>
      
      <Row>
        <Col lg={6}>
          <Card className="dashboard-card mb-4">
            <Card.Body>
              <Card.Title>Category Distribution</Card.Title>
              <div className="chart-container">
                <Pie 
                  data={chartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'right'
                      }
                    }
                  }}
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={6}>
          <Card className="dashboard-card">
            <Card.Body>
              <Card.Title>Category Breakdown</Card.Title>
              <div className="table-responsive">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Count</th>
                      <th>Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categories.map(cat => (
                      <tr key={cat.name}>
                        <td style={{textTransform: 'capitalize'}}>{cat.name.replace('_', ' ')}</td>
                        <td>{cat.count}</td>
                        <td>{((cat.count / totalInquiries) * 100).toFixed(1)}%</td>
                      </tr>
                    ))}
                    <tr className="table-active">
                      <td><strong>Total</strong></td>
                      <td><strong>{totalInquiries}</strong></td>
                      <td><strong>100%</strong></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Categories;
