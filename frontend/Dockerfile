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
COPY package*.json ./

# Install dependencies using 'npm ci' for fast, reproducible installs
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Change ownership of the app directory
RUN chown -R node:node /app

# Switch to the non-root user
USER node

# Expose the Vite development port
EXPOSE 5173

# Run the development server, exposing it to the host machine
# The '--' ensures the following arguments are passed to the 'dev' script
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]


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

# Install curl for the healthcheck and gettext for envsubst (runtime env variables)
RUN apk add --no-cache curl gettext

# Copy the custom Nginx configuration
# This config is optimized for Single Page Applications (SPAs)
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Remove the default Nginx welcome page
RUN rm /usr/share/nginx/html/*

# Copy the built static files from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy the entrypoint script that injects environment variables at runtime
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the production port
EXPOSE 80

# Healthcheck to verify that Nginx is running and serving content
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost/ || exit 1

# The entrypoint script will run first, then it will execute the CMD
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
