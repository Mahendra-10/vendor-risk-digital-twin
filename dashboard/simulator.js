/**
 * Vendor Failure Simulation Engine
 * 
 * Simulates vendor failure scenarios and predicts impact on:
 * - Operations (affected services, business processes)
 * - Finance (revenue loss, transaction failures)
 * - Compliance (control failures, framework score changes)
 */

import neo4j from 'neo4j-driver';
import {
  loadConfig,
  loadJsonFile,
  formatCurrency,
  formatPercentage,
  calculateImpactScore,
  setupLogging,
} from './utils.js';

export class VendorFailureSimulator {
  /**
   * Initialize simulator
   * 
   * @param {string} neo4jUri - Neo4j connection URI
   * @param {string} neo4jUser - Neo4j username
   * @param {string} neo4jPassword - Neo4j password
   */
  constructor(neo4jUri, neo4jUser, neo4jPassword) {
    this.logger = setupLogging(process.env.LOG_LEVEL || 'INFO');
    this.driver = neo4j.driver(neo4jUri, neo4j.auth.basic(neo4jUser, neo4jPassword));
    this.config = loadConfig();
    this.complianceData = loadJsonFile('data/sample/compliance_controls.json');
    this.logger.info('Simulator initialized');
  }

  /**
   * Close Neo4j connection
   */
  async close() {
    await this.driver.close();
  }

  /**
   * Simulate vendor failure and calculate impact
   * 
   * @param {string} vendorName - Name of the vendor
   * @param {number} durationHours - Failure duration in hours
   * @returns {Promise<Object>} Simulation results
   */
  async simulateVendorFailure(vendorName, durationHours) {
    this.logger.info(`🔴 Simulating ${vendorName} failure for ${durationHours} hours...`);

    const simulation = {
      vendor: vendorName,
      duration_hours: durationHours,
      timestamp: new Date().toISOString(),
      operational_impact: {},
      financial_impact: {},
      compliance_impact: {},
      overall_impact_score: 0.0,
      recommendations: [],
    };

    // Calculate operational impact
    const operational = await this._calculateOperationalImpact(vendorName);
    simulation.operational_impact = operational;

    // Calculate financial impact
    const financial = this._calculateFinancialImpact(vendorName, durationHours, operational);
    simulation.financial_impact = financial;

    // Calculate compliance impact
    const compliance = this._calculateComplianceImpact(vendorName);
    simulation.compliance_impact = compliance;

    // Calculate overall impact score
    simulation.overall_impact_score = calculateImpactScore(
      operational.impact_score,
      financial.impact_score,
      compliance.impact_score
    );

    // Generate recommendations
    simulation.recommendations = this._generateRecommendations(simulation);

    this.logger.info(
      `✅ Simulation complete. Impact score: ${simulation.overall_impact_score.toFixed(2)}`
    );
    return simulation;
  }

  /**
   * Calculate operational impact
   * 
   * @param {string} vendorName - Vendor name
   * @returns {Promise<Object>} Operational impact details
   */
  async _calculateOperationalImpact(vendorName) {
    this.logger.info(`Calculating operational impact for vendor: "${vendorName}"...`);

    const session = this.driver.session();
    try {
      // Normalize vendor name to lowercase to match Neo4j storage format
      const normalizedVendorName = vendorName.toLowerCase().trim();
      this.logger.info(`Normalized vendor name: "${normalizedVendorName}"`);
      
      // First, check if vendor exists
      const vendorCheck = await session.run(
        'MATCH (v:Vendor {name: $vendor_name}) RETURN v.name as name, v.display_name as display_name',
        { vendor_name: normalizedVendorName }
      );
      
      if (vendorCheck.records.length === 0) {
        this.logger.warn(`Vendor "${normalizedVendorName}" not found in Neo4j`);
        // Try to find similar vendor names
        const similarVendors = await session.run(
          'MATCH (v:Vendor) WHERE toLower(v.name) CONTAINS toLower($search) OR toLower(COALESCE(v.display_name, "")) CONTAINS toLower($search) RETURN v.name as name, v.display_name as display_name LIMIT 5',
          { search: normalizedVendorName }
        );
        if (similarVendors.records.length > 0) {
          this.logger.warn(`Found similar vendors: ${similarVendors.records.map(r => r.get('name')).join(', ')}`);
        }
      } else {
        const vendorRecord = vendorCheck.records[0];
        this.logger.info(`Found vendor: name="${vendorRecord.get('name')}", display_name="${vendorRecord.get('display_name')}"`);
      }
      
      const query = `
        MATCH (v:Vendor {name: $vendor_name})<-[:DEPENDS_ON]-(s:Service)
        OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
        RETURN s.name as service_name,
               s.type as service_type,
               s.rpm as rpm,
               s.customers_affected as customers_affected,
               collect(DISTINCT bp.name) as business_processes
      `;

      const result = await session.run(query, { vendor_name: normalizedVendorName });
      this.logger.info(`Query returned ${result.records.length} service records`);

      const affectedServices = [];
      let totalRpm = 0;
      let customersAffected = 0;
      const businessProcesses = new Set();

      for (const record of result.records) {
        // Convert Neo4j integers (BigInt) to regular numbers
        const rpmValue = record.get('rpm');
        const customersValue = record.get('customers_affected');
        
        const service = {
          name: record.get('service_name'),
          type: record.get('service_type'),
          rpm: rpmValue ? Number(rpmValue) : 0,
          customers_affected: customersValue ? Number(customersValue) : 0,
          business_processes: record.get('business_processes') || [],
        };
        affectedServices.push(service);
        totalRpm += service.rpm;
        customersAffected = Math.max(customersAffected, service.customers_affected);
        service.business_processes.forEach(bp => businessProcesses.add(bp));
      }

      // Calculate impact score (0.0 to 1.0)
      const impactScore = Math.min(affectedServices.length / 10, 1.0); // Normalize

      return {
        affected_services: affectedServices,
        service_count: affectedServices.length,
        total_rpm: totalRpm,
        customers_affected: customersAffected,
        business_processes: Array.from(businessProcesses).sort(),
        impact_score: impactScore,
      };
    } finally {
      await session.close();
    }
  }

  /**
   * Calculate financial impact
   * 
   * @param {string} vendorName - Vendor name
   * @param {number} durationHours - Failure duration
   * @param {Object} operational - Operational impact data
   * @returns {Object} Financial impact details
   */
  _calculateFinancialImpact(vendorName, durationHours, operational) {
    this.logger.info('Calculating financial impact...');

    // Get business metrics from config
    const businessMetrics = this.config.simulation.business;
    const revenuePerHour = businessMetrics.revenue_per_hour;

    // Calculate revenue loss based on affected services
    // Assume revenue loss proportional to number of critical services affected
    const serviceCount = operational.service_count;
    const revenueLossPercentage = Math.min(serviceCount * 0.25, 1.0); // 25% per service, max 100%

    const revenueLoss = revenuePerHour * durationHours * revenueLossPercentage;

    // Calculate transaction failures
    const transactionsPerHour = businessMetrics.transactions_per_hour;
    const failedTransactions = Math.floor(
      transactionsPerHour * durationHours * revenueLossPercentage
    );

    // Customer impact cost (estimated)
    const customersAffected = operational.customers_affected;
    const customerImpactCost = customersAffected * 5; // $5 per affected customer

    const totalCost = revenueLoss + customerImpactCost;

    // Impact score
    const impactScore = Math.min(totalCost / 1000000, 1.0); // Normalize to $1M

    return {
      revenue_loss: revenueLoss,
      revenue_loss_formatted: formatCurrency(revenueLoss),
      failed_transactions: failedTransactions,
      customer_impact_cost: customerImpactCost,
      total_cost: totalCost,
      total_cost_formatted: formatCurrency(totalCost),
      impact_score: impactScore,
    };
  }

  /**
   * Calculate compliance impact
   * 
   * @param {string} vendorName - Vendor name
   * @returns {Object} Compliance impact details
   */
  _calculateComplianceImpact(vendorName) {
    this.logger.info('Calculating compliance impact...');

    // Get vendor's compliance controls (case-insensitive lookup)
    const controlMappings = this.complianceData.control_mappings || {};
    // Try exact match first, then case-insensitive
    let vendorControls = controlMappings[vendorName] || {};
    if (Object.keys(vendorControls).length === 0) {
      // Try case-insensitive match
      const vendorKey = Object.keys(controlMappings).find(
        key => key.toLowerCase() === vendorName.toLowerCase()
      );
      vendorControls = vendorKey ? controlMappings[vendorKey] : {};
    }

    if (Object.keys(vendorControls).length === 0) {
      return {
        affected_frameworks: {},
        impact_score: 0.0,
        summary: {},
      };
    }

    // Get impact weights
    const impactWeights = this.complianceData.impact_weights || {};
    const baseline = this.complianceData.compliance_baseline || {};

    // Calculate impact for each framework
    const frameworks = {};
    let totalImpact = 0;
    let frameworkCount = 0;

    for (const [framework, controlIds] of Object.entries(vendorControls)) {
      const frameworkKey = framework.replace('_controls', '');
      if (!impactWeights[frameworkKey]) {
        continue;
      }

      // Calculate score reduction
      let scoreReduction = 0;
      for (const ctrl of controlIds) {
        scoreReduction += impactWeights[frameworkKey][ctrl] || 0.05;
      }

      const baselineScore = baseline[`${frameworkKey}_score`] || 0.9;
      const newScore = Math.max(baselineScore - scoreReduction, 0.0);

      frameworks[frameworkKey] = {
        baseline_score: baselineScore,
        new_score: newScore,
        score_change: scoreReduction,
        affected_controls: controlIds,
      };

      totalImpact += scoreReduction;
      frameworkCount++;
    }

    // Overall compliance impact score
    const impactScore = frameworkCount > 0
      ? Math.min(totalImpact / frameworkCount, 1.0)
      : 0.0;

    // Create summary
    const summary = {};
    for (const [framework, frameworkData] of Object.entries(frameworks)) {
      summary[framework] = {
        change: formatPercentage(frameworkData.score_change),
        new_score: formatPercentage(frameworkData.new_score),
      };
    }

    return {
      affected_frameworks: frameworks,
      impact_score: impactScore,
      summary,
    };
  }

  /**
   * Generate remediation recommendations
   * 
   * @param {Object} simulation - Simulation results
   * @returns {Array<string>} List of recommendations
   */
  _generateRecommendations(simulation) {
    const recommendations = [];
    const vendor = simulation.vendor;

    // Operational recommendations
    const serviceCount = simulation.operational_impact.service_count;
    if (serviceCount > 0) {
      recommendations.push(
        `Implement fallback mechanisms for ${serviceCount} services depending on ${vendor}`
      );
      recommendations.push(
        'Consider vendor diversification for critical business processes'
      );
    }

    // Financial recommendations
    const totalCost = simulation.financial_impact.total_cost;
    if (totalCost > 100000) {
      recommendations.push(
        `High financial impact detected (${formatCurrency(totalCost)}). ` +
        'Implement circuit breakers and graceful degradation'
      );
    }

    // Compliance recommendations
    const compliance = simulation.compliance_impact;
    if (compliance.impact_score > 0.1) {
      recommendations.push(
        'Compliance impact significant. Review compensating controls for affected frameworks'
      );
      for (const [framework, frameworkData] of Object.entries(compliance.summary || {})) {
        recommendations.push(
          `  - ${framework.toUpperCase()}: Score drops to ${frameworkData.new_score}`
        );
      }
    }

    return recommendations;
  }
}

