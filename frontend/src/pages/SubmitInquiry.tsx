import React, { useState, ChangeEvent, FormEvent } from 'react';
import { Container, Card, Form, Button, Alert } from 'react-bootstrap';
import { submitInquiry } from '../services/api';
import { InquiryRequest } from '../types';

interface SubmitResult {
  type: 'success' | 'danger';
  message: string;
}

const SubmitInquiry: React.FC = () => {
  const [formData, setFormData] = useState<InquiryRequest>({
    from_email: '',
    from_name: '',
    subject: '',
    content: '',
    category: '',
    priority: 'medium'
  });
  
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await submitInquiry(formData);
      
      setSubmitResult({
        type: 'success',
        message: `Inquiry submitted successfully. ID: ${response.data.inquiry_id}`
      });
      
      // Reset form after successful submission
      setFormData({
        from_email: '',
        from_name: '',
        subject: '',
        content: '',
        category: '',
        priority: 'medium'
      });
    } catch (error: any) {
      console.error('Error submitting inquiry:', error);
      setSubmitResult({
        type: 'danger',
        message: error.response?.data?.detail || 'Failed to submit inquiry. Please try again.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container>
      <h1 className="mb-4">Submit New Inquiry</h1>
      
      {submitResult && (
        <Alert variant={submitResult.type} dismissible onClose={() => setSubmitResult(null)}>
          {submitResult.message}
        </Alert>
      )}
      
      <Card className="dashboard-card">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3" controlId="from_email">
              <Form.Label>Email Address *</Form.Label>
              <Form.Control
                type="email"
                name="from_email"
                value={formData.from_email}
                onChange={handleChange}
                placeholder="Enter your email"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="from_name">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="from_name"
                value={formData.from_name}
                onChange={handleChange}
                placeholder="Enter your name"
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="subject">
              <Form.Label>Subject *</Form.Label>
              <Form.Control
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                placeholder="Enter inquiry subject"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="category">
              <Form.Label>Category</Form.Label>
              <Form.Select
                name="category"
                value={formData.category}
                onChange={handleChange}
              >
                <option value="">Select category</option>
                <option value="prequalification">Prequalification</option>
                <option value="finance">Finance</option>
                <option value="contract">Contract</option>
                <option value="bidding">Bidding</option>
                <option value="issue">Issue</option>
                <option value="information">Information</option>
                <option value="other">Other</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3" controlId="priority">
              <Form.Label>Priority</Form.Label>
              <Form.Select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3" controlId="content">
              <Form.Label>Inquiry Content *</Form.Label>
              <Form.Control
                as="textarea"
                name="content"
                value={formData.content}
                onChange={handleChange}
                placeholder="Enter your inquiry details"
                rows={5}
                required
              />
            </Form.Group>

            <Button 
              variant="primary" 
              type="submit" 
              disabled={isSubmitting}
              className="w-100"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Inquiry'}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default SubmitInquiry;
