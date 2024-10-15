FROM node:16-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy project files and build for production
COPY . .
RUN npm run build

# Serve the application
CMD ["npm", "start"]
