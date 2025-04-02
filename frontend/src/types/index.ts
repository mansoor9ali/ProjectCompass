// System status interfaces
export interface SystemStatus {
  status: string;
  active_inquiries: number;
  total_inquiries: number;
  notifications_sent: number;
  performance_metrics?: Record<string, any>;
}

// Inquiry interfaces
export interface Inquiry {
  id: string;
  vendor_name: string;
  subject: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'new' | 'assigned' | 'in_progress' | 'resolved' | 'closed';
  assigned_to: string;
  created_at: string;
}

export interface InquiryRequest {
  from_email: string;
  from_name?: string;
  subject: string;
  content: string;
  category?: string;
  priority?: 'low' | 'medium' | 'high';
}

export interface InquiriesResponse {
  inquiries: Inquiry[];
  total: number;
}

// Department interfaces
export interface Department {
  name: string;
  load: number;
  avg_response_time: number;
}

export interface DepartmentsResponse {
  departments: Department[];
}

// Category interfaces
export interface Category {
  name: string;
  count: number;
}

export interface CategoriesResponse {
  categories: Category[];
}
