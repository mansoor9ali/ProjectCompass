import React, { useState, useEffect } from 'react';
import { Container, Card, Row, Col, Table, Spinner, ProgressBar } from 'react-bootstrap';
import { Bar } from 'react-chartjs-2';
import { getDepartmentStats } from '../services/api';
import { Department } from '../types';

const Departments: React.FC = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        setLoading(true);
        const response = await getDepartmentStats();
        setDepartments(response.data.departments);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching department stats:', err);
        setError('Failed to load department data. Please try again later.');
        setLoading(false);
      }
    };

    fetchDepartments();
  }, []);

  // Prepare chart data
  const chartData = {
    labels: departments.map(dept => dept.name),
    datasets: [
      {
        label: 'Average Response Time (hours)',
        data: departments.map(dept => dept.avg_response_time),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
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

  // Helper function to determine load color
  const getLoadColor = (load: number): 'success' | 'warning' | 'danger' => {
    if (load <= 4) return 'success';
    if (load <= 7) return 'warning';
    return 'danger';
  };

  return (
    <Container fluid>
      <h1 className="mb-4">Department Performance</h1>
      
      <Row>
        <Col lg={12}>
          <Card className="dashboard-card mb-4">
            <Card.Body>
              <Card.Title>Department Workload</Card.Title>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Department</th>
                    <th>Current Load</th>
                    <th>Load Status</th>
                    <th>Avg. Response Time (hours)</th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map(dept => (
                    <tr key={dept.name}>
                      <td>{dept.name}</td>
                      <td>{dept.load}</td>
                      <td>
                        <ProgressBar 
                          now={dept.load * 10} 
                          variant={getLoadColor(dept.load)} 
                          label={`${dept.load}/10`} 
                        />
                      </td>
                      <td>{dept.avg_response_time}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row>
        <Col>
          <Card className="dashboard-card">
            <Card.Body>
              <Card.Title>Average Response Time by Department</Card.Title>
              <div className="chart-container">
                <Bar 
                  data={chartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        title: {
                          display: true,
                          text: 'Hours'
                        }
                      }
                    },
                    plugins: {
                      legend: {
                        display: false
                      },
                      title: {
                        display: true,
                        text: 'Average Response Time (Lower is Better)'
                      }
                    }
                  }}
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Departments;
