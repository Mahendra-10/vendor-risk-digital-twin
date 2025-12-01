# BigQuery Vendor Check Queries

**Purpose:** Commands to check if specific vendors are loaded in BigQuery dependencies table

---

## Table Schema

The `dependencies` table has the following columns:

- `vendor_name` (STRING, REQUIRED) - Vendor name
- `service_name` (STRING, REQUIRED) - Service name
- `resource_type` (STRING, REQUIRED) - Resource type (cloud_function, cloud_run)
- `resource_name` (STRING, REQUIRED) - Full GCP resource name
- `env_variable` (STRING, NULLABLE) - Environment variable that detected vendor
- `project_id` (STRING, REQUIRED) - GCP project ID
- `discovered_at` (TIMESTAMP, REQUIRED) - Discovery timestamp

## Quick Reference

### 1. List All Vendors

```bash
bq query --use_legacy_sql=false \
  'SELECT DISTINCT vendor_name 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   ORDER BY vendor_name'
```

### 2. Check if Specific Vendor Exists

```bash
# Replace "Auth0" with your vendor name
bq query --use_legacy_sql=false \
  'SELECT vendor_name, COUNT(*) as count 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE vendor_name = "Auth0" 
   GROUP BY vendor_name'
```

**Case-insensitive check:**
```bash
bq query --use_legacy_sql=false \
  'SELECT vendor_name, COUNT(*) as count 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE LOWER(vendor_name) = "auth0" 
   GROUP BY vendor_name'
```

### 3. Get All Records for a Vendor

```bash
bq query --use_legacy_sql=false \
  'SELECT * 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE vendor_name = "Auth0" 
   LIMIT 100'
```

### 4. Count Records Per Vendor

```bash
bq query --use_legacy_sql=false \
  'SELECT vendor_name, COUNT(*) as record_count 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   GROUP BY vendor_name 
   ORDER BY record_count DESC'
```

### 5. Check Multiple Vendors

```bash
bq query --use_legacy_sql=false \
  'SELECT vendor_name, COUNT(*) as count 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE vendor_name IN ("Auth0", "Stripe", "SendGrid") 
   GROUP BY vendor_name 
   ORDER BY vendor_name'
```

### 6. Search by Partial Name

```bash
# Find vendors containing "auth"
bq query --use_legacy_sql=false \
  'SELECT DISTINCT vendor_name 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE LOWER(vendor_name) LIKE "%auth%" 
   ORDER BY vendor_name'
```

---

## Output Formats

### Pretty JSON (default)
```bash
bq query --use_legacy_sql=false --format=prettyjson '...'
```

### CSV
```bash
bq query --use_legacy_sql=false --format=csv '...'
```

### Table (readable)
```bash
bq query --use_legacy_sql=false --format=pretty '...'
```

---

## Common Vendors to Check

Based on the project, common vendors include:

- **Auth0** - Authentication
- **Stripe** - Payment processing
- **SendGrid** - Email service
- **Twilio** - SMS/Communication
- **Datadog** - Monitoring
- **MongoDB** - Database
- **PayPal** - Payment processing
- **Okta** - Authentication

### Check All Common Vendors

```bash
bq query --use_legacy_sql=false \
  'SELECT vendor_name, COUNT(*) as count 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE vendor_name IN (
     "Auth0", "Stripe", "SendGrid", "Twilio", 
     "Datadog", "MongoDB", "PayPal", "Okta"
   ) 
   GROUP BY vendor_name 
   ORDER BY vendor_name'
```

---

## Using gcloud Instead of bq

If you prefer `gcloud`:

```bash
gcloud bq query \
  --use_legacy_sql=false \
  --format=json \
  'SELECT DISTINCT vendor_name 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   ORDER BY vendor_name'
```

---

## Troubleshooting

### Error: Table not found

**Check if table exists:**
```bash
bq ls vendor-risk-digital-twin:vendor_risk
```

**Check table schema:**
```bash
bq show --schema --format=prettyjson vendor-risk-digital-twin:vendor_risk.dependencies
```

### Error: Column not found

**List all columns:**
```bash
bq query --use_legacy_sql=false \
  'SELECT * 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   LIMIT 0'
```

### Case Sensitivity

Vendor names might be stored in different cases. Use `LOWER()` for case-insensitive matching:

```bash
bq query --use_legacy_sql=false \
  'SELECT DISTINCT vendor_name 
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` 
   WHERE LOWER(vendor_name) = LOWER("auth0")'
```

---

## Example Script

Create a script to check multiple vendors:

```bash
#!/bin/bash
# check_vendors.sh

VENDORS=("Auth0" "Stripe" "SendGrid" "Twilio")

for vendor in "${VENDORS[@]}"; do
  echo "Checking for $vendor..."
  bq query --use_legacy_sql=false --format=csv \
    "SELECT vendor_name, COUNT(*) as count 
     FROM \`vendor-risk-digital-twin.vendor_risk.dependencies\` 
     WHERE LOWER(vendor_name) = LOWER(\"$vendor\") 
     GROUP BY vendor_name" 2>&1 | tail -n +2
  echo ""
done
```

---

## Related Tables

### Check Simulations Table

```bash
bq query --use_legacy_sql=false \
  'SELECT DISTINCT vendor 
   FROM `vendor-risk-digital-twin.vendor_risk.simulations` 
   ORDER BY vendor'
```

### Join Dependencies and Simulations

```bash
bq query --use_legacy_sql=false \
  'SELECT 
     d.vendor_name,
     COUNT(DISTINCT d.service_id) as services,
     COUNT(DISTINCT s.simulation_id) as simulations
   FROM `vendor-risk-digital-twin.vendor_risk.dependencies` d
   LEFT JOIN `vendor-risk-digital-twin.vendor_risk.simulations` s
     ON LOWER(d.vendor_name) = LOWER(s.vendor)
   GROUP BY d.vendor_name
   ORDER BY d.vendor_name'
```

---

## Quick Commands Reference

```bash
# List all vendors
bq query --use_legacy_sql=false 'SELECT DISTINCT vendor_name FROM `vendor-risk-digital-twin.vendor_risk.dependencies` ORDER BY vendor_name'

# Check specific vendor (case-insensitive)
bq query --use_legacy_sql=false "SELECT vendor_name, COUNT(*) as count FROM \`vendor-risk-digital-twin.vendor_risk.dependencies\` WHERE LOWER(vendor_name) = LOWER(\"VENDOR_NAME\") GROUP BY vendor_name"

# Count all records
bq query --use_legacy_sql=false 'SELECT COUNT(*) as total FROM `vendor-risk-digital-twin.vendor_risk.dependencies`'

# Get sample records
bq query --use_legacy_sql=false 'SELECT * FROM `vendor-risk-digital-twin.vendor_risk.dependencies` LIMIT 10'
```

