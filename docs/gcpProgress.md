Reviewing the GCP integration roadmap to outline the initial setup steps:


[1 tool called]


Verifying the project is set correctly, then enabling the required APIs:


[1 tool called]


Project is set to `yeti-consult-463902`. If you want to use `vendor-risk-digital-twin`, switch to it. Enabling the required APIs for the Vendor Risk Digital Twin project:


[1 tool called]


Listing your projects to find the correct one:


[1 tool called]


Setting `vendor-risk-digital-twin` as the active project, then enabling the required APIs:


[2 tools called]


APIs enabled. Creating a service account for the project:


[1 tool called]


Granting necessary permissions to the service account:


[4 tools called]


GCP project setup complete. Summary:

## Setup complete

1. Project set: `vendor-risk-digital-twin`
2. APIs enabled:
   - Cloud Functions
   - Cloud Run
   - BigQuery
   - Secret Manager
   - Cloud Scheduler
   - Pub/Sub
   - Cloud Storage
   - Cloud Logging
   - Cloud Monitoring
3. Service account created: `vendor-risk-sa`
4. Permissions granted:
   - Cloud Functions Developer
   - Cloud Run Developer
   - BigQuery Data Editor
   - Secret Manager Secret Accessor

## Next steps (Phase 1: Secret Management)

According to your roadmap (`docs/gcp_integration_roadmap.md`), the next phase is to migrate secrets to Secret Manager. You can:

1. Store Neo4j credentials in Secret Manager:
   ```bash
   # You'll need your Neo4j password
   echo -n "your-neo4j-password" | gcloud secrets create neo4j-password \
     --data-file=- --replication-policy="automatic"
   ```

2. Update your code to fetch secrets from Secret Manager instead of `.env` files

3. Test the integration

Should I help you:
- Set up Secret Manager for your Neo4j credentials?
- Start implementing the GCP discovery module (`gcp_discovery.py`)?
- Move on to another phase of the roadmap?

Your GCP project is ready for the Vendor Risk Digital Twin integration.