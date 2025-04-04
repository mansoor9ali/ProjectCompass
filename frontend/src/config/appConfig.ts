/**
 * Application configuration based on environment
 */

interface AppConfig {
  apiBaseUrl: string;
  refreshIntervals: {
    dashboard: number;
    inquiries: number;
  };
}

// Default configuration
const defaultConfig: AppConfig = {
  apiBaseUrl: 'http://localhost:8000/api',
  refreshIntervals: {
    dashboard: 120000, // 2 minutes (increased from 30 seconds)
    inquiries: 180000  // 3 minutes (increased from 60 seconds)
  }
};

// Environment-specific overrides
const environmentConfigs: Record<string, Partial<AppConfig>> = {
  development: {
    // Development-specific settings (same as default)

  },
  test: {
    // Test environment settings
    refreshIntervals: {
      dashboard: 300000, // 5 minutes
      inquiries: 300000  // 5 minutes
    }
  },
  production: {
    // Production environment settings
    apiBaseUrl: 'http://projectcompass-api:8000/api', // Relative path for same-origin API in production
    refreshIntervals: {
      dashboard: 120000,  // 2 minutes
      inquiries: 180000   // 3 minutes
    }
  }
};

// Determine current environment
const getEnvironment = (): string => {
  return process.env.NODE_ENV || 'development';
};

// Build config by merging default with environment-specific settings
const buildConfig = (): AppConfig => {
  const env = getEnvironment();
  const envConfig = environmentConfigs[env] || {};
  
  return {
    ...defaultConfig,
    ...envConfig,
    refreshIntervals: {
      ...defaultConfig.refreshIntervals,
      ...(envConfig.refreshIntervals || {})
    }
  };
};

// Export the configuration
const appConfig = buildConfig();
console.log(appConfig);
export default appConfig;
