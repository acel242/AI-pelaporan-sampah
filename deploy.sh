#!/bin/bash
# Deploy EcoLapor frontend to nginx
cd "$(dirname "$0")/pelaporan-sampah"
echo "Building frontend..."
npm run build 2>&1
if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi
echo "Deploying to nginx..."
sudo cp -r dist/* /var/www/ecolapor/
sudo chown -R www-data:www-data /var/www/ecolapor
echo "Done! Frontend deployed to http://43.157.235.76"
echo "Restarting backend..."
pm2 restart ecolapor-backend
