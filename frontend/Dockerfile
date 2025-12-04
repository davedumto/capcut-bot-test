FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (needed for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port (Railway sets PORT dynamically)
EXPOSE 3000

# Start the application
CMD ["npm", "start"]