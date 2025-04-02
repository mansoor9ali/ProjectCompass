import React from 'react';
import { Navbar as BootstrapNavbar, Container, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import './Layout.css';

const Navbar: React.FC = () => {
  return (
    <BootstrapNavbar bg="primary" variant="dark" expand="lg" className="mb-3">
      <Container fluid>
        <BootstrapNavbar.Brand as={Link} to="/">
          ProjectCompass Dashboard
        </BootstrapNavbar.Brand>
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
            <Nav.Link as={Link} to="/inquiries">Inquiries</Nav.Link>
            <Nav.Link as={Link} to="/submit">Submit Inquiry</Nav.Link>
          </Nav>
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar;
