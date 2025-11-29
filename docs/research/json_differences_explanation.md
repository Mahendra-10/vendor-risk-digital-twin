# Why Local vs Cloud Run JSON Output Differs

## Summary

The JSON output differs between local and Cloud Run because:
1. **Cloud Run is using an OLD version** of `scripts/simulate_failure.py` that doesn't have vendor name lookup fixes
2. **Different empty state formats**: Python returns `[]` (array) when no data, JavaScript returns `{}` (object)
3. **Missing vendor name normalization**: Cloud Run can't find compliance data because it looks for `"auth0"` but data has `"Auth0"`

---

## Detailed Comparison

### 1. Compliance Impact Structure

#### ✅ Local (Working - Has Data)
```json
{
  "compliance_impact": {
    "affected_frameworks": {
      "soc2": { "baseline_score": 0.92, "new_score": 0.77, ... },
      "nist": { "baseline_score": 0.88, "new_score": 0.73, ... },
      "iso27001": { "baseline_score": 0.9, "new_score": 0.75, ... }
    },
    "impact_score": 0.15,
    "summary": {
      "soc2": { "change": "15.0%", "new_score": "77.0%" },
      "nist": { "change": "15.0%", "new_score": "73.0%" },
      "iso27001": { "change": "15.0%", "new_score": "75.0%" }
    }
  }
}
```

#### ❌ Cloud Run (Broken - No Data)
```json
{
  "compliance_impact": {
    "affected_frameworks": [],  // Empty ARRAY (should be object or have data)
    "impact_score": 0,
    // Missing "summary" field
  }
}
```

---

### 2. Vendor Name Formatting

#### ✅ Local
- Vendor name: `"Auth0"` (properly capitalized)
- Recommendations use: `"Auth0"`

#### ❌ Cloud Run
- Vendor name: `"auth0"` (lowercase)
- Recommendations use: `"auth0"` (lowercase)

---

## Root Causes

### Cause 1: Cloud Run Has Old Code Without Vendor Name Lookup Fixes

**Local Code (Current - `scripts/simulate_failure.py` lines 285-315):**
```python
# Try exact match first (compliance data uses "Auth0", "Stripe", etc.)
vendor_controls = control_mappings.get(vendor_name, {})

# If not found, try common variations
if not vendor_controls:
    vendor_lower = vendor_name.lower().strip()
    
    # Map common lowercase variations to compliance data keys
    name_mapping = {
        'auth0': 'Auth0',
        'stripe': 'Stripe',
        'sendgrid': 'SendGrid',
        'mongodb atlas': 'MongoDB Atlas',
        'twilio': 'Twilio'
    }
    
    if vendor_lower in name_mapping:
        vendor_controls = control_mappings.get(name_mapping[vendor_lower], {})
```

**Cloud Run Code (Old Version):**
```python
# OLD CODE - Only does simple lookup
vendor_controls = control_mappings.get(vendor_name, {})  # vendor_name = "auth0"
# Looks for "auth0" but compliance data has "Auth0" → NOT FOUND
# Returns empty result
```

**Result:** Cloud Run receives `"auth0"` (lowercase), looks for `"auth0"` in compliance data, but data has `"Auth0"` → **No match → Empty compliance impact**

---

### Cause 2: Different Empty State Formats

**Python Script (`scripts/simulate_failure.py` line 319):**
```python
if not vendor_controls:
    return {
        'affected_frameworks': [],  # Empty ARRAY
        'impact_score': 0.0
    }
```

**JavaScript Simulator (`dashboard/simulator.js` line 251):**
```javascript
if (Object.keys(vendorControls).length === 0) {
  return {
    affected_frameworks: {},  // Empty OBJECT
    impact_score: 0.0,
    summary: {},  // Always includes summary
  };
}
```

**Why this matters:**
- Python uses `[]` (array) for empty state
- JavaScript uses `{}` (object) for empty state
- When Cloud Run finds no data, it returns `[]` instead of `{}`
- Dashboard expects `{}` or an object with framework keys

---

### Cause 3: Missing Summary Field in Cloud Run

**Current Python Code (lines 360-366):**
```python
return {
    'affected_frameworks': frameworks,
    'impact_score': impact_score,
    'summary': {  # Always includes summary when data exists
        framework: {
            'change': format_percentage(data['score_change']),
            'new_score': format_percentage(data['new_score'])
        }
        for framework, data in frameworks.items()
    }
}
```

**Cloud Run (Old Code):**
- When `vendor_controls` is empty, returns early without `summary` field
- Even when data exists, old code might not generate `summary` correctly

---

## Code Path Comparison

### Local Flow (Working)
1. Dashboard sends: `vendor: "Auth0"` (from dropdown)
2. `server.js` normalizes to: `"auth0"` (lowercase)
3. `simulator.js` receives: `"Auth0"` (original name preserved)
4. `_calculateComplianceImpact("Auth0")`:
   - Looks for `"Auth0"` → ✅ **FOUND**
   - Returns compliance data with `summary`

### Cloud Run Flow (Broken)
1. Dashboard sends: `vendor: "auth0"` (normalized lowercase)
2. Cloud Run receives: `"auth0"`
3. `simulate_vendor_failure("auth0")`:
   - Calls `_calculate_compliance_impact("auth0")`
   - Old code looks for `"auth0"` → ❌ **NOT FOUND** (data has `"Auth0"`)
   - Returns `affected_frameworks: []`, no `summary`

---

## Solution

### Option 1: Disable Cloud Run (Current Solution)
✅ **Already done** - `dashboard/server.js` line 231: `const enableCloudRun = false;`

This forces local simulator usage, which has all the fixes.

### Option 2: Redeploy Cloud Run with Updated Code
1. Ensure `scripts/simulate_failure.py` has the vendor name lookup fixes (lines 285-315)
2. Ensure `cloud_run/simulation-service/Dockerfile` copies the latest code
3. Redeploy: `gcloud run deploy simulation-service --source cloud_run/simulation-service`
4. Re-enable Cloud Run: `const enableCloudRun = true;`

### Option 3: Fix Empty State Format Consistency
Update Python code to return `{}` instead of `[]` for consistency:
```python
if not vendor_controls:
    return {
        'affected_frameworks': {},  # Change from [] to {}
        'impact_score': 0.0,
        'summary': {}  # Always include summary
    }
```

---

## Verification

To verify Cloud Run has the fixes:
1. Check Cloud Run logs for vendor name lookup
2. Look for: `"Calculating compliance impact..."` followed by framework data
3. Check if `affected_frameworks` is an object `{}` or array `[]`
4. Verify `summary` field exists in response

---

## Summary Table

| Feature | Local (✅ Working) | Cloud Run (❌ Broken) |
|---------|-------------------|----------------------|
| **Vendor Name** | `"Auth0"` (capitalized) | `"auth0"` (lowercase) |
| **Compliance Lookup** | ✅ Finds "Auth0" | ❌ Looks for "auth0", not found |
| **affected_frameworks** | `{}` (object) or data | `[]` (empty array) |
| **summary field** | ✅ Always present | ❌ Missing when no data |
| **Code Version** | Latest with fixes | Old version without fixes |

---

## Next Steps

1. ✅ **Current**: Cloud Run disabled, using local simulator
2. **Future**: Redeploy Cloud Run with updated code to enable automatic BigQuery saving
3. **Optional**: Standardize empty state format (`{}` vs `[]`) for consistency

