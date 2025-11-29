/**
 * Vendor Risk Digital Twin - Web Dashboard Server
 * 
 * Express server for running vendor failure simulations
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile } from 'fs/promises';
import { VendorFailureSimulator } from './simulator.js';
import { loadConfig, validateEnvVars, setupLogging } from './utils.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5001;

// Cloud Run Simulation Service URL (for automatic BigQuery saving)
const SIMULATION_SERVICE_URL = process.env.SIMULATION_SERVICE_URL || 
  'https://simulation-service-16418516910.us-central1.run.app';

// Setup logging
const logger = setupLogging(process.env.LOG_LEVEL || 'INFO');

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'templates')));

// Global simulator instance
let simulator = null;

/**
 * Initialize the simulator with Neo4j connection
 */
/**
 * Initialize the simulator with Neo4j connection
 */
async function initSimulator() {
  try {
    // Validate environment variables
    const requiredVars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD'];
    if (!validateEnvVars(requiredVars)) {
      logger.error('Missing required environment variables. Please check your .env file.');
      return false;
    }

    const config = loadConfig();
    const neo4jConfig = config.neo4j;

    simulator = new VendorFailureSimulator(
      neo4jConfig.uri,
      neo4jConfig.user,
      neo4jConfig.password
    );

    // Test connection
    const session = simulator.driver.session();
    await session.run('RETURN 1 as test');
    await session.close();

    logger.info('Simulator initialized successfully');
    return true;
  } catch (error) {
    logger.error(`Failed to initialize simulator: ${error.message}`);
    logger.warning('Server starting in OFFLINE MODE. Dashboard will load, but simulation features requiring Neo4j will be disabled.');
    return false;
  }
}

/**
 * Get list of available vendors from Neo4j
 */
async function getAvailableVendors() {
  if (!simulator) {
    return [];
  }

  try {
    const session = simulator.driver.session();
    // Use DISTINCT to remove duplicates, and normalize case for grouping
    const result = await session.run(
      'MATCH (v:Vendor) RETURN DISTINCT COALESCE(v.display_name, v.name) as name ORDER BY COALESCE(v.display_name, v.name)'
    );
    await session.close();

    // Additional deduplication on the application side (case-insensitive)
    const vendorNames = result.records.map(record => record.get('name'));
    const seen = new Set();
    const uniqueVendors = [];
    
    for (const name of vendorNames) {
      const normalized = name.toLowerCase();
      if (!seen.has(normalized)) {
        seen.add(normalized);
        uniqueVendors.push(name);
      }
    }
    
    return uniqueVendors;
  } catch (error) {
    logger.error(`Error fetching vendors: ${error.message}`);
    return [];
  }
}

// Routes

/**
 * Main dashboard page
 */
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

/**
 * API endpoint to get Neo4j connection info (for dashboard link)
 */
app.get('/api/neo4j/info', async (req, res) => {
  try {
    const config = loadConfig();
    const neo4jConfig = config.neo4j;
    const uri = neo4jConfig.uri || '';
    
    // Extract Aura instance ID from URI (format: neo4j+s://INSTANCE_ID.databases.neo4j.io)
    let auraBrowserUrl = null;
    let auraConsoleUrl = null;
    let instanceId = null;
    
    if (uri.includes('databases.neo4j.io')) {
      // Extract instance ID from Aura URI
      const match = uri.match(/neo4j\+s?:\/\/([a-f0-9]+)\.databases\.neo4j\.io/);
      if (match && match[1]) {
        instanceId = match[1];
        // Neo4j Browser URL (for running queries and viewing graph)
        auraBrowserUrl = `https://${instanceId}.databases.neo4j.io/browser/`;
        // Neo4j Console URL (for instance management)
        auraConsoleUrl = `https://console.neo4j.io/instances/${instanceId}`;
      }
    }
    
    // Return safe info (no password)
    res.json({
      uri: uri.replace(/\/\/[^:]+:[^@]+@/, '//***:***@'), // Mask credentials in URI
      instanceId: instanceId,
      auraBrowserUrl: auraBrowserUrl, // Direct browser URL for viewing graph
      auraConsoleUrl: auraConsoleUrl, // Console URL for instance management
      isAura: uri.includes('databases.neo4j.io')
    });
  } catch (error) {
    logger.error(`Error in /api/neo4j/info: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * API endpoint to get available vendors
 */
app.get('/api/vendors', async (req, res) => {
  try {
    const vendors = await getAvailableVendors();
    res.json({ vendors });
  } catch (error) {
    logger.error(`Error in /api/vendors: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * API endpoint to run a simulation
 */
app.post('/api/simulate', async (req, res) => {
  try {
    const { vendor, duration, useCloudService } = req.body;
    const durationHours = parseInt(duration) || 4;
    const useCloud = useCloudService !== false; // Default to true (use Cloud Run)

    if (!vendor) {
      return res.status(400).json({ error: 'Vendor name is required' });
    }

    // Validate that Neo4j has data before running simulation
    const vendors = await getAvailableVendors();
    if (!vendors || vendors.length === 0) {
      // If we are in offline mode (simulator not init), we might still want to try Cloud Run if enabled
      if (!simulator && !process.env.ENABLE_CLOUD_RUN_SIMULATION) {
         return res.status(503).json({ 
          error: 'Simulator is in OFFLINE MODE (Neo4j unavailable). Please check database connection.',
          requiresDataLoad: true
        });
      }
      
      if (simulator) {
        return res.status(400).json({ 
          error: 'No vendor data found in Neo4j. Please "Fetch Latest Discovery" and "Load into Neo4j" first.',
          requiresDataLoad: true
        });
      }
    }

    // Warn if data hasn't been loaded in this session (but allow simulation)
    if (lastDataLoadTime === null && simulator) {
      logger.warning(`Simulation requested but data hasn't been loaded in this session. Last load: ${lastDataLoadTime}`);
      // Don't block, but log a warning - data exists from previous session
    }

    // Normalize vendor name for validation (vendors list contains display_names)
    // We need to check if the vendor exists, accounting for case differences
    const normalizedVendor = vendor.toLowerCase().trim();
    
    // Only validate against local Neo4j if we have it
    if (vendors.length > 0) {
      const vendorExists = vendors.some(v => v.toLowerCase().trim() === normalizedVendor);
      
      if (!vendorExists) {
        return res.status(400).json({ 
          error: `Vendor "${vendor}" not found in Neo4j. Please ensure discovery data is loaded.`,
          availableVendors: vendors
        });
      }
    }

    // Option 1: Use Cloud Run Service (automatic BigQuery saving via Pub/Sub)
    // Controlled by env var ENABLE_CLOUD_RUN_SIMULATION
    const enableCloudRun = process.env.ENABLE_CLOUD_RUN_SIMULATION === 'true';
    
    if (enableCloudRun && useCloud && SIMULATION_SERVICE_URL) {
      try {
        // Normalize vendor name to match Neo4j storage (lowercase)
        // The vendor parameter comes from display_name, but we need the actual vendor name
        const normalizedVendor = vendor.toLowerCase().trim();
        logger.info(`Running simulation via Cloud Run: ${vendor} (normalized: ${normalizedVendor}) for ${durationHours} hours`);
        
        // Use Node.js built-in fetch (Node 18+)
        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

        try {
            const response = await fetch(`${SIMULATION_SERVICE_URL}/simulate`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                vendor: normalizedVendor,  // Send normalized name to match Neo4j
                duration: durationHours
              }),
              signal: controller.signal
            });
            
            clearTimeout(timeoutId);

            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.error || `Cloud Run service returned ${response.status}`);
            }

            const result = await response.json();
            logger.info(`✅ Simulation completed via Cloud Run (auto-saved to BigQuery)`);
            
            // Debug: Log compliance data structure
            if (result.compliance_impact) {
              logger.info(`Compliance data received: summary=${Object.keys(result.compliance_impact.summary || {}).length}, frameworks=${Object.keys(result.compliance_impact.affected_frameworks || {}).length}`);
            } else {
              logger.warn('⚠️ No compliance_impact in Cloud Run response');
            }
            
            // Add timestamp if not present
            if (!result.simulation_timestamp) {
              result.simulation_timestamp = new Date().toISOString();
            }
            
            return res.json(result);
        } catch (fetchError) {
            clearTimeout(timeoutId);
            throw fetchError;
        }
      } catch (cloudError) {
        logger.warn(`Cloud Run simulation failed: ${cloudError.message}, falling back to local`);
        // Fall through to local simulation
      }
    }

    // Option 2: Fallback to local simulation (no BigQuery auto-save)
    if (!simulator) {
      return res.status(503).json({ 
        error: 'Simulator not initialized (Offline Mode) and Cloud Run failed or disabled. Please check Neo4j connection.' 
      });
    }

    logger.info(`Running simulation locally: ${vendor} for ${durationHours} hours`);
    const result = await simulator.simulateVendorFailure(vendor, durationHours);

    // Add timestamp
    result.simulation_timestamp = new Date().toISOString();
    result.warning = 'Simulation ran locally. Results NOT automatically saved to BigQuery. Use Cloud Run service for automatic saving.';

    res.json(result);
  } catch (error) {
    logger.error(`Simulation error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// Track when data was last loaded (in-memory, resets on server restart)
let lastDataLoadTime = null;

/**
 * API endpoint to get graph statistics
 */
app.get('/api/graph/stats', async (req, res) => {
  if (!simulator) {
    return res.json({
        nodes: { Vendor: 0, Service: 0 },
        relationships: {},
        lastDataLoad: null,
        dataLoaded: false,
        status: 'offline'
    });
  }

  try {
    const session = simulator.driver.session();

    // Get node counts - use DISTINCT for vendors and services to avoid duplicates
    const nodeCounts = {};
    
    // Count unique vendors (case-insensitive)
    const vendorResult = await session.run(`
      MATCH (v:Vendor)
      WITH DISTINCT toLower(v.name) as normalized_name
      RETURN count(normalized_name) as count
    `);
    nodeCounts['Vendor'] = vendorResult.records[0].get('count').toNumber();
    
    // Count unique services
    const serviceResult = await session.run(`
      MATCH (s:Service)
      WITH DISTINCT s.name as name
      RETURN count(name) as count
    `);
    nodeCounts['Service'] = serviceResult.records[0].get('count').toNumber();
    
    // Count other node types normally
    const otherLabels = ['BusinessProcess', 'ComplianceControl'];
    for (const label of otherLabels) {
      const result = await session.run(`MATCH (n:${label}) RETURN count(n) as count`);
      nodeCounts[label] = result.records[0].get('count').toNumber();
    }

    // Get relationship counts
    const relCounts = {};
    const relTypes = ['DEPENDS_ON', 'SUPPORTS', 'SATISFIES'];
    
    for (const relType of relTypes) {
      const result = await session.run(
        `MATCH ()-[r:${relType}]->() RETURN count(r) as count`
      );
      relCounts[relType] = result.records[0].get('count').toNumber();
    }

    await session.close();

    res.json({
      nodes: nodeCounts,
      relationships: relCounts,
      lastDataLoad: lastDataLoadTime, // Include when data was last loaded
      dataLoaded: lastDataLoadTime !== null,
      status: 'online'
    });
  } catch (error) {
    logger.error(`Error fetching graph stats: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * API endpoint to get vendor dependencies for visualization
 */
app.get('/api/graph/dependencies', async (req, res) => {
  const vendorName = req.query.vendor;

  if (!simulator) {
    return res.status(503).json({ error: 'Simulator not initialized (Offline Mode)' });
  }

  try {
    const session = simulator.driver.session();

    let query;
    if (vendorName) {
      // Get dependencies for specific vendor
      query = `
        MATCH (v:Vendor {name: $normalized_vendor_name})<-[:DEPENDS_ON]-(s:Service)
        OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
        OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
        RETURN v, s, bp, cc
      `;
    } else {
      // Get all dependencies
      query = `
        MATCH (v:Vendor)<-[:DEPENDS_ON]-(s:Service)
        OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
        OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
        RETURN v, s, bp, cc
        LIMIT 100
      `;
    }

    const result = await session.run(
      query,
      vendorName ? { normalized_vendor_name: vendorName.toLowerCase().trim() } : {}
    );

    // Format for frontend
    const nodes = [];
    const edges = [];
    const nodeIds = new Set();

    for (const record of result.records) {
      const v = record.get('v');
      const s = record.get('s');
      const bp = record.get('bp');
      const cc = record.get('cc');

      // Vendor node
      if (v) {
        const vId = `vendor_${v.properties.name}`;
        if (!nodeIds.has(vId)) {
          nodes.push({
            id: vId,
            label: v.properties.name,
            type: 'vendor',
            category: v.properties.category || 'unknown',
          });
          nodeIds.add(vId);
        }
      }

      // Service node
      if (s) {
        const sId = `service_${s.properties.name}`;
        if (!nodeIds.has(sId)) {
          const rpmValue = s.properties.rpm;
          nodes.push({
            id: sId,
            label: s.properties.name,
            type: 'service',
            rpm: rpmValue ? Number(rpmValue) : 0,
          });
          nodeIds.add(sId);
        }

        // Edge: Service -> Vendor
        if (v) {
          edges.push({
            from: sId,
            to: `vendor_${v.properties.name}`,
            type: 'DEPENDS_ON',
          });
        }
      }

      // Business Process node
      if (bp) {
        const bpId = `process_${bp.properties.name}`;
        if (!nodeIds.has(bpId)) {
          nodes.push({
            id: bpId,
            label: bp.properties.name,
            type: 'business_process',
          });
          nodeIds.add(bpId);
        }

        // Edge: Service -> Business Process
        if (s) {
          edges.push({
            from: `service_${s.properties.name}`,
            to: bpId,
            type: 'SUPPORTS',
          });
        }
      }

      // Compliance Control node
      if (cc) {
        const ccId = `control_${cc.properties.control_id}`;
        if (!nodeIds.has(ccId)) {
          nodes.push({
            id: ccId,
            label: cc.properties.control_id,
            type: 'compliance_control',
            framework: cc.properties.framework || 'unknown',
          });
          nodeIds.add(ccId);
        }

        // Edge: Vendor -> Compliance Control
        if (v) {
          edges.push({
            from: `vendor_${v.properties.name}`,
            to: ccId,
            type: 'SATISFIES',
          });
        }
      }
    }

    await session.close();

    res.json({
      nodes,
      edges,
    });
  } catch (error) {
    logger.error(`Error fetching dependencies: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * API endpoint to fetch latest discovery results from Cloud Storage
 */
app.get('/api/discovery/latest', async (req, res) => {
  try {
    const projectId = req.query.project_id || process.env.GCP_PROJECT_ID;
    const devMode = req.query.dev_mode === 'true';
    
    if (!projectId) {
      return res.status(400).json({ error: 'GCP_PROJECT_ID or project_id parameter required' });
    }

    // Use promisified exec for child process
    const execPromise = promisify(exec);

    // Run the Python script to fetch discovery results (using venv Python)
    const scriptPath = path.join(__dirname, '..', 'scripts', 'fetch_discovery_results.py');
    const venvPython = path.join(__dirname, '..', 'venv', 'bin', 'python');
    
    // Build command with verbose logging if dev mode
    let command = `"${venvPython}" "${scriptPath}" --project-id "${projectId}" --output-file /tmp/discovery_latest.json`;
    if (devMode) {
      command += ' --log-level DEBUG';
    }
    
    const { stdout, stderr } = await execPromise(command);

    // Parse stdout/stderr for developer mode details
    const logs = [];
    const apis = [];
    const resources = [];
    
    if (devMode) {
      // Extract API calls and resource discoveries from logs
      const lines = (stdout + '\n' + stderr).split('\n');
      lines.forEach(line => {
        if (line.includes('INFO') || line.includes('DEBUG')) {
          logs.push(line);
          
          // Detect GCP API calls
          if (line.includes('Cloud Functions') || line.includes('functions_v1')) {
            apis.push({ name: 'Cloud Functions API', action: 'Listing Cloud Functions', timestamp: new Date().toISOString() });
          }
          if (line.includes('Cloud Run') || line.includes('run_v2')) {
            apis.push({ name: 'Cloud Run API', action: 'Listing Cloud Run Services', timestamp: new Date().toISOString() });
          }
          if (line.includes('Cloud Storage') || line.includes('storage.Client')) {
            apis.push({ name: 'Cloud Storage API', action: 'Fetching discovery results', timestamp: new Date().toISOString() });
          }
          
          // Detect resource discoveries
          if (line.includes('discovered') || line.includes('found')) {
            const match = line.match(/(\d+)\s+(cloud functions|cloud run|vendors)/i);
            if (match) {
              resources.push({ type: match[2], count: match[1], timestamp: new Date().toISOString() });
            }
          }
        }
      });
    }

    if (stderr && !stderr.includes('INFO') && !stderr.includes('WARNING') && !stderr.includes('DEBUG')) {
      logger.warning(`Discovery fetch warnings: ${stderr}`);
    }

    // Read the output file
    const data = await readFile('/tmp/discovery_latest.json', 'utf8');
    const discoveryData = JSON.parse(data);

    // Calculate service counts from vendor data if metadata is missing
    let cloudFunctionsCount = discoveryData.discovery_metadata?.cloud_functions_count;
    let cloudRunServicesCount = discoveryData.discovery_metadata?.cloud_run_services_count;
    
    if (cloudFunctionsCount === undefined || cloudRunServicesCount === undefined) {
      // Count from actual vendor services
      cloudFunctionsCount = 0;
      cloudRunServicesCount = 0;
      if (discoveryData.vendors) {
        for (const vendor of discoveryData.vendors) {
          if (vendor.services) {
            for (const service of vendor.services) {
              if (service.type === 'cloud_function') {
                cloudFunctionsCount++;
              } else if (service.type === 'cloud_run') {
                cloudRunServicesCount++;
              }
            }
          }
        }
      }
    }

    res.json({
      success: true,
      project_id: projectId,
      discovery: discoveryData,
      timestamp: discoveryData.discovery_metadata?.discovery_timestamp || new Date().toISOString(),
      dev_mode: devMode ? {
        logs: logs.slice(-50), // Last 50 log lines
        apis: apis,
        resources: resources,
        summary: {
          cloud_functions: cloudFunctionsCount || 0,
          cloud_run_services: cloudRunServicesCount || 0,
          vendors_found: discoveryData.vendors?.length || 0
        }
      } : null
    });
  } catch (error) {
    logger.error(`Error fetching discovery results: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * API endpoint to load discovery results into Neo4j
 */
app.post('/api/discovery/load', async (req, res) => {
  try {
    const { project_id } = req.body;
    if (!project_id) {
      return res.status(400).json({ error: 'project_id is required' });
    }

    // Use promisified exec for child process
    const execPromise = promisify(exec);

    // Run the Python script to fetch and load discovery results (using venv Python)
    const scriptPath = path.join(__dirname, '..', 'scripts', 'fetch_discovery_results.py');
    const venvPython = path.join(__dirname, '..', 'venv', 'bin', 'python');
    const { stdout, stderr } = await execPromise(
      `"${venvPython}" "${scriptPath}" --project-id "${project_id}" --load-to-neo4j`
    );

    if (stderr && !stderr.includes('INFO') && !stderr.includes('WARNING')) {
      logger.warning(`Discovery load warnings: ${stderr}`);
    }

    // Update last data load time
    lastDataLoadTime = new Date().toISOString();
    logger.info(`Data loaded at: ${lastDataLoadTime}`);

    res.json({
      success: true,
      message: 'Discovery results loaded into Neo4j successfully',
      output: stdout,
      loadTime: lastDataLoadTime
    });
  } catch (error) {
    logger.error(`Error loading discovery results: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Health check endpoint
 */
app.get('/api/health', async (req, res) => {
  if (simulator && simulator.driver) {
    try {
      const session = simulator.driver.session();
      await session.run('RETURN 1 as test');
      await session.close();
      res.json({ status: 'healthy', neo4j: 'connected' });
    } catch (error) {
      res.status(500).json({ status: 'unhealthy', neo4j: 'disconnected' });
    }
  } else {
    // Return healthy but offline if simulator not initialized
    res.json({ status: 'healthy', neo4j: 'offline', mode: 'offline' });
  }
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');
  if (simulator) {
    await simulator.close();
  }
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully...');
  if (simulator) {
    await simulator.close();
  }
  process.exit(0);
});

// Start server
async function startServer() {
  const initialized = await initSimulator();
  
  // Start server regardless of simulator initialization status
  // This ensures the dashboard always loads, even if Neo4j is down
  app.listen(PORT, () => {
    logger.info('Starting Vendor Risk Digital Twin Dashboard...');
    logger.info(`Dashboard available at: http://localhost:${PORT}`);
    if (!initialized) {
      logger.warning('⚠️  Neo4j connection failed. Dashboard running in OFFLINE MODE.');
    }
  });
}

startServer();

