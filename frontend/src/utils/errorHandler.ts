import { AxiosError } from 'axios';

// Generic error handling utility for API errors
export const formatApiError = (error: unknown): string => {
  if (error instanceof Error) {
    // Check if it's an Axios error
    const axiosError = error as AxiosError<{ detail?: string }>;
    
    if (axiosError.response) {
      // Return backend error message if available
      return axiosError.response.data?.detail || 
             `Error ${axiosError.response.status}: ${axiosError.response.statusText}`;
    } else if (axiosError.request) {
      // Request was made but no response received
      return 'No response received from server. Please check your connection.';
    }
    
    // Regular error with message
    return error.message;
  }
  
  // Fallback for unknown error types
  return 'An unexpected error occurred. Please try again.';
};
