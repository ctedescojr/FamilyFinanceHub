#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Find all environment variables starting with VITE_ and create a list
export VITE_VARS=$(env | grep '^VITE_' | awk -F= '{print "$"$1}')

# Substitute the variables in all JS files inside /usr/share/nginx/html
for file in /usr/share/nginx/html/assets/*.js;
do
  echo "Processing $file ...";
  # Use envsubst to replace the variables, and write to a temp file
  envsubst "$VITE_VARS" < "$file" > "$file.tmp" && mv "$file.tmp" "$file"
done

# Execute the original command (CMD) from the Dockerfile
exec "$@"