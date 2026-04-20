#!/bin/bash
# Check current EcoLapor tunnel URLs
echo "=== EcoLapor Status ==="
echo ""
echo "📡 Frontend (Dashboard):"
pm2 logs ecolapor-tunnel-frontend --lines 20 --nostream 2>&1 | grep "trycloudflare.com" | tail -1
echo ""
echo "📡 Backend (API):"
pm2 logs ecolapor-tunnel-backend --lines 20 --nostream 2>&1 | grep "trycloudflare.com" | tail -1
echo ""
echo "🔧 Services:"
pm2 status | grep ecolapor
echo ""
echo "💡 If URLs don't work, run:"
echo "   pm2 restart ecolapor-tunnel-frontend ecolapor-tunnel-backend"
echo "   Then check this script again for new URLs"
