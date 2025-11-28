# Vendor Risk Digital Twin - Web Dashboard

Node.js/Express-based web interface for running vendor failure simulations.

## Features

- 🎯 Run vendor failure simulations through web interface
- 📊 View multi-dimensional impact results (operational, financial, compliance)
- 📈 Real-time graph statistics
- 💡 Actionable recommendations
- 🎨 Modern, responsive UI
- 🚀 Easy deployment (works with Vercel, Netlify, or any Node.js host)

## Setup

### Prerequisites

- Node.js 18.0+ 
- Neo4j database running
- npm or yarn package manager

### Installation

1. Install dependencies:
   ```bash
   cd dashboard
   npm install
   ```

2. Configure environment variables (create `.env` file in project root):
   ```bash
   NEO4J_URI=neo4j://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   PORT=5000
   LOG_LEVEL=INFO
   ```

3. Make sure Neo4j is running and data is loaded:
   ```bash
   # From project root
   python scripts/load_graph.py
   ```

### Running the Dashboard

1. Start the server:
   ```bash
   cd dashboard
   npm start
   ```
   
   Or for development with auto-reload:
   ```bash
   npm run dev
   ```

2. Open your browser:
   ```
   http://localhost:5000
   ```

## Usage

1. **Select a Vendor**: Choose from the dropdown (loaded from Neo4j)
2. **Set Duration**: Enter failure duration in hours (1-72)
3. **Run Simulation**: Click "Run Simulation" button
4. **View Results**: See multi-dimensional impact analysis

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/vendors` - Get list of available vendors
- `POST /api/simulate` - Run a simulation
  ```json
  {
    "vendor": "Stripe",
    "duration": 4
  }
  ```
- `GET /api/graph/stats` - Get graph statistics
- `GET /api/graph/dependencies?vendor=Stripe` - Get dependency graph data
- `GET /api/health` - Health check

## Architecture

```
dashboard/
├── server.js           # Express server
├── simulator.js        # Simulation engine
├── utils.js            # Utility functions
├── package.json        # Node.js dependencies
├── templates/
│   └── index.html      # Frontend UI
└── README.md           # This file
```

## Future Enhancements

- [ ] Graph visualization (using vis.js or D3.js)
- [ ] Historical simulation results
- [ ] Export results to PDF/JSON
- [ ] Comparison between multiple vendors
- [ ] Real-time graph updates

## Troubleshooting

**Error: "Simulator not initialized"**
- Check Neo4j connection in `.env` file
- Ensure Neo4j is running
- Verify credentials are correct

**No vendors in dropdown**
- Run `python scripts/load_graph.py` to load data
- Check Neo4j connection
- Verify environment variables are set correctly

**Simulation fails**
- Check Neo4j is accessible
- Verify vendor name exists in database
- Check logs in terminal for errors
- Ensure Node.js version is 18.0+

**Module not found errors**
- Run `npm install` to install dependencies
- Check that you're using Node.js 18.0+

