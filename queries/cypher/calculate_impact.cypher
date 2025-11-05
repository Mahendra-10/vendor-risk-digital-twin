// Neo4j Cypher Queries - Calculate Impact

// 1. Calculate total impact if vendor fails (count affected resources)
MATCH (v:Vendor {name: 'Stripe'})<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
RETURN v.name as vendor,
       count(DISTINCT s) as affected_services,
       count(DISTINCT bp) as affected_processes,
       count(DISTINCT cc) as affected_controls,
       sum(s.rpm) as total_rpm_affected,
       max(s.customers_affected) as customers_impacted;

// 2. Find compliance controls at risk if vendor fails
MATCH (v:Vendor {name: 'Auth0'})-[:SATISFIES]->(cc:ComplianceControl)
RETURN v.name as vendor,
       cc.control_id as control_id,
       cc.framework as framework
ORDER BY cc.framework, cc.control_id;

// 3. Calculate cascading impact (find all connected resources)
MATCH path = (v:Vendor {name: 'Stripe'})<-[:DEPENDS_ON*1..3]-(resource)
RETURN DISTINCT labels(resource)[0] as resource_type,
       count(resource) as count;

// 4. Identify single points of failure (business processes with only one vendor)
MATCH (bp:BusinessProcess)<-[:SUPPORTS]-(s:Service)-[:DEPENDS_ON]->(v:Vendor)
WITH bp, collect(DISTINCT v.name) as vendors
WHERE size(vendors) = 1
RETURN bp.name as business_process,
       vendors[0] as single_vendor,
       'HIGH_RISK' as risk_level;

// 5. Calculate vendor criticality score based on dependencies
MATCH (v:Vendor)<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
OPTIONAL MATCH (v)-[:SATISFIES]->(cc:ComplianceControl)
WITH v,
     count(DISTINCT s) as service_count,
     count(DISTINCT bp) as process_count,
     count(DISTINCT cc) as control_count,
     sum(s.rpm) as total_rpm
RETURN v.name as vendor,
       v.criticality as stated_criticality,
       service_count,
       process_count,
       control_count,
       total_rpm,
       (service_count * 10 + process_count * 15 + control_count * 5) as calculated_score
ORDER BY calculated_score DESC;

// 6. Find vendors affecting the same business process (substitute vendors)
MATCH (bp:BusinessProcess)<-[:SUPPORTS]-(s1:Service)-[:DEPENDS_ON]->(v1:Vendor)
MATCH (bp)<-[:SUPPORTS]-(s2:Service)-[:DEPENDS_ON]->(v2:Vendor)
WHERE v1 <> v2
RETURN bp.name as business_process,
       collect(DISTINCT v1.name) as vendor_1,
       collect(DISTINCT v2.name) as vendor_2,
       'POTENTIAL_REDUNDANCY' as note;

// 7. Calculate percentage of services affected if vendor fails
MATCH (s:Service)
WITH count(s) as total_services
MATCH (v:Vendor {name: 'MongoDB Atlas'})<-[:DEPENDS_ON]-(affected:Service)
WITH total_services, count(affected) as affected_count
RETURN affected_count,
       total_services,
       round(100.0 * affected_count / total_services) as percentage_affected;

// 8. Identify critical path (vendors affecting critical business processes)
MATCH (v:Vendor)<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
WHERE bp.name IN ['checkout', 'user_login', 'payment_processing']
RETURN v.name as vendor,
       v.criticality as criticality,
       collect(DISTINCT bp.name) as critical_processes
ORDER BY size(critical_processes) DESC;

// 9. Find vendor concentration risk (multiple services in same category)
MATCH (v:Vendor)<-[:DEPENDS_ON]-(s:Service)
WITH v, count(s) as dependency_count
WHERE dependency_count > 2
RETURN v.name as vendor,
       v.category as category,
       dependency_count,
       'CONCENTRATION_RISK' as risk_type
ORDER BY dependency_count DESC;

// 10. Calculate compliance framework coverage by vendor
MATCH (cc:ComplianceControl)<-[:SATISFIES]-(v:Vendor)
WITH v, cc.framework as framework, count(cc) as control_count
RETURN v.name as vendor,
       collect({
           framework: framework,
           controls: control_count
       }) as framework_coverage
ORDER BY v.name;

// 11. Simulate multi-vendor failure (worst case scenario)
UNWIND ['Stripe', 'Auth0', 'MongoDB Atlas'] as vendor_name
MATCH (v:Vendor {name: vendor_name})<-[:DEPENDS_ON]-(s:Service)
OPTIONAL MATCH (s)-[:SUPPORTS]->(bp:BusinessProcess)
WITH vendor_name,
     count(DISTINCT s) as services,
     collect(DISTINCT bp.name) as processes
RETURN vendor_name,
       services,
       processes,
       size(processes) as process_count
ORDER BY process_count DESC;

// 12. Find redundant vendor coverage (good for resilience)
MATCH (bp:BusinessProcess)<-[:SUPPORTS]-(s:Service)-[:DEPENDS_ON]->(v:Vendor)
WHERE v.category = 'payment_processor'
WITH bp, collect(DISTINCT v.name) as payment_vendors
WHERE size(payment_vendors) > 1
RETURN bp.name as business_process,
       payment_vendors,
       'REDUNDANCY_EXISTS' as status;

