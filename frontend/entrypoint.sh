#!/bin/sh
set -e

# Replace PORT in nginx config
export PORT="${PORT:-80}"
envsubst '${PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# If VITE_API_URL is provided, replace it in the built JS files
if [ ! -z "$VITE_API_URL" ]; then
    echo "Configuring API URL: $VITE_API_URL"
    # Find and replace in built JS files
    find /usr/share/nginx/html/assets -type f -name "*.js" -exec sed -i "s|VITE_API_URL_PLACEHOLDER|$VITE_API_URL|g" {} +
fi

echo "Starting Nginx on port $PORT"
exec nginx -g 'daemon off;'
