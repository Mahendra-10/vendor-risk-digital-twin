# Running Neo4j and Dashboard Simultaneously

## ✅ Good News: Neo4j is Already Running!

Neo4j Desktop runs as a **background service**, so it can run simultaneously with your Node.js dashboard.

## How It Works

```
┌─────────────────┐         ┌──────────────────┐
│  Neo4j Desktop  │         │  Node.js Server  │
│  (Background)   │◄────────┤  (Dashboard)     │
│  Port: 7687     │         │  Port: 3000      │
└─────────────────┘         └──────────────────┘
         │                           │
         └───────────┬───────────────┘
                     ▼
            ┌─────────────────┐
            │   Your Browser  │
            │  localhost:3000 │
            └─────────────────┘
```

## Running Both Services

### Option 1: Neo4j Desktop (What You're Using) ✅

**Neo4j Desktop is already running!** You can see it in:
- Applications → Neo4j Desktop 2
- Or check: `ps aux | grep neo4j`

**To start Neo4j Desktop:**
1. Open **Neo4j Desktop** application
2. Click **Start** on your database instance
3. Status should show "Active" (green)

**To stop Neo4j Desktop:**
- Click **Stop** in Neo4j Desktop app
- Or quit the Neo4j Desktop application

### Option 2: Docker (Alternative)

If you prefer Docker:

```bash
# Start Neo4j in Docker (runs in background)
docker run -d \
  --name neo4j-vendor-risk \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Check if it's running
docker ps | grep neo4j

# Stop Neo4j
docker stop neo4j-vendor-risk
```

## Running the Dashboard

**In a separate terminal window:**

```bash
cd dashboard
npm start
```

The dashboard will connect to Neo4j automatically using your `.env` configuration.

## Typical Workflow

### Terminal 1: Neo4j (Already Running)
- Neo4j Desktop is running in the background
- No terminal needed (it's a GUI app)
- Database is accessible at `neo4j://localhost:7687`

### Terminal 2: Dashboard Server
```bash
cd dashboard
npm start
```
- Dashboard runs on `http://localhost:3000`
- Connects to Neo4j automatically

### Browser
- Open `http://localhost:3000` to use the dashboard
- Open `http://localhost:7474` to use Neo4j Browser (optional)

## Verification

### Check Neo4j is Running:
```bash
# Check process
ps aux | grep neo4j | grep -v grep

# Test connection
curl http://localhost:7474
```

### Check Dashboard is Running:
```bash
# Check process
ps aux | grep "node server.js" | grep -v grep

# Test API
curl http://localhost:3000/api/health
```

## Ports Used

| Service | Port | Purpose |
|---------|------|---------|
| Neo4j | 7687 | Database connection (Bolt protocol) |
| Neo4j Browser | 7474 | Web interface for Neo4j |
| Dashboard | 3000 | Your web dashboard |

## Troubleshooting

### "Cannot connect to Neo4j"
- Check Neo4j Desktop is running (green "Active" status)
- Verify `.env` has correct credentials:
  ```env
  NEO4J_URI=neo4j://localhost:7687
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=your_password
  ```

### "Port 7687 already in use"
- This is normal - Neo4j is using it
- Your dashboard connects TO Neo4j, not on the same port

### "No vendors in dashboard"
- Make sure data is loaded:
  ```bash
  python scripts/load_graph.py
  ```

## Quick Commands

```bash
# Start Neo4j (if using Docker)
docker start neo4j-vendor-risk

# Start Dashboard
cd dashboard && npm start

# Check both are running
ps aux | grep -E "neo4j|node server"

# Stop Dashboard
# Press Ctrl+C in the terminal

# Stop Neo4j Desktop
# Click Stop in Neo4j Desktop app
```

## Summary

✅ **Neo4j Desktop** = Background service (already running)
✅ **Dashboard** = Run `npm start` in terminal
✅ **Both can run simultaneously** - they use different ports
✅ **Dashboard connects to Neo4j** automatically via `.env` config

No special setup needed - just make sure Neo4j Desktop shows "Active" status!

