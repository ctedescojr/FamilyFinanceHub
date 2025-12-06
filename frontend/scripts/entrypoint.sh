#!/bin/sh

# Abort the script if any command fails
set -e

# --- User and Permission Management ---
# Get the host user's UID and GID from environment variables
PUID=${HOST_UID:-1000}
PGID=${HOST_GID:-1000}

# Check if the node user's UID and GID match the host's
CURRENT_UID=$(id -u node)
CURRENT_GID=$(id -g node)

if [ "$CURRENT_UID" != "$PUID" ] || [ "$CURRENT_GID" != "$PGID" ]; then
    echo "---> Updating node user UID to $PUID and GID to $PGID..."
    # Change the UID and GID of the node user
    groupmod -o -g "$PGID" node
    usermod -o -u "$PUID" node
fi

# --- Project Initialization ---
# Check if package.json exists. If not, initialize the Vite project.
if [ ! -f "package.json" ]; then
    echo "---> Initializing Vite + React project in a temporary directory..."

    # Define and create a temporary directory to ensure a clean slate for Vite
    TEMP_DIR="/tmp/vite-project"
    mkdir -p "$TEMP_DIR"
    chown -R node:node "$TEMP_DIR"

    # Scaffold the project inside the temp dir. Using a subshell `()` means we don't have to `cd` back.
    (cd "$TEMP_DIR" && gosu node npm create vite@latest . -- --template react)

    # Move the generated files (including dotfiles) from the temp dir to the current directory (/app)
    mv "$TEMP_DIR"/* "$TEMP_DIR"/.[!.]* .

    # Clean up the now-empty temporary directory
    rm -rf "$TEMP_DIR"

    # !!! IMPORTANT FIX: Change ownership of the new files BEFORE running npm install.
    chown -R node:node .

    # Install Node.js dependencies
    echo "---> Installing dependencies..."
    gosu node npm install

    # --- Install & Configure TailwindCSS (The Vite Plugin Way) ---
    echo "---> Installing and configuring TailwindCSS with the Vite plugin..."

    # Install TailwindCSS and the dedicated Vite plugin
    gosu node npm install -D tailwindcss @tailwindcss/vite

    # Create the tailwind.config.js file to scan the correct source files
    cat <<'EOF' > tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

    # Overwrite vite.config.js to add the TailwindCSS plugin and Docker-friendly server settings.
    cat <<'EOF' > vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0', // Required for Docker container port mapping
    port: 5173,
    watch: {
      usePolling: true, // Helps with file change detection in some Docker setups
    },
  },
});
EOF

    # Overwrite src/index.css with the single import directive
    cat <<'EOF' > src/index.css
@import "tailwindcss";
EOF

    # Create a sample App component with Tailwind classes to verify setup
    cat <<'EOF' > src/App.jsx
function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center font-sans">
      <header className="text-center p-4">
        <h1 className="text-5xl font-bold text-cyan-400 mb-4 animate-pulse">
          Vite + React + TailwindCSS
        </h1>
        <p className="text-lg text-gray-400">
          Your automated frontend environment is ready!
        </p>
        <p className="mt-8 text-sm text-gray-500">
          Start editing <code className="bg-gray-700 p-1 rounded">src/App.jsx</code>
        </p>
      </header>
    </div>
  );
}

export default App;
EOF

    echo "---> Frontend project initialized successfully."
fi

# --- Runtime Operations ---
# Ensure node_modules are installed if they are missing
if [ ! -d "node_modules" ]; then
    echo "---> node_modules not found. Installing dependencies..."
    gosu node npm install
fi

# Ensure the app directory is owned by the node user before starting
echo "---> Setting permissions for runtime..."
chown -R node:node /app

# Executes the main command of the container (e.g., "npm run dev") as the node user
echo "---> Starting frontend development server..."
exec gosu node "$@"