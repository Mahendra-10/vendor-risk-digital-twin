# Cloud Scheduler: Simulation Automation Options

## Current Status

**Cloud Scheduler currently only runs:**
- ✅ Discovery Function (daily at 2 AM)

**Cloud Scheduler does NOT run:**
- ❌ Simulation Service (manual trigger only)

---

## Why Simulation Isn't Scheduled (Currently)

### 1. **Requires User Input**
Simulation needs specific parameters:
- **Vendor name** (e.g., "Stripe", "Auth0", "SendGrid")
- **Failure duration** (1, 2, 4, 8, 24, or 72 hours)
- **Business context** (which scenario to analyze)

### 2. **Context-Dependent**
Simulations are typically run:
- When evaluating a specific vendor risk
- Before making vendor decisions
- For compliance assessments
- During incident planning

### 3. **Resource Considerations**
- Simulations query Neo4j and calculate impacts
- Multiple automated simulations could increase costs
- Results are stored in BigQuery

---

## Option 1: Schedule Default Simulation

### Use Case
Run a standard simulation automatically (e.g., weekly) for monitoring purposes.

### Implementation

```bash
# Add to setup_cloud_scheduler.sh
SIMULATION_SERVICE_URL="https://simulation-service-16418516910.us-central1.run.app"

# Create weekly simulation job
gcloud scheduler jobs create http weekly-vendor-simulation \
    --location=us-central1 \
    --schedule="0 3 * * 1" \
    --uri="${SIMULATION_SERVICE_URL}/simulate" \
    --http-method=POST \
    --message-body='{"vendor": "Stripe", "duration_hours": 4}' \
    --headers="Content-Type=application/json" \
    --time-zone="America/Los_Angeles" \
    --description="Weekly automated simulation for Stripe (4-hour failure)"
```

### Pros
- ✅ Automated risk monitoring
- ✅ Regular compliance checks
- ✅ Historical trend data

### Cons
- ❌ Fixed parameters (may not reflect current needs)
- ❌ Additional costs
- ❌ May generate unnecessary data

---

## Option 2: Schedule Multiple Vendors (Rotation)

### Use Case
Run simulations for different vendors on different days.

### Implementation

```bash
# Monday: Stripe
gcloud scheduler jobs create http weekly-simulation-stripe \
    --schedule="0 3 * * 1" \
    --uri="${SIMULATION_SERVICE_URL}/simulate" \
    --message-body='{"vendor": "Stripe", "duration_hours": 4}'

# Tuesday: Auth0
gcloud scheduler jobs create http weekly-simulation-auth0 \
    --schedule="0 3 * * 2" \
    --uri="${SIMULATION_SERVICE_URL}/simulate" \
    --message-body='{"vendor": "Auth0", "duration_hours": 4}'

# Wednesday: SendGrid
gcloud scheduler jobs create http weekly-simulation-sendgrid \
    --schedule="0 3 * * 3" \
    --uri="${SIMULATION_SERVICE_URL}/simulate" \
    --message-body='{"vendor": "SendGrid", "duration_hours": 4}'
```

### Pros
- ✅ Comprehensive coverage of all vendors
- ✅ Regular risk assessment rotation
- ✅ Historical comparison data

### Cons
- ❌ Multiple scheduled jobs to manage
- ❌ Higher costs (more simulations)
- ❌ May not align with actual risk priorities

---

## Option 3: Schedule After Discovery

### Use Case
Automatically run simulation after discovery completes, using newly discovered vendors.

### Implementation

This would require:
1. Discovery Function publishes vendor list to Pub/Sub
2. A new Cloud Function subscribes to discovery events
3. Function triggers simulation for each discovered vendor

**Flow:**
```
Discovery Function
    ↓
Cloud Storage (discovery results)
    ↓
Pub/Sub (vendor list)
    ↓
Simulation Trigger Function (NEW)
    ↓
Simulation Service (for each vendor)
```

### Pros
- ✅ Simulations based on actual discovered vendors
- ✅ Automatic risk assessment of new dependencies
- ✅ No manual configuration needed

### Cons
- ❌ More complex architecture
- ❌ Requires new Cloud Function
- ❌ May run many simulations (cost)

---

## Option 4: Keep Manual (Recommended)

### Use Case
Run simulations only when needed for specific business decisions.

### Current Flow
```
User clicks "Run Simulation" in Dashboard
    ↓
Dashboard API → Simulation Service
    ↓
Results displayed immediately
    ↓
Stored in BigQuery for historical analysis
```

### Pros
- ✅ Context-aware (right vendor, right duration)
- ✅ Cost-effective (only when needed)
- ✅ User controls what to analyze
- ✅ Results are immediately actionable

### Cons
- ❌ Requires manual intervention
- ❌ No automated monitoring

---

## Recommendation

### For Production Use
**Keep simulation manual** because:
1. Simulations are decision-support tools
2. They should be run with specific business context
3. Automated simulations may not provide actionable insights
4. Cost optimization (only run when needed)

### For Monitoring Use
**Option 1 (Default Simulation)** if you want:
- Regular risk monitoring
- Historical trend analysis
- Automated compliance tracking

### For Comprehensive Coverage
**Option 2 (Rotation)** if you want:
- All vendors assessed regularly
- Systematic risk management
- Complete historical data

---

## Implementation Guide (If You Want to Add It)

### Step 1: Update Setup Script

Add to `scripts/setup_cloud_scheduler.sh`:

```bash
# Simulation service URL
SIMULATION_SERVICE_URL="https://simulation-service-16418516910.us-central1.run.app"

# Optional: Create weekly simulation job
if [ "$ENABLE_SIMULATION_SCHEDULING" = "true" ]; then
    echo "📅 Creating weekly simulation scheduler job..."
    
    gcloud scheduler jobs create http weekly-vendor-simulation \
        --location=$REGION \
        --schedule="0 3 * * 1" \
        --uri="${SIMULATION_SERVICE_URL}/simulate" \
        --http-method=POST \
        --message-body='{"vendor": "Stripe", "duration_hours": 4}' \
        --headers="Content-Type=application/json" \
        --time-zone="America/Los_Angeles" \
        --description="Weekly automated vendor failure simulation" \
        --project=$PROJECT_ID
    
    echo "   ✅ Weekly simulation job created"
fi
```

### Step 2: Verify Simulation Service Endpoint

```bash
# Test the endpoint
curl -X POST "${SIMULATION_SERVICE_URL}/simulate" \
  -H "Content-Type: application/json" \
  -d '{"vendor": "Stripe", "duration_hours": 4}'
```

### Step 3: Test Scheduled Job

```bash
# Run immediately to test
gcloud scheduler jobs run weekly-vendor-simulation \
    --location=us-central1
```

---

## Cost Considerations

### Discovery (Currently Scheduled)
- **Frequency:** Daily
- **Cost:** ~$0.0001 per execution
- **Monthly:** ~$0.003

### Simulation (If Scheduled)
- **Frequency:** Weekly (example)
- **Cost:** ~$0.001 per execution (Cloud Run + Neo4j queries + BigQuery)
- **Monthly:** ~$0.004

**Total:** Minimal cost impact

---

## Summary

| Option | Automation | Complexity | Cost | Use Case |
|--------|-----------|------------|------|----------|
| **Keep Manual** | ❌ | Low | Low | Decision support |
| **Default Simulation** | ✅ | Low | Low | Regular monitoring |
| **Rotation** | ✅ | Medium | Medium | Comprehensive coverage |
| **After Discovery** | ✅ | High | Medium-High | Dynamic assessment |

**Current Recommendation:** Keep simulation manual for now, add scheduling later if monitoring needs arise.

---

**Last Updated:** 2025-11-30  
**Status:** Discovery automated, Simulation manual

