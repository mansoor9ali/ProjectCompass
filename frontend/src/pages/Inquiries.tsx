import React, { useState, useEffect } from 'react';
import { Container, Table, Card, Badge, Spinner } from 'react-bootstrap';
import { getRecentInquiries } from '../services/api';
import { Inquiry } from '../types';

const Inquiries: React.FC = () => {
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInquiries = async () => {
      try {
        setLoading(true);
        const response = await getRecentInquiries();
        setInquiries(response.data.inquiries);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching inquiries:', err);
        setError('Failed to load inquiries. Please try again later.');
        setLoading(false);
      }
    };

    fetchInquiries();
  }, []);

  const getPriorityBadge = (priority: string): JSX.Element => {
    switch (priority) {
      case 'high':
        return <Badge bg="danger">High</Badge>;
      case 'medium':
        return <Badge bg="warning">Medium</Badge>;
      case 'low':
        return <Badge bg="success">Low</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
  };

  const getStatusBadge = (status: string): JSX.Element => {
    switch (status) {
      case 'new':
        return <Badge bg="info">New</Badge>;
      case 'assigned':
        return <Badge bg="primary">Assigned</Badge>;
      case 'in_progress':
        return <Badge bg="warning">In Progress</Badge>;
      case 'resolved':
        return <Badge bg="success">Resolved</Badge>;
      case 'closed':
        return <Badge bg="secondary">Closed</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
    }
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

  return (
    <Container fluid>
      <h1 className="mb-4">Recent Inquiries</h1>
      <Card className="dashboard-card">
        <Card.Body>
          <Table responsive hover>
            <thead>
              <tr>
                <th>ID</th>
                <th>Vendor</th>
                <th>Subject</th>
                <th>Category</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Assigned To</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {inquiries.length > 0 ? (
                inquiries.map((inquiry) => (
                  <tr key={inquiry.id}>
                    <td>{inquiry.id}</td>
                    <td>{inquiry.vendor_name}</td>
                    <td>{inquiry.subject}</td>
                    <td>{inquiry.category}</td>
                    <td>{getPriorityBadge(inquiry.priority)}</td>
                    <td>{getStatusBadge(inquiry.status)}</td>
                    <td>{inquiry.assigned_to}</td>
                    <td>{new Date(inquiry.created_at).toLocaleString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="text-center">No inquiries found</td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Inquiries;
