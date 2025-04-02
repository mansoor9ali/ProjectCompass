FROM node:16-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all frontend files
COPY . .

# Build the React app
RUN npm run build

# Install serve to run the application
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Set environment variables to connect to API
ENV REACT_APP_API_URL=http://projectcompass-api:8000
ENV NODE_ENV=production

# Start the app with the correct configuration for React Router
# The -s flag ensures all routes are redirected to index.html for client-side routing
CMD ["serve", "-s", "build", "-l", "3000", "--single"]
