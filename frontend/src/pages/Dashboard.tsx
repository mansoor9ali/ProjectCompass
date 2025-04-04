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
      
      // Safely set data with proper error handling
      setSystemStatus(statusResponse.data || {
        status: 'unknown',
        active_inquiries: 0,
        total_inquiries: 0,
        notifications_sent: 0
      });
      
      // Check if departments property exists in the response
      if (departmentResponse?.data?.departments) {
        setDepartmentStats(departmentResponse.data.departments);
      } else {
        console.warn('No department data found in API response');
        setDepartmentStats([]);
      }
      
      // Check if categories property exists in the response
      if (categoryResponse?.data?.categories) {
        setCategoryData(categoryResponse.data.categories);
      } else {
        console.warn('No category data found in API response');
        setCategoryData([]);
      }
      
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

  // Prepare department chart data only if departmentStats is available
  const departmentChartData = {
    labels: departmentStats?.map(dept => dept.name) || [],
    datasets: [
      {
        label: 'Current Load',
        data: departmentStats?.map(dept => dept.load) || [],
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      },
      {
        label: 'Avg Response Time (hours)',
        data: departmentStats?.map(dept => dept.avg_response_time) || [],
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      }
    ]
  };

  // Prepare category chart data only if categoryData is available
  const categoryChartData = {
    labels: categoryData?.map(cat => cat.name) || [],
    datasets: [
      {
        label: 'Inquiries by Category',
        data: categoryData?.map(cat => cat.count) || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <Container>
      <Row className="mb-4 mt-4">
        <Col>
          <h1>Dashboard</h1>
          <div className="d-flex justify-content-between align-items-center">
            <p className="text-muted">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
            {/* Manual refresh button */}
            <Button 
              variant="primary" 
              onClick={fetchDashboardData} 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" className="me-2" />
                  Refreshing...
                </>
              ) : (
                'Refresh Data'
              )}
            </Button>
          </div>
        </Col>
      </Row>

      {error && (
        <Row className="mb-4">
          <Col>
            <Alert variant="danger">
              {error}
            </Alert>
          </Col>
        </Row>
      )}

      {isLoading ? (
        <Row className="justify-content-center my-5">
          <Col xs="auto">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </Col>
        </Row>
      ) : (
        <>
          <Row className="mb-4">
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <Card.Title>System Status</Card.Title>
                  <h3 className={`mt-3 ${systemStatus.status === 'operational' ? 'text-success' : 'text-warning'}`}>
                    {systemStatus.status === 'operational' ? 'Operational' : 'Attention Needed'}
                  </h3>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <Card.Title>Active Inquiries</Card.Title>
                  <h3 className="mt-3">{systemStatus.active_inquiries}</h3>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <Card.Title>Total Inquiries</Card.Title>
                  <h3 className="mt-3">{systemStatus.total_inquiries}</h3>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center h-100">
                <Card.Body>
                  <Card.Title>Notifications</Card.Title>
                  <h3 className="mt-3">{systemStatus.notifications_sent}</h3>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mb-4">
            <Col lg={8}>
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Department Performance</Card.Title>
                  {departmentStats.length > 0 ? (
                    <Bar data={departmentChartData} />
                  ) : (
                    <div className="text-center text-muted py-5">
                      <p>No department data available</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
            <Col lg={4}>
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>Category Distribution</Card.Title>
                  {categoryData.length > 0 ? (
                    <Doughnut data={categoryChartData} />
                  ) : (
                    <div className="text-center text-muted py-5">
                      <p>No category data available</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </Container>
  );
};

export default Dashboard;
