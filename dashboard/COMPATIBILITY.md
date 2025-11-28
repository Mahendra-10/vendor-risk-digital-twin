# Python Scripts & JavaScript Dashboard Compatibility

## ✅ Yes, They Work Together!

All tools connect to the **same Neo4j database**, so they're fully compatible and can be used together.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Neo4j Database                          │
│  (Shared by all tools - single source of truth)            │
└─────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │                    │                    │
         │                    │                    │
    ┌────┴────┐          ┌─────┴─────┐         ┌─────┴─────┐
    │         │          │          │         │          │
    │ Python  │          │ Python   │         │  Node.js │
    │ Scripts │          │ Scripts  │         │ Dashboard │
    │ (CLI)   │          │ (CLI)    │         │ (Web)    │
    └─────────┘          └──────────┘         └──────────┘
```

## How Each Tool Works

### 1. Python Scripts (CLI Tools)

#### `load_graph.py` - Data Loader
- **Purpose**: Loads vendor/service data INTO Neo4j
- **Usage**: `python scripts/load_graph.py`
- **What it does**: 
  - Reads JSON files (sample data or GCP discovery output)
  - Creates nodes (Vendor, Service, BusinessProcess, ComplianceControl)
  - Creates relationships (DEPENDS_ON, SUPPORTS, SATISFIES)
- **When to use**: Initial setup, after GCP discovery, when updating data

#### `simulate_failure.py` - CLI Simulator
- **Purpose**: Run simulations from command line
- **Usage**: `python scripts/simulate_failure.py --vendor "Stripe" --duration 4`
- **What it does**:
  - Reads FROM Neo4j (queries vendor dependencies)
  - Calculates impact (operational, financial, compliance)
  - Saves results to JSON file
- **When to use**: Scripting, automation, batch processing

#### `gcp_discovery.py` - Cloud Discovery
- **Purpose**: Discover vendor dependencies from GCP
- **Usage**: `python scripts/gcp_discovery.py --project-id YOUR_PROJECT`
- **What it does**:
  - Queries GCP APIs (Cloud Functions, Cloud Run, etc.)
  - Extracts environment variables
  - Matches vendor patterns
  - Outputs JSON (used by `load_graph.py`)
- **When to use**: Discovering real vendor dependencies from GCP infrastructure

### 2. JavaScript Dashboard (Web Server)

#### `server.js` + `simulator.js` - Web Dashboard
- **Purpose**: Web interface for running simulations
- **Usage**: `npm start` (from dashboard directory)
- **What it does**:
  - Reads FROM Neo4j (queries vendors, dependencies)
  - Runs simulations via web API
  - Serves web UI (`templates/index.html`)
- **When to use**: Demos, interactive exploration, web-based access

## Workflow Examples

### Example 1: Initial Setup
```bash
# 1. Load data using Python script
python scripts/load_graph.py

# 2. Start JavaScript dashboard
cd dashboard
npm start

# 3. Run simulations via web UI at http://localhost:5000
```

### Example 2: GCP Discovery → Dashboard
```bash
# 1. Discover dependencies from GCP
python scripts/gcp_discovery.py --project-id my-project

# 2. Load discovered data into Neo4j
python scripts/load_graph.py --data-file data/outputs/discovered_dependencies.json

# 3. View in JavaScript dashboard
cd dashboard && npm start
```

### Example 3: CLI Simulation + Web Dashboard
```bash
# 1. Run simulation from CLI (saves to JSON)
python scripts/simulate_failure.py --vendor "Stripe" --duration 4

# 2. Also run same simulation via web dashboard
# (Both use same Neo4j data, get same results)
```

## Key Points

### ✅ They're Compatible Because:
1. **Same Database**: All tools connect to the same Neo4j instance
2. **Same Data Model**: All use the same node labels and relationship types
3. **Same Configuration**: All read from `config/config.yaml` and `.env`
4. **Independent Execution**: CLI tools and web server can run simultaneously

### 🔄 Data Flow:
```
GCP Discovery (Python) 
    ↓ (JSON output)
Load Graph (Python) 
    ↓ (writes to)
Neo4j Database 
    ↓ (read by)
├── Simulate Failure (Python CLI)
└── JavaScript Dashboard (Web)
```

### 📊 Two Simulation Engines:
You now have **two simulation engines** that do the same thing:

1. **Python**: `scripts/simulate_failure.py` (CLI)
   - Good for: Scripting, automation, batch processing
   - Output: JSON file

2. **JavaScript**: `dashboard/simulator.js` (Web API)
   - Good for: Interactive demos, web access
   - Output: JSON API response

Both use the same Neo4j data and produce identical results!

## When to Use Which?

| Use Case | Tool |
|----------|------|
| Initial data loading | `load_graph.py` (Python) |
| GCP discovery | `gcp_discovery.py` (Python) |
| Batch simulations | `simulate_failure.py` (Python CLI) |
| Interactive demos | JavaScript Dashboard |
| Web-based access | JavaScript Dashboard |
| Automation/scripts | Python scripts |
| Research/analysis | Python scripts + Jupyter notebooks |

## Configuration

All tools use the same configuration:
- **Neo4j connection**: `config/config.yaml` + `.env`
- **Environment variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

Make sure your `.env` file is in the project root (not in `dashboard/`).

## Troubleshooting

**"No vendors found" in dashboard:**
- Run `python scripts/load_graph.py` first to load data

**"Simulator not initialized" in dashboard:**
- Check `.env` file has correct Neo4j credentials
- Ensure Neo4j is running

**Python scripts work but dashboard doesn't:**
- Both should use same `.env` file in project root
- Check Neo4j connection string matches

## Summary

✅ **Yes, all Python scripts work perfectly with the JavaScript dashboard!**

They're designed to work together:
- Python scripts = Data management & CLI tools
- JavaScript dashboard = Web interface & demos

Both read/write to the same Neo4j database, so they're fully compatible.

