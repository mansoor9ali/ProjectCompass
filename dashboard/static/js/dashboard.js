/**
 * ProjectCompass Dashboard JavaScript
 * Provides interactive functionality for the ProjectCompass dashboard
 */

// Wait for the document to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard components
    initDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadSystemStatus();
    loadRecentInquiries();
    loadDepartmentStats();
    loadCategoryDistribution();
    
    // Initialize charts
    initCharts();
});

/**
 * Initialize the dashboard components
 */
function initDashboard() {
    console.log('Initializing dashboard...');
    
    // Set up tab navigation
    const tabLinks = document.querySelectorAll('.nav-link');
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            tabLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show the corresponding tab content
            const targetId = this.getAttribute('href');
            const tabContents = document.querySelectorAll('.tab-pane');
            tabContents.forEach(tab => {
                tab.classList.remove('show', 'active');
                if (tab.id === targetId.substring(1)) {
                    tab.classList.add('show', 'active');
                }
            });
        });
    });
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Refresh dashboard button
    const refreshButton = document.getElementById('refresh-dashboard');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            loadSystemStatus();
            loadRecentInquiries();
            loadDepartmentStats();
            loadCategoryDistribution();
            updateCharts();
        });
    }
    
    // Submit inquiry button
    const submitButton = document.getElementById('submit-inquiry');
    if (submitButton) {
        submitButton.addEventListener('click', submitInquiry);
    }
    
    // Category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterInquiries);
    }
    
    // Priority filter
    const priorityFilter = document.getElementById('priority-filter');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', filterInquiries);
    }
    
    // Status filter
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterInquiries);
    }
    
    // Search inquiries
    const searchInput = document.getElementById('search-inquiries');
    if (searchInput) {
        searchInput.addEventListener('keyup', filterInquiries);
    }
}

/**
 * Load system status data from API
 */
function loadSystemStatus() {
    // In a real implementation, this would fetch from the API
    // For demo purposes, simulate an API call
    
    console.log('Loading system status...');
    
    // Simulate API delay
    setTimeout(() => {
        const statusData = {
            status: "operational",
            active_inquiries: 42,
            total_inquiries: 156,
            notifications_sent: 98,
            performance_metrics: {
                avg_response_time: 2.3, // hours
                categorization_accuracy: 0.92,
                routing_efficiency: 0.88
            }
        };
        
        updateSystemStatusUI(statusData);
    }, 500);
    
    // In a real implementation, this would be:
    /*
    fetch('/api/system/status')
        .then(response => response.json())
        .then(data => {
            updateSystemStatusUI(data);
        })
        .catch(error => {
            console.error('Error fetching system status:', error);
        });
    */
}

/**
 * Update the system status UI elements
 */
function updateSystemStatusUI(data) {
    // Update status cards
    document.getElementById('system-status').textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
    document.getElementById('active-inquiries').textContent = data.active_inquiries;
    document.getElementById('total-inquiries').textContent = data.total_inquiries;
    document.getElementById('notifications-sent').textContent = data.notifications_sent;
    
    // Update status icon
    const statusIcon = document.querySelector('#system-status').parentElement.parentElement.nextElementSibling.querySelector('i');
    
    if (data.status === 'operational') {
        statusIcon.className = 'bi bi-check-circle-fill text-success fs-2';
    } else if (data.status === 'degraded') {
        statusIcon.className = 'bi bi-exclamation-triangle-fill text-warning fs-2';
    } else {
        statusIcon.className = 'bi bi-x-circle-fill text-danger fs-2';
    }
}

/**
 * Load recent inquiries from API
 */
function loadRecentInquiries() {
    console.log('Loading recent inquiries...');
    
    // Simulate API call
    setTimeout(() => {
        const inquiriesData = {
            inquiries: [
                {
                    id: "INQ-12345ABC",
                    vendor_name: "Acme Corp",
                    subject: "Prequalification Application Status",
                    category: "prequalification",
                    priority: "medium",
                    status: "assigned",
                    assigned_to: "registration.specialist@example.com",
                    created_at: "2025-03-29T08:30:00Z"
                },
                {
                    id: "INQ-67890DEF",
                    vendor_name: "TechSupplies Inc",
                    subject: "Invoice Payment Issue",
                    category: "finance",
                    priority: "high",
                    status: "in_progress",
                    assigned_to: "finance.senior@example.com",
                    created_at: "2025-03-29T10:15:00Z"
                },
                {
                    id: "INQ-ABCDE123",
                    vendor_name: "GlobalLogistics Ltd",
                    subject: "Contract Renewal Questions",
                    category: "contract",
                    priority: "medium",
                    status: "assigned",
                    assigned_to: "legal.specialist@example.com",
                    created_at: "2025-03-29T11:05:00Z"
                },
                {
                    id: "INQ-FGHIJ456",
                    vendor_name: "QualityParts Co",
                    subject: "Portal Access Issue",
                    category: "issue",
                    priority: "critical",
                    status: "in_progress",
                    assigned_to: "support.senior@example.com",
                    created_at: "2025-03-29T09:45:00Z"
                },
                {
                    id: "INQ-KLMNO789",
                    vendor_name: "FastFreight Inc",
                    subject: "Bid Submission Clarification",
                    category: "bidding",
                    priority: "high",
                    status: "assigned",
                    assigned_to: "procurement.specialist@example.com",
                    created_at: "2025-03-29T07:30:00Z"
                }
            ]
        };
        
        updateRecentInquiriesUI(inquiriesData);
    }, 700);
    
    // In a real implementation:
    /*
    fetch('/api/inquiries/recent')
        .then(response => response.json())
        .then(data => {
            updateRecentInquiriesUI(data);
        })
        .catch(error => {
            console.error('Error fetching recent inquiries:', error);
        });
    */
}

/**
 * Update the recent inquiries table
 */
function updateRecentInquiriesUI(data) {
    const tableBody = document.getElementById('recent-inquiries-body');
    if (!tableBody) return;
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add new rows
    data.inquiries.forEach(inquiry => {
        const row = document.createElement('tr');
        
        // Format date
        const createdDate = new Date(inquiry.created_at);
        const formattedDate = createdDate.toLocaleString();
        
        // Create row content
        row.innerHTML = `
            <td>${inquiry.id}</td>
            <td>${inquiry.vendor_name}</td>
            <td>${inquiry.subject}</td>
            <td>${inquiry.category}</td>
            <td><span class="badge priority-${inquiry.priority}">${inquiry.priority}</span></td>
            <td><span class="badge status-${inquiry.status}">${inquiry.status.replace('_', ' ')}</span></td>
            <td>${inquiry.assigned_to.split('@')[0]}</td>
            <td>${formattedDate}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Also update the inquiries table if it exists
    const inquiriesBody = document.getElementById('inquiries-body');
    if (inquiriesBody) {
        inquiriesBody.innerHTML = '';
        
        data.inquiries.forEach(inquiry => {
            const row = document.createElement('tr');
            
            // Format date
            const createdDate = new Date(inquiry.created_at);
            const formattedDate = createdDate.toLocaleString();
            
            // Create row content with actions column
            row.innerHTML = `
                <td>${inquiry.id}</td>
                <td>${inquiry.vendor_name}</td>
                <td>${inquiry.subject}</td>
                <td>${inquiry.category}</td>
                <td><span class="badge priority-${inquiry.priority}">${inquiry.priority}</span></td>
                <td><span class="badge status-${inquiry.status}">${inquiry.status.replace('_', ' ')}</span></td>
                <td>${inquiry.assigned_to.split('@')[0]}</td>
                <td>${formattedDate}</td>
                <td>
                    <button class="btn btn-sm btn-info view-inquiry" data-id="${inquiry.id}">View</button>
                    <button class="btn btn-sm btn-primary edit-inquiry" data-id="${inquiry.id}">Edit</button>
                </td>
            `;
            
            inquiriesBody.appendChild(row);
        });
    }
}

/**
 * Load department statistics
 */
function loadDepartmentStats() {
    console.log('Loading department statistics...');
    
    // Simulate API call
    setTimeout(() => {
        const departmentData = {
            departments: [
                { name: "Vendor Registration", load: 5, avg_response_time: 2.3 },
                { name: "Finance", load: 8, avg_response_time: 4.1 },
                { name: "Legal", load: 3, avg_response_time: 6.5 },
                { name: "Procurement", load: 7, avg_response_time: 3.2 },
                { name: "Technical Support", load: 10, avg_response_time: 1.5 },
                { name: "Vendor Relations", load: 4, avg_response_time: 2.8 }
            ]
        };
        
        updateDepartmentStatsUI(departmentData);
        updateDepartmentChart(departmentData);
    }, 600);
    
    // In a real implementation:
    /*
    fetch('/api/departments/stats')
        .then(response => response.json())
        .then(data => {
            updateDepartmentStatsUI(data);
            updateDepartmentChart(data);
        })
        .catch(error => {
            console.error('Error fetching department stats:', error);
        });
    */
}

/**
 * Update department statistics UI
 */
function updateDepartmentStatsUI(data) {
    const container = document.getElementById('department-stats-container');
    if (!container) return;
    
    // Clear existing cards
    container.innerHTML = '';
    
    // Add department cards
    data.departments.forEach(dept => {
        const col = document.createElement('div');
        col.className = 'col-xl-4 col-md-6 mb-4';
        
        col.innerHTML = `
            <div class="card shadow h-100 py-2 department-card">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="department-title text-primary text-uppercase mb-1">
                                ${dept.name}
                            </div>
                            <div class="department-metric mb-0">${dept.load}</div>
                            <div class="department-subtitle">Current Inquiries</div>
                            <div class="mt-2">
                                <div class="small font-weight-bold">Avg. Response Time: ${dept.avg_response_time.toFixed(1)} hours</div>
                                <div class="progress progress-sm mb-2">
                                    <div class="progress-bar bg-info" role="progressbar" style="width: ${Math.min(dept.avg_response_time * 10, 100)}%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-auto">
                            <i class="bi bi-people-fill text-gray-300 fs-2"></i>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

/**
 * Load category distribution data
 */
function loadCategoryDistribution() {
    console.log('Loading category distribution...');
    
    // Simulate API call
    setTimeout(() => {
        const categoryData = {
            categories: [
                { name: "prequalification", count: 15 },
                { name: "finance", count: 23 },
                { name: "contract", count: 8 },
                { name: "bidding", count: 12 },
                { name: "issue", count: 18 },
                { name: "information", count: 10 },
                { name: "other", count: 5 }
            ]
        };
        
        updateCategoryChart(categoryData);
    }, 800);
    
    // In a real implementation:
    /*
    fetch('/api/categories/distribution')
        .then(response => response.json())
        .then(data => {
            updateCategoryChart(data);
        })
        .catch(error => {
            console.error('Error fetching category distribution:', error);
        });
    */
}

/**
 * Initialize charts
 */
function initCharts() {
    // Set up inquiries chart (line chart)
    setupInquiriesChart();
    
    // Set up category chart (pie chart)
    // Data will be loaded from API
    
    // Set up department load chart (bar chart)
    // Data will be loaded from API
}

/**
 * Set up inquiries chart
 */
function setupInquiriesChart() {
    const ctx = document.getElementById('inquiriesChart');
    if (!ctx) return;
    
    // Sample data - in a real implementation, this would come from the API
    const chartData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
            {
                label: 'Total Inquiries',
                data: [10, 15, 18, 22, 30, 35, 42, 48, 52, 60, 65, 70],
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                pointBackgroundColor: '#4e73df',
                pointBorderColor: '#4e73df',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: '#4e73df',
                pointHoverBorderColor: '#4e73df',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: true,
                tension: 0.3
            },
            {
                label: 'Critical Inquiries',
                data: [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15],
                borderColor: '#e74a3b',
                backgroundColor: 'rgba(231, 74, 59, 0.05)',
                pointBackgroundColor: '#e74a3b',
                pointBorderColor: '#e74a3b',
                pointHoverRadius: 3,
                pointHoverBackgroundColor: '#e74a3b',
                pointHoverBorderColor: '#e74a3b',
                pointHitRadius: 10,
                pointBorderWidth: 2,
                fill: true,
                tension: 0.3
            }
        ]
    };
    
    window.inquiriesChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Update category distribution chart
 */
function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    // Prepare chart data
    const labels = data.categories.map(cat => cat.name.charAt(0).toUpperCase() + cat.name.slice(1));
    const values = data.categories.map(cat => cat.count);
    
    // Chart colors
    const backgroundColors = [
        '#4e73df', // Primary
        '#1cc88a', // Success
        '#36b9cc', // Info
        '#f6c23e', // Warning
        '#e74a3b', // Danger
        '#858796', // Secondary
        '#5a5c69'  // Dark
    ];
    
    const chartData = {
        labels: labels,
        datasets: [{
            data: values,
            backgroundColor: backgroundColors,
            hoverBackgroundColor: backgroundColors.map(color => color + 'dd'),
            hoverBorderColor: "rgba(234, 236, 244, 1)",
        }]
    };
    
    // Create or update chart
    if (window.categoryChart) {
        window.categoryChart.data = chartData;
        window.categoryChart.update();
    } else {
        window.categoryChart = new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * Update department load chart
 */
function updateDepartmentChart(data) {
    const ctx = document.getElementById('departmentLoadChart');
    if (!ctx) return;
    
    // Prepare chart data
    const labels = data.departments.map(dept => dept.name);
    const values = data.departments.map(dept => dept.load);
    
    const chartData = {
        labels: labels,
        datasets: [{
            label: 'Current Inquiries',
            data: values,
            backgroundColor: '#4e73df',
            hoverBackgroundColor: '#2e59d9',
            borderWidth: 0
        }]
    };
    
    // Create or update chart
    if (window.departmentChart) {
        window.departmentChart.data = chartData;
        window.departmentChart.update();
    } else {
        window.departmentChart = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

/**
 * Update all charts with new data
 */
function updateCharts() {
    // In a real implementation, this would fetch new data from the API
    // For now, we'll just use our simulated data loading functions
    loadCategoryDistribution();
    loadDepartmentStats();
}

/**
 * Submit a new inquiry
 */
function submitInquiry() {
    const fromEmail = document.getElementById('from-email').value;
    const fromName = document.getElementById('from-name').value;
    const subject = document.getElementById('subject').value;
    const content = document.getElementById('content').value;
    const category = document.getElementById('category').value;
    const priority = document.getElementById('priority').value;
    
    if (!fromEmail || !subject || !content) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Create inquiry data
    const inquiryData = {
        from_email: fromEmail,
        from_name: fromName,
        subject: subject,
        content: content,
        category: category || null,
        priority: priority || null
    };
    
    console.log('Submitting inquiry:', inquiryData);
    
    // Simulate API call
    setTimeout(() => {
        // Simulate successful response
        const response = {
            status: "success",
            message: "Inquiry submitted successfully",
            inquiry_id: `INQ-MANUAL${Math.floor(Math.random() * 1000)}`
        };
        
        // Update UI
        alert(`${response.message} (ID: ${response.inquiry_id})`);
        
        // Close modal and reset form
        const modal = document.getElementById('newInquiryModal');
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        bootstrapModal.hide();
        
        document.getElementById('new-inquiry-form').reset();
        
        // Refresh data
        loadSystemStatus();
        loadRecentInquiries();
    }, 1000);
    
    // In a real implementation:
    /*
    fetch('/api/inquiries/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(inquiryData)
    })
    .then(response => response.json())
    .then(data => {
        alert(`${data.message} (ID: ${data.inquiry_id})`);
        
        // Close modal and reset form
        const modal = document.getElementById('newInquiryModal');
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        bootstrapModal.hide();
        
        document.getElementById('new-inquiry-form').reset();
        
        // Refresh data
        loadSystemStatus();
        loadRecentInquiries();
    })
    .catch(error => {
        console.error('Error submitting inquiry:', error);
        alert('Error submitting inquiry. Please try again.');
    });
    */
}

/**
 * Filter inquiries based on selected filters
 */
function filterInquiries() {
    // Get filter values
    const categoryFilter = document.getElementById('category-filter').value;
    const priorityFilter = document.getElementById('priority-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    const searchQuery = document.getElementById('search-inquiries').value.toLowerCase();
    
    // Get all rows in the table
    const rows = document.querySelectorAll('#inquiries-body tr');
    
    // Filter rows
    rows.forEach(row => {
        const category = row.children[3].textContent.toLowerCase();
        const priority = row.children[4].textContent.toLowerCase();
        const status = row.children[5].textContent.toLowerCase();
        const rowText = row.textContent.toLowerCase();
        
        // Check if row matches all filters
        const matchesCategory = categoryFilter === 'all' || category === categoryFilter;
        const matchesPriority = priorityFilter === 'all' || priority === priorityFilter;
        const matchesStatus = statusFilter === 'all' || status === statusFilter;
        const matchesSearch = searchQuery === '' || rowText.includes(searchQuery);
        
        // Show or hide row based on filter matches
        if (matchesCategory && matchesPriority && matchesStatus && matchesSearch) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}
