# Getting Started with JavaScript Dashboard

Quick start guide to get the Vendor Risk Digital Twin dashboard running.

## Prerequisites

Before you begin, make sure you have:

1. **Node.js 18.0+** installed
   ```bash
   node --version  # Should show v18.0.0 or higher
   ```
   [Download Node.js](https://nodejs.org/) if needed

2. **Neo4j Database** running
   - Neo4j Desktop (recommended) or Docker
   - See main [README.md](../README.md) for Neo4j setup

3. **Data loaded in Neo4j**
   - Run `python scripts/load_graph.py` from project root first

## Step-by-Step Setup

### Step 1: Install Dependencies

```bash
cd dashboard
npm install
```

This installs:
- `express` - Web server
- `neo4j-driver` - Neo4j database driver
- `dotenv` - Environment variable management
- `js-yaml` - YAML config parsing
- `cors` - CORS middleware

**Expected output:**
```
added 150 packages in 10s
```

### Step 2: Configure Environment Variables

Create or update `.env` file in the **project root** (not in `dashboard/`):

```bash
# From project root
cd ..
nano .env  # or use your preferred editor
```

Add these variables:
```env
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
PORT=5000
LOG_LEVEL=INFO
```

**Important:** 
- Use the same password you set when creating your Neo4j database
- If using Neo4j Desktop, the URI is usually `neo4j://localhost:7687`
- If using Docker, check your container's port mapping

### Step 3: Load Data into Neo4j

If you haven't already, load the sample data:

```bash
# From project root (not dashboard/)
python scripts/load_graph.py
```

**Expected output:**
```
✅ Graph loaded successfully!
   - Vendors: 5
   - Services: 12
   - Business Processes: 8
   - Compliance Controls: 15
   - Relationships: 25
```

### Step 4: Start the Dashboard

```bash
cd dashboard
npm start
```

**Expected output:**
```
[INFO] Simulator initialized successfully
[INFO] Starting Vendor Risk Digital Twin Dashboard...
[INFO] Dashboard available at: http://localhost:5000
```

### Step 5: Open in Browser

Open your browser and navigate to:
```
http://localhost:5000
```

You should see the Vendor Risk Digital Twin dashboard!

## Verification Checklist

✅ **Node.js installed**
```bash
node --version  # v18.0.0+
npm --version   # Should work
```

✅ **Dependencies installed**
```bash
cd dashboard
ls node_modules  # Should show installed packages
```

✅ **Neo4j running**
- Open Neo4j Browser: http://localhost:7474
- Run: `MATCH (v:Vendor) RETURN v.name LIMIT 5`
- Should return vendor names

✅ **Environment variables set**
```bash
# From project root
cat .env | grep NEO4J  # Should show your Neo4j config
```

✅ **Data loaded**
```bash
# From project root
python scripts/load_graph.py  # Should complete successfully
```

✅ **Dashboard running**
- Browser shows dashboard at http://localhost:5000
- Vendor dropdown should populate with vendors
- Graph stats should show numbers (not "-")

## Quick Test

Once everything is running:

1. **Select a vendor** from the dropdown (e.g., "Stripe")
2. **Set duration** to 4 hours
3. **Click "Run Simulation"**
4. **View results** - should show:
   - Operational impact
   - Financial impact
   - Compliance impact
   - Recommendations

## Troubleshooting

### "Cannot find module" errors
```bash
cd dashboard
rm -rf node_modules package-lock.json
npm install
```

### "Simulator not initialized"
- Check `.env` file exists in project root
- Verify Neo4j credentials are correct
- Ensure Neo4j is running: `http://localhost:7474`

### "No vendors in dropdown"
- Run `python scripts/load_graph.py` to load data
- Check Neo4j Browser to verify data exists
- Check server logs for errors

### "Port 5000 already in use"
```bash
# Option 1: Use different port
PORT=3000 npm start

# Option 2: Kill process on port 5000
# macOS/Linux:
lsof -ti:5000 | xargs kill
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "ECONNREFUSED" Neo4j connection error
- Verify Neo4j is running
- Check URI in `.env` matches your Neo4j setup
- Try: `neo4j://localhost:7687` or `bolt://localhost:7687`

## Development Mode

For auto-reload during development:

```bash
npm run dev
```

This uses Node.js `--watch` flag (requires Node 18+).

## Next Steps

- ✅ Dashboard is running
- 📊 Try different vendors and durations
- 🔍 Explore the API endpoints (see README.md)
- 🎨 Customize the UI in `templates/index.html`
- 📈 Add graph visualization (future enhancement)

## API Testing

Test the API directly:

```bash
# Get vendors
curl http://localhost:5000/api/vendors

# Get graph stats
curl http://localhost:5000/api/graph/stats

# Run simulation
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration": 4}'

# Health check
curl http://localhost:5000/api/health
```

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Check [COMPATIBILITY.md](COMPATIBILITY.md) for Python scripts integration
- Check [MIGRATION.md](MIGRATION.md) for migration details

