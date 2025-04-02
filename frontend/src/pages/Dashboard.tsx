import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Alert, Spinner, Button } from 'react-bootstrap';
import { Bar, Doughnut } from 'react-chartjs-2';
import { 
  Chart as ChartJS, 
  ArcElement, 
  Tooltip, 
  Legend, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title 
} from 'chart.js';
import { getSystemStatus, getDepartmentStats, getCategoryDistribution } from '../services/api';
import { SystemStatus, Department, Category } from '../types';
import { formatApiError } from '../utils/errorHandler';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const Dashboard: React.FC = () => {
  // Switch to traditional useState approach instead of custom hooks
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    status: 'loading',
    active_inquiries: 0,
    total_inquiries: 0,
    notifications_sent: 0
  });
  
  const [departmentStats, setDepartmentStats] = useState<Department[]>([]);
  const [categoryData, setCategoryData] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Function to fetch all dashboard data
  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch all data in parallel
      const [statusResponse, departmentResponse, categoryResponse] = await Promise.all([
        getSystemStatus(),
        getDepartmentStats(),
        getCategoryDistribution()
      ]);
      
      setSystemStatus(statusResponse.data);
      setDepartmentStats(departmentResponse.data.departments);
      setCategoryData(categoryResponse.data.categories);
      setLastUpdated(new Date());
      setIsLoading(false);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(formatApiError(err));
      setIsLoading(false);
    }
  };

  // Only fetch data on initial component mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Prepare department chart data
  const departmentChartData = {
    labels: departmentStats.map(dept => dept.name),
    datasets: [
      {
        label: 'Current Load',
        data: departmentStats.map(dept => dept.load),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      },
      {
        label: 'Avg Response Time (hours)',
        data: departmentStats.map(dept => dept.avg_response_time),
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      }
    ]
  };

  // Prepare category chart data
  const categoryChartData = {
    labels: categoryData.map(cat => cat.name),
    datasets: [
      {
        data: categoryData.map(cat => cat.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)',
          'rgba(255, 159, 64, 0.5)',
          'rgba(201, 203, 207, 0.5)'
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

  // Get status class based on system status
  const getStatusClass = (status: string): string => {
    switch (status) {
      case 'operational':
        return 'status-operational';
      case 'warning':
        return 'status-warning';
      case 'error':
        return 'status-error';
      default:
        return '';
    }
  };

  if (isLoading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading dashboard data...</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert variant="danger">{error}</Alert>
        <Button variant="primary" onClick={fetchDashboardData}>
          Retry
        </Button>
      </Container>
    );
  }

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>ProjectCompass Dashboard</h1>
        <div>
          <small className="text-muted me-2">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </small>
          <Button 
            variant="outline-primary" 
            size="sm" 
            onClick={fetchDashboardData}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh Data'}
          </Button>
        </div>
      </div>
      
      {/* System Status Section */}
      <Row className="mb-4">
        <Col lg={3} md={6} sm={12} className="mb-3">
          <Card className="dashboard-card h-100">
            <Card.Body>
              <Card.Title>System Status</Card.Title>
              <div className={`status-card ${getStatusClass(systemStatus.status)}`}>
                {systemStatus.status.toUpperCase()}
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={3} md={6} sm={12} className="mb-3">
          <Card className="dashboard-card h-100">
            <Card.Body>
              <Card.Title>Active Inquiries</Card.Title>
              <h2 className="text-center">{systemStatus.active_inquiries}</h2>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={3} md={6} sm={12} className="mb-3">
          <Card className="dashboard-card h-100">
            <Card.Body>
              <Card.Title>Total Inquiries</Card.Title>
              <h2 className="text-center">{systemStatus.total_inquiries}</h2>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={3} md={6} sm={12} className="mb-3">
          <Card className="dashboard-card h-100">
            <Card.Body>
              <Card.Title>Notifications Sent</Card.Title>
              <h2 className="text-center">{systemStatus.notifications_sent}</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Charts Section */}
      <Row>
        <Col lg={6} className="mb-4">
          <Card className="dashboard-card">
            <Card.Body>
              <Card.Title>Department Workload & Response Time</Card.Title>
              <div className="chart-container">
                <Bar 
                  data={departmentChartData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true
                      }
                    }
                  }}
                />
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={6} className="mb-4">
          <Card className="dashboard-card">
            <Card.Body>
              <Card.Title>Inquiry Categories Distribution</Card.Title>
              <div className="chart-container">
                <Doughnut 
                  data={categoryChartData}
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
      </Row>
    </Container>
  );
};

export default Dashboard;
