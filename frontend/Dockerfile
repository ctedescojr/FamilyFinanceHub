#
# Frontend Dockerfile - React + Vite + Tailwind CSS
# This is a multi-stage Dockerfile for both development and production.
#

# --- Development Stage ---
# This stage is for running the Vite dev server with hot-reloading.
FROM node:24-alpine AS development

# Set the working directory
WORKDIR /app

# Copy dependency definition files
# The entrypoint script will handle dependency installation at runtime.
COPY package*.json ./

# Install gosu for permission management
RUN apk add --no-cache gosu

# Copy the rest of the application source code (including the scripts folder)
COPY . .

# The container will be started as root and the entrypoint will use gosu to step down to the node user.
# This is necessary to fix potential file permission issues with bind mounts.

# Copy the entrypoint script and make it executable
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the Vite development port
EXPOSE 5173

# The entrypoint script will handle project initialization and run the main command
ENTRYPOINT ["entrypoint.sh"]
CMD ["npm", "run", "dev"]


# --- Build Stage ---
# This stage builds the application for production.
FROM node:24-alpine AS build

# Set the working directory
WORKDIR /app

# Copy dependency definition files
COPY package*.json ./

# Install all dependencies (including devDependencies needed for the build)
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Build the static files for production
RUN npm run build


# --- Production Stage ---
# This stage serves the built static files using Nginx.
FROM nginx:1.27-alpine AS production

# Install curl for the healthcheck
RUN apk add --no-cache curl

# Copy the custom Nginx configuration (assuming you have one at nginx/nginx.conf)
# This config should be optimized for Single Page Applications (SPAs)
# COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Remove the default Nginx welcome page
RUN rm -rf /usr/share/nginx/html/*

# Copy the built static files from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose the production port
EXPOSE 80

# Healthcheck to verify that Nginx is running and serving content
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
