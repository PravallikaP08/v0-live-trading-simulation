# Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git

### Quick Start
\`\`\`bash
# Clone repository
git clone <repository-url>
cd algo-trading-system

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Generate sample data
python scripts/generate_sample_data.py

# Start backend (Terminal 1)
cd backend
python -m uvicorn main:app --reload --port 8000

# Frontend setup (Terminal 2)
npm install
npm run dev
\`\`\`

Access at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker Deployment

### Using Docker Compose
\`\`\`bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
\`\`\`

### Individual Containers
\`\`\`bash
# Backend only
docker build -t algo-trading-backend --target backend .
docker run -p 8000:8000 algo-trading-backend

# Frontend only
docker build -t algo-trading-frontend --target frontend .
docker run -p 3000:3000 algo-trading-frontend
\`\`\`

## Cloud Deployment

### Railway (Recommended)
1. Fork this repository
2. Connect Railway to your GitHub
3. Deploy backend:
   - Create new project
   - Connect repository
   - Set root directory to `backend/`
   - Add environment variables
4. Deploy frontend:
   - Create new service
   - Set root directory to `/`
   - Add `NEXT_PUBLIC_API_URL` environment variable

### Vercel + Railway
\`\`\`bash
# Deploy frontend to Vercel
npm install -g vercel
vercel --prod

# Deploy backend to Railway
# Use Railway CLI or web interface
\`\`\`

### Render
1. Create web service for backend
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
2. Create web service for frontend
   - Build command: `npm install && npm run build`
   - Start command: `npm start`

## Environment Variables

### Backend (.env)
\`\`\`
TRADER_DATABASE_URL=sqlite:///./data/trading.db
TRADER_CORS_ORIGINS=["http://localhost:3000"]
TRADER_DEFAULT_SYMBOL=AAPL
TRADER_INITIAL_CASH=100000.0
\`\`\`

### Frontend (.env.local)
\`\`\`
NEXT_PUBLIC_API_URL=http://localhost:8000
\`\`\`

## Production Considerations

### Database
- **Development**: SQLite (included)
- **Production**: Consider PostgreSQL for better performance
- **Migration**: Update `DATABASE_URL` in backend config

### Security
- Add authentication/authorization
- Implement rate limiting
- Use HTTPS in production
- Validate all user inputs

### Performance
- Enable Redis for caching
- Implement database connection pooling
- Add CDN for static assets
- Monitor with APM tools

### Monitoring
- Add logging with structured format
- Implement health checks
- Set up error tracking (Sentry)
- Monitor WebSocket connections

## Troubleshooting

### Common Issues

**Backend won't start**
\`\`\`bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall

# Check port availability
lsof -i :8000
\`\`\`

**Frontend build fails**
\`\`\`bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
\`\`\`

**WebSocket connection fails**
- Check CORS settings in backend
- Verify WebSocket URL in frontend
- Check firewall/proxy settings

**Database errors**
\`\`\`bash
# Reset database
rm backend/data/trading.db
python scripts/generate_sample_data.py
\`\`\`

### Performance Issues
- Reduce chart data points for better rendering
- Implement data pagination for large datasets
- Use WebSocket message throttling
- Optimize database queries

## Scaling

### Horizontal Scaling
- Use load balancer for multiple backend instances
- Implement Redis for session storage
- Use message queue for background tasks

### Database Scaling
- Migrate to PostgreSQL
- Implement read replicas
- Add database indexing
- Use connection pooling

### Monitoring & Alerts
- Set up uptime monitoring
- Monitor API response times
- Track WebSocket connection health
- Alert on high error rates
