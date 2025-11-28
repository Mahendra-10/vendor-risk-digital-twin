# Migration from Python/Flask to Node.js/Express

This dashboard has been converted from Python/Flask to Node.js/Express for better demo portability and a unified JavaScript stack.

## What Changed

### Backend
- **Before**: `app.py` (Flask)
- **After**: `server.js` (Express)

### Core Logic
- **Before**: `scripts/simulate_failure.py` (Python class)
- **After**: `simulator.js` (JavaScript class)

### Utilities
- **Before**: `scripts/utils.py` (Python)
- **After**: `utils.js` (JavaScript)

## Key Benefits

1. **Single Language Stack**: JavaScript everywhere (frontend + backend)
2. **Easier Deployment**: Works with Vercel, Netlify, Railway, or any Node.js host
3. **Better for Demos**: Can be deployed as serverless functions or static + API
4. **Modern Tooling**: Uses ES modules, async/await, modern Node.js features

## API Compatibility

All API endpoints remain **100% compatible** with the original Flask version:
- `GET /` - Dashboard page
- `GET /api/vendors` - Get vendors
- `POST /api/simulate` - Run simulation
- `GET /api/graph/stats` - Graph statistics
- `GET /api/graph/dependencies` - Dependency graph
- `GET /api/health` - Health check

The frontend (`templates/index.html`) works without any changes!

## Migration Notes

- Uses ES modules (`"type": "module"` in package.json)
- Requires Node.js 18.0+ (for `--watch` flag in dev mode)
- Neo4j driver API is slightly different but functionally equivalent
- All simulation logic has been preserved and converted

## Running Both Versions

You can keep both versions:
- Python version: `python app.py` (original)
- Node.js version: `npm start` (new)

Both connect to the same Neo4j database and provide identical functionality.

## Python Scripts Compatibility

**All Python CLI scripts still work perfectly with the JavaScript dashboard:**

- ✅ `load_graph.py` - Loads data into Neo4j (used by both)
- ✅ `simulate_failure.py` - CLI simulation tool (alternative to web dashboard)
- ✅ `gcp_discovery.py` - GCP discovery tool (feeds data to load_graph.py)

**Why they work together:**
- All tools connect to the same Neo4j database
- Python scripts are CLI tools (run from command line)
- JavaScript dashboard is a web server (runs continuously)
- They can run simultaneously and share the same data

**Typical workflow:**
1. Load data: `python scripts/load_graph.py` (Python)
2. Run dashboard: `npm start` (JavaScript)
3. Both can query the same Neo4j database

See [COMPATIBILITY.md](COMPATIBILITY.md) for detailed explanation.

