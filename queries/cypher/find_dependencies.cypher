// Neo4j Cypher Queries - Find Dependencies

// 1. Find all services that depend on a specific vendor
MATCH (v:Vendor {name: 'Stripe'})<-[:DEPENDS_ON]-(s:Service)
RETURN v.name as vendor, 
       collect(s.name) as dependent_services;

// 2. Find all business processes affected by a vendor
MATCH (v:Vendor {name: 'Stripe'})<-[:DEPENDS_ON]-(s:Service)-[:SUPPORTS]->(bp:BusinessProcess)
RETURN v.name as vendor,
       s.name as service,
       collect(DISTINCT bp.name) as business_processes;

// 3. Find vendors by criticality level
MATCH (v:Vendor)
WHERE v.criticality = 'critical'
RETURN v.name as vendor,
       v.category as category,
       v.criticality as criticality
ORDER BY v.name;

// 4. Find all dependencies for a specific service
MATCH (s:Service {name: 'payment-api'})-[:DEPENDS_ON]->(v:Vendor)
RETURN s.name as service,
       collect(v.name) as vendors;

// 5. Find multi-vendor dependencies (services depending on multiple vendors)
MATCH (s:Service)-[:DEPENDS_ON]->(v:Vendor)
WITH s, collect(v.name) as vendors
WHERE size(vendors) > 1
RETURN s.name as service,
       vendors,
       size(vendors) as vendor_count
ORDER BY vendor_count DESC;

// 6. Find all services in a specific GCP region
MATCH (s:Service)
WHERE s.gcp_resource CONTAINS 'us-central1'
RETURN s.name as service,
       s.type as type,
       s.gcp_resource as resource;

// 7. Count services by type
MATCH (s:Service)
RETURN s.type as service_type,
       count(s) as count
ORDER BY count DESC;

// 8. Find vendor dependency chain (2 levels deep)
MATCH path = (v1:Vendor)<-[:DEPENDS_ON]-(s:Service)-[:DEPENDS_ON]->(v2:Vendor)
WHERE v1.name <> v2.name
RETURN v1.name as primary_vendor,
       s.name as service,
       v2.name as secondary_vendor;

// 9. Find services with high request volume (RPM > 500)
MATCH (s:Service)-[:DEPENDS_ON]->(v:Vendor)
WHERE s.rpm > 500
RETURN v.name as vendor,
       s.name as service,
       s.rpm as requests_per_minute
ORDER BY s.rpm DESC;

// 10. Find all business processes and their vendor dependencies
MATCH (bp:BusinessProcess)<-[:SUPPORTS]-(s:Service)-[:DEPENDS_ON]->(v:Vendor)
RETURN bp.name as business_process,
       collect(DISTINCT v.name) as vendors,
       collect(DISTINCT s.name) as services
ORDER BY bp.name;

