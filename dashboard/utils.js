/**
 * Utility functions for Vendor Risk Digital Twin
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import yaml from 'js-yaml';
import dotenv from 'dotenv';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '..');

// Load environment variables from project root
dotenv.config({ path: path.join(PROJECT_ROOT, '.env') });

/**
 * Setup logging (simple console logger)
 */
export function setupLogging(logLevel = 'INFO') {
  const levels = { DEBUG: 0, INFO: 1, WARNING: 2, ERROR: 3 };
  const currentLevel = levels[logLevel.toUpperCase()] || 1;

  return {
    debug: (msg) => currentLevel <= 0 && console.log(`[DEBUG] ${msg}`),
    info: (msg) => currentLevel <= 1 && console.log(`[INFO] ${msg}`),
    warning: (msg) => currentLevel <= 2 && console.warn(`[WARNING] ${msg}`),
    error: (msg) => currentLevel <= 3 && console.error(`[ERROR] ${msg}`),
  };
}

/**
 * Load configuration from YAML file with environment variable substitution
 */
export function loadConfig(configPath = 'config/config.yaml') {
  const configFile = path.join(PROJECT_ROOT, configPath);

  if (!fs.existsSync(configFile)) {
    throw new Error(`Config file not found: ${configFile}`);
  }

  const content = fs.readFileSync(configFile, 'utf8');
  let config = yaml.load(content);

  // Substitute environment variables
  config = substituteEnvVars(config);

  return config;
}

/**
 * Recursively substitute environment variables in config
 */
function substituteEnvVars(config) {
  if (typeof config === 'object' && config !== null) {
    if (Array.isArray(config)) {
      return config.map(item => substituteEnvVars(item));
    }
    const result = {};
    for (const [key, value] of Object.entries(config)) {
      result[key] = substituteEnvVars(value);
    }
    return result;
  } else if (typeof config === 'string' && config.startsWith('${') && config.endsWith('}')) {
    const envVar = config.slice(2, -1);
    return process.env[envVar] || config;
  }
  return config;
}

/**
 * Load JSON file
 */
export function loadJsonFile(filePath) {
  const fullPath = path.join(PROJECT_ROOT, filePath);

  if (!fs.existsSync(fullPath)) {
    throw new Error(`JSON file not found: ${fullPath}`);
  }

  const content = fs.readFileSync(fullPath, 'utf8');
  return JSON.parse(content);
}

/**
 * Save data to JSON file
 */
export function saveJsonFile(data, filePath, indent = 2) {
  const fullPath = path.join(PROJECT_ROOT, filePath);

  // Create directory if it doesn't exist
  const dir = path.dirname(fullPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  fs.writeFileSync(fullPath, JSON.stringify(data, null, indent));
}

/**
 * Get project root directory
 */
export function getProjectRoot() {
  return PROJECT_ROOT;
}

/**
 * Validate that required environment variables are set
 */
export function validateEnvVars(requiredVars) {
  const missingVars = requiredVars.filter(varName => !process.env[varName]);

  if (missingVars.length > 0) {
    console.error(`Missing required environment variables: ${missingVars.join(', ')}`);
    return false;
  }

  return true;
}

/**
 * Format amount as currency
 */
export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format value as percentage
 */
export function formatPercentage(value) {
  return `${(value * 100).toFixed(1)}%`;
}

/**
 * Calculate weighted impact score
 */
export function calculateImpactScore(
  operationalImpact,
  financialImpact,
  complianceImpact,
  weights = null
) {
  if (!weights) {
    weights = {
      operational: 0.4,
      financial: 0.35,
      compliance: 0.25,
    };
  }

  const score =
    operationalImpact * weights.operational +
    financialImpact * weights.financial +
    complianceImpact * weights.compliance;

  return Math.min(Math.max(score, 0.0), 1.0); // Clamp between 0 and 1
}

