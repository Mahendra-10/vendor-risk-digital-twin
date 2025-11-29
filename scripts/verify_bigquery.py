"""Quick script to verify BigQuery data"""
from google.cloud import bigquery

client = bigquery.Client(project='vendor-risk-digital-twin')
query = """
SELECT 
    simulation_id, 
    vendor_name, 
    duration_hours, 
    overall_score, 
    services_affected, 
    customers_affected, 
    revenue_loss, 
    timestamp 
FROM `vendor-risk-digital-twin.vendor_risk.simulations` 
ORDER BY timestamp DESC 
LIMIT 5
"""

results = client.query(query).result()
print('✅ BigQuery Data Verification:')
print('='*60)
for row in results:
    print(f'  Simulation ID: {row.simulation_id}')
    print(f'  Vendor: {row.vendor_name}')
    print(f'  Duration: {row.duration_hours} hours')
    print(f'  Impact Score: {row.overall_score:.2f}')
    print(f'  Services Affected: {row.services_affected}')
    print(f'  Customers Affected: {row.customers_affected:,}')
    print(f'  Revenue Loss: ${row.revenue_loss:,.2f}')
    print(f'  Timestamp: {row.timestamp}')
    print('='*60)

