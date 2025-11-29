Local 
mahendra@Mahendras-MacBook-Air dashboard %    node server.js
[INFO] Simulator initialized
[INFO] Simulator initialized successfully
[INFO] Starting Vendor Risk Digital Twin Dashboard...
[INFO] Dashboard available at: http://localhost:3000
[INFO] Data loaded at: 2025-11-29T02:50:19.869Z
[INFO] Running simulation locally: Auth0 for 4 hours
[INFO] 🔴 Simulating Auth0 failure for 4 hours...
[INFO] Calculating operational impact for vendor: "Auth0"...
[INFO] Normalized vendor name: "auth0"
[INFO] Found vendor: name="auth0", display_name="Auth0"
[INFO] Query returned 2 service records
[INFO] Calculating financial impact...
[INFO] Calculating compliance impact...
[INFO] Log of Compliance impact: {"affected_frameworks":{"soc2":{"baseline_score":0.92,"new_score":0.77,"score_change":0.15,"affected_controls":["CC6.1"]},"nist":{"baseline_score":0.88,"new_score":0.73,"score_change":0.15,"affected_controls":["PR.AC-1"]},"iso27001":{"baseline_score":0.9,"new_score":0.75,"score_change":0.15,"affected_controls":["A.5.15"]}},"impact_score":0.15,"summary":{"soc2":{"change":"15.0%","new_score":"77.0%"},"nist":{"change":"15.0%","new_score":"73.0%"},"iso27001":{"change":"15.0%","new_score":"75.0%"}}}
[INFO] ✅ Simulation complete. Impact score: 0.40



Cloud run
{
   "compliance_impact":{
      "affected_frameworks":[
         
      ],
      "impact_score":0
   },
   "deployed_at":"simulation-service",
   "duration_hours":4,
   "financial_impact":{
      "customer_impact_cost":500000,
      "failed_transactions":10000,
      "impact_score":0.8,
      "revenue_loss":300000,
      "revenue_loss_formatted":"$300,000.00",
      "total_cost":800000,
      "total_cost_formatted":"$800,000.00"
   },
   "operational_impact":{
      "affected_services":[
         {
            "business_processes":[
               "checkout",
               "refunds",
               "subscription_billing",
               "order_confirmation",
               "password_reset",
               "marketing_emails",
               "system_monitoring",
               "alerting",
               "log_aggregation",
               "sms_notifications",
               "2fa_verification"
            ],
            "customers_affected":50000,
            "name":"checkout-service",
            "rpm":500,
            "type":"cloud_run"
         },
         {
            "business_processes":[
               "user_login",
               "user_registration",
               "password_reset"
            ],
            "customers_affected":100000,
            "name":"auth-service",
            "rpm":300,
            "type":"cloud_run"
         }
      ],
      "business_processes":[
         "2fa_verification",
         "alerting",
         "checkout",
         "log_aggregation",
         "marketing_emails",
         "order_confirmation",
         "password_reset",
         "refunds",
         "sms_notifications",
         "subscription_billing",
         "system_monitoring",
         "user_login",
         "user_registration"
      ],
      "customers_affected":100000,
      "impact_score":0.2,
      "service_count":2,
      "total_rpm":800
   },
   "overall_impact_score":0.36,
   "recommendations":[
      "Implement fallback mechanisms for 2 services depending on auth0",
      "Consider vendor diversification for critical business processes",
      "High financial impact detected ($800,000.00). Implement circuit breakers and graceful degradation"
   ],
   "service":"simulation-service",
   "simulation_id":"auth0-20251129020034",
   "timestamp":"2025-11-29T02:00:34.047213",
   "vendor":"auth0"
}