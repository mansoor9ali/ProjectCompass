import axios from 'axios';
import { 
  SystemStatus, 
  InquiryRequest, 
  InquiriesResponse, 
  DepartmentsResponse,
  CategoriesResponse
} from '../types';
import appConfig from '../config/appConfig';

// Create axios instance with base URL
const api = axios.create({
  baseURL: appConfig.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json'
  }
});

// System endpoints
export const getSystemStatus = () => 
  api.get<SystemStatus>('/system/status');

// Inquiries endpoints
export const getRecentInquiries = (limit = 10) => 
  api.get<InquiriesResponse>(`/inquiries/recent?limit=${limit}`);

export const submitInquiry = (inquiryData: InquiryRequest) => 
  api.post<{ status: string; message: string; inquiry_id: string }>('/inquiries/submit', inquiryData);

// Department endpoints
export const getDepartmentStats = () => 
  api.get<DepartmentsResponse>('/departments/stats');

// Categories endpoints
export const getCategoryDistribution = () => 
  api.get<CategoriesResponse>('/categories/distribution');

export default api;
