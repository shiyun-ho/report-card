FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Create .next directory with proper permissions
RUN mkdir -p /app/.next && \
    addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Set environment for development
ENV NODE_ENV=development
ENV WATCHPACK_POLLING=true

# Start the development server
CMD ["npm", "run", "dev"]