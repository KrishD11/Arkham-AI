# Arkham AI - Autonomous Supply Chain Rerouting

Arkham AI is an autonomous AI agent that monitors geopolitical risk and trade disruptions, then automatically reroutes shipments to safer routes in real time.

Generate routes for global supply chains.

## Features

- Real-time Risk Monitoring: Aggregates risk from trade news, political instability, and port congestion
- Predictive Risk Scoring: Uses Vertex AI to predict risk levels 3-7 days ahead
- Autonomous Rerouting: Automatically selects and executes optimal route changes
- Route Optimization: Balances risk, cost, and time to find the best alternative routes
- Interactive Dashboard: Visual map showing routes, risk heatmaps, and shipment status

## MVP Architecture

Data Ingestion → Risk Assessment → Predictive Scoring → Route Optimization → Autonomous Execution → Dashboard

## Tech Stack

- Agent Framework: Google ADK (Agent Development Kit)
- AI/ML: Vertex AI (Gemini 2.0 Flash)
- Backend: Flask (Python)
- Database: MongoDB Atlas
- Frontend: React + Mapbox/Leaflet
- Cloud: Google Cloud Platform (Cloud Run, Vertex AI)

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
```

### 3. Run the Application

```bash
# Start Flask server
python agent/main.py

# Server will run on http://localhost:8080
```

## Project Structure

```
agent/
├── main.py              # Flask application
├── config.py            # Configuration settings
├── adk_agent.py         # ADK agent setup ✅
├── database.py          # MongoDB Atlas service ✅
├── policy.py            # ACLED OAuth authentication ✅
├── data_ingestion.py    # Data fetching service ✅
└── tools/
    ├── risk_tool.py     # Risk assessment ✅
    ├── score_tool.py    # Predictive scoring ✅
    ├── route_tool.py    # Route optimization ✅
    ├── exec_tool.py     # Autonomous execution ✅
    └── log_tool.py      # Logging ✅
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy to Google Cloud Run

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy
./deploy.sh
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your credentials

# Run locally
python agent/main.py
```

## API Endpoints

### Health & Info
- `GET /` - Health check
- `GET /api/health` - API health
- `GET /api/agent/info` - Agent information

### Agent
- `POST /api/agent/query` - Query the agent

### Data Ingestion
- `GET /api/data/trade-news` - Get trade news
- `GET /api/data/political` - Get political data
- `GET /api/data/ports` - Get port data
- `GET /api/data/all` - Get all risk data
- `POST /api/data/route` - Get route-specific data

### Risk Assessment
- `POST /api/routes/assess` - Assess route risk
- `GET /api/routes/<route_id>/risk` - Get route risk
- `POST /api/routes/compare` - Compare routes

### Predictive Scoring
- `POST /api/routes/predict` - Predict risk levels
- `GET /api/routes/<route_id>/predict` - Get predictions

### Route Optimization
- `POST /api/routes/optimize` - Optimize routes
- `GET /api/routes` - List routes

### Execution
- `POST /api/execution/monitor` - Monitor and execute
- `POST /api/execution/execute` - Execute reroute

### Logging
- `GET /api/logs` - Get logs
- `GET /api/logs/export` - Export logs

### Authentication
- `GET /api/auth/acled/token` - ACLED token status
- `POST /api/auth/acled/refresh` - Refresh ACLED token
- `GET /api/auth/acled/test` - Test ACLED connection

### Database (MongoDB)
- `GET /api/db/health` - Check MongoDB connection status
- `GET /api/db/risk-data` - Query risk data from MongoDB (supports: category, location, source, limit, days_back)
- `GET /api/db/stats` - Get database statistics (collection counts)

## MongoDB Atlas Integration

The application automatically stores all fetched risk data in MongoDB Atlas. Data is persisted when fetched from APIs.

### MongoDB Atlas Setup

1. **Create MongoDB Atlas Account**
   - Go to https://www.mongodb.com/cloud/atlas
   - Create a free cluster

2. **Get Connection String**
   - In Atlas dashboard, click "Connect"
   - Choose "Connect your application"
   - Copy the connection string (format: `mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`)

3. **Configure Environment**
   ```bash
   # Add to .env file
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=arkham_ai
   ```

4. **Database Collections**
   - `risk_data` - Stores all risk data points from APIs
   - `routes` - Stores route information
   - `assessments` - Stores risk assessments
   - `executions` - Stores execution actions
   - `logs` - Stores application logs

## License

MIT
