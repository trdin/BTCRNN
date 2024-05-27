# Use Node.js as the base image
FROM node:16-alpine as build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

ARG REACT_APP_API_URL=https://p01--api--lmdv97v8xxkc.code.run
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Copy the rest of the application
COPY . .

# Build the React app
RUN npm run build

# Use Nginx as the base image for serving static files
FROM nginx:alpine

# Copy the build files from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
