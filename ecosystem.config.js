module.exports = {
  apps: [
    {
      name: 'ecolapor-backend',
      script: 'backend/server.py',
      interpreter: 'python3',
      cwd: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah',
      autorestart: true,
      watch: false,
    },
    {
      name: 'ecolapor-proxy',
      script: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah/start-proxy.sh',
      interpreter: 'bash',
      cwd: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah',
      autorestart: true,
      watch: false,
    },
    {
      name: 'ecolapor-tunnel-backend',
      script: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah/start-tunnel.sh',
      interpreter: 'bash',
      args: '5000 /home/ubuntu/.ecolapor-tunnel-backend.log EcolaporBackend',
      cwd: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah',
      autorestart: true,
      watch: false,
      env: {
        BACKEND_TUNNEL_URL: ''
      }
    },
    {
      name: 'ecolapor-tunnel-frontend',
      script: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah/start-tunnel.sh',
      interpreter: 'bash',
      args: '5004 /home/ubuntu/.ecolapor-tunnel-frontend.log EcolaporFrontend',
      cwd: '/home/ubuntu/.openclaw/workspace/AI-pelaporan-sampah',
      autorestart: true,
      watch: false,
    }
  ]
};
