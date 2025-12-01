# Final Presentation Outline: Vendor Risk Digital Twin
**Duration:** 24 minutes  
**Format:** Case Study + Simulation/Demo  
**Target Audience:** Academic/Industry (Cloud Computing Course)

---

## Slide Structure (24 minutes total)

### **SLIDE 1: Title Slide** (30 seconds)
**Content:**
- Title: "Vendor Risk Digital Twin: A Cloud-Native Framework for Predicting Third-Party Failure Impact"
- Authors: Mahendra Shahi, Jalil Rezek, Clifford Odhiambo
- Institution: Johns Hopkins University
- Course: Cloud Computing
- Date: November 2025

**Image Placeholder:**
- [IMAGE: Project logo or Neo4j graph visualization]

---

### **SLIDE 2: The Problem We're Solving** (2 minutes)
**Content:**
- **Headline:** "When a vendor fails, the impact cascades—but current tools can't predict it"

**Key Points:**
1. **The Reality:**
   - Cloud-native orgs depend on 30-50 third-party vendors
   - Vendor failures cost $500K-$2M per incident
   - Impact cascades: Operations → Finance → Compliance

2. **Current Tools Are Reactive:**
   - Static questionnaires (annual/biannual)
   - External ratings that don't understand your infrastructure
   - **No simulation capability** ("What if vendor X fails?")
   - **No cloud integration** (can't map vendor → cloud resource → business process)

**Quote from Interview (Linda):**
> "The hardest part is gathering the evidence and identifying who's going to provide that evidence... It does get very frustrating when you're trying to complete your task, but you're dependent on somebody else or another team."

**Quote from Interview (JZ):**
> "Anytime we're bringing anything into our ecosystem... we thoroughly test it in a sandbox. Almost a digital twin of the real world environment... just to make sure nothing sneaky is going to happen and nothing bad happens, you know, like the CrowdStrike thing."

**Image Placeholder:**
- [IMAGE: Diagram showing vendor failure cascading to multiple services/business processes]
- [IMAGE: Screenshot of traditional GRC tool interface (static)]

---

### **SLIDE 3: Regulatory Drivers: DORA & NIS2** (1.5 minutes)
**Content:**
- **Headline:** "It's not just technical—it's regulatory"

**Key Points:**
1. **DORA (Digital Operational Resilience Act) - Effective January 2025:**
   - **Article 25:** Mandates "digital operational resilience testing"
   - **Article 28:** Requires "Register of Information" for all third-party providers
   - **Shift:** From "Compliance" to "Demonstrable Resilience"

2. **NIS2 Directive:**
   - Requires operational resilience through testing
   - Incident response capabilities validation

**Quote from Interview (JZ):**
> "Yeah, that's great... What you're proposing is similar to what I'm proposing: make a digital twin of the real world system... and you mess with it."

**Image Placeholder:**
- [IMAGE: DORA compliance requirements checklist]
- [IMAGE: Timeline showing regulatory deadlines]

---

### **SLIDE 4: Market Gap Analysis** (1.5 minutes)
**Content:**
- **Headline:** "No single vendor offers what we built"

**Competitive Landscape:**
- **GRC Platforms (Archer, MetricStream):** Manual data entry, no simulation
- **Security Ratings (BitSight, SecurityScorecard):** External ratings, no infrastructure mapping
- **Risk Quantification (Safe Security):** Financial-only, no operational simulation

**Our Differentiation:**
✅ Automated cloud-native discovery  
✅ Real-time failure simulation  
✅ Multi-dimensional impact (operational, financial, compliance)  
✅ Cloud infrastructure integration  

**Quote from Interview (Anurag):**
> "They're framing it as more dynamic and predictive instead of just compliance checks... this goes way beyond that. I think right now most companies are still trying to implement basic automation."

**Image Placeholder:**
- [IMAGE: Competitive comparison matrix/table]
- [IMAGE: Feature comparison chart]

---

### **SLIDE 5: Our Solution: Vendor Risk Digital Twin** (2 minutes)
**Content:**
- **Headline:** "Simulate vendor failures before they happen"

**Core Capabilities:**
1. **Automated Discovery:** GCP API integration → Auto-detect vendor dependencies
2. **Graph Modeling:** Neo4j → Map vendor → service → business process → compliance
3. **Failure Simulation:** "What if Stripe fails for 4 hours?" → Multi-dimensional impact
4. **Impact Prediction:** Operational, Financial, Compliance scores

**Quote from Interview (JZ):**
> "What you're suggesting is called Industry 5.0... an AI‑driven model and simulation... This is a very important project you guys are working on, very interesting to the community."

**Quote from Interview (Azmath):**
> "Current GRC tools are not perfect"

**Image Placeholder:**
- [IMAGE: High-level architecture diagram (4-layer design)]
- [IMAGE: Solution workflow: Discovery → Graph → Simulation → Impact]

---

### **SLIDE 6: System Architecture** (2 minutes)
**Content:**
- **Headline:** "Cloud-native, event-driven architecture"

**Four-Layer Architecture:**
1. **Presentation Layer:** Dashboard, Neo4j Browser, CLI
2. **Application Layer:** Discovery, Graph Loader, Simulation Engine
3. **Data Layer:** Neo4j Graph DB, Cloud Storage, BigQuery
4. **External Systems:** GCP APIs, Compliance Frameworks

**GCP Integration Highlights:**
- ✅ Cloud Functions (Gen2) - Discovery & Loaders
- ✅ Cloud Run - Simulation Service
- ✅ Pub/Sub - Event-driven automation
- ✅ BigQuery - Analytics & historical tracking
- ✅ Secret Manager - Secure credential management
- ✅ Cloud Scheduler - Automated daily discovery
- ✅ Cloud Monitoring - Observability

**Image Placeholder:**
- [IMAGE: Detailed architecture diagram with all GCP components]
- [IMAGE: Data flow diagram showing event-driven flow]

---

### **SLIDE 7: Graph Data Model** (1.5 minutes)
**Content:**
- **Headline:** "Modeling complex dependencies as a graph"

**Node Types:**
- **Vendor:** Stripe, Auth0, SendGrid, etc.
- **Service:** Cloud Functions, Cloud Run services
- **BusinessProcess:** checkout, user_login, password_reset
- **ComplianceControl:** SOC 2, NIST CSF, ISO 27001 controls

**Relationship Types:**
- **DEPENDS_ON:** Service → Vendor
- **SUPPORTS:** Service → BusinessProcess
- **SATISFIES:** Vendor → ComplianceControl

**Example:**
```
(payment-api:Service) → DEPENDS_ON → (Stripe:Vendor)
(payment-api:Service) → SUPPORTS → (checkout:BusinessProcess)
(Stripe:Vendor) → SATISFIES → (CC6.6:ComplianceControl)
```

**Image Placeholder:**
- [IMAGE: Neo4j graph visualization showing vendor dependencies]
- [IMAGE: Close-up of graph relationships with labels]

---

### **SLIDE 8: Automated Discovery Process** (1.5 minutes)
**Content:**
- **Headline:** "From manual spreadsheets to automated discovery"

**Discovery Flow:**
1. **Cloud Scheduler** triggers daily at 2 AM (automated)
2. **Discovery Function** queries GCP APIs:
   - Cloud Functions API
   - Cloud Run API
   - Environment variables analysis
3. **Vendor Detection:** Pattern matching (STRIPE_, AUTH0_, SENDGRID_, etc.)
4. **Results Stored:** Cloud Storage (JSON)
5. **Pub/Sub Event:** Triggers Graph Loader automatically
6. **Neo4j Updated:** Graph database refreshed

**Quote from Interview (Linda):**
> "If those steps could be captured some kind of way, I think that would really help... especially capture audit evidence."

**Image Placeholder:**
- [IMAGE: Discovery flow diagram with GCP components]
- [IMAGE: Screenshot of discovered vendor dependencies in Cloud Storage]

---

### **SLIDE 9: Simulation Methodology** (2 minutes)
**Content:**
- **Headline:** "Multi-dimensional impact calculation"

**Simulation Process:**
1. **Input:** Vendor name + Failure duration (1, 2, 4, 8, 24, 72 hours)
2. **Graph Traversal:** Find all affected services and business processes
3. **Impact Calculation:**
   - **Operational:** Services affected, customers impacted
   - **Financial:** Revenue loss, transaction failures
   - **Compliance:** Score degradation across SOC 2, NIST, ISO 27001

**Impact Weights:**
- Operational: 40%
- Financial: 35%
- Compliance: 25%

**Quote from Interview (JZ):**
> "Being able to do what you're suggesting—simulate, 'Okay, I'm going to do this thing or this service breaks'... in a real world only, that's risky... So being able to test that out in a digital twin is huge."

**Image Placeholder:**
- [IMAGE: Simulation calculation flow diagram]
- [IMAGE: Impact score breakdown visualization]

---

### **SLIDE 10: LIVE DEMO - Discovery & Graph Visualization** (3 minutes)
**Content:**
- **Headline:** "Let's see it in action"

**Demo Flow:**
1. **Show Dashboard:** "Refresh Vendor Inventory" button
2. **Trigger Discovery:** Click button → Show Cloud Scheduler (if time permits)
3. **Show Neo4j Browser:** 
   - Display graph with vendors, services, relationships
   - Zoom into Stripe dependencies
   - Show business process connections
4. **Explain:** "This is our digital twin—a live model of your vendor dependencies"

**Talking Points:**
- "Notice how Stripe connects to multiple services"
- "Each service supports different business processes"
- "Compliance controls are mapped to vendors"

**Image Placeholder:**
- [IMAGE: Screenshot of dashboard with "Refresh Vendor Inventory" button]
- [IMAGE: Neo4j Browser showing full graph (40 nodes, 40 relationships)]
- [IMAGE: Zoomed view of Stripe vendor node with connections]

---

### **SLIDE 11: LIVE DEMO - Simulation Execution** (3 minutes)
**Content:**
- **Headline:** "Simulate a vendor failure"

**Demo Flow:**
1. **Select Vendor:** "Let's simulate Stripe failing for 4 hours"
2. **Run Simulation:** Click "Run Simulation" button
3. **Show Results:**
   - **Operational Impact:** 2 services affected, 50,000 customers impacted
   - **Financial Impact:** $550,000 revenue loss
   - **Compliance Impact:** 
     - SOC 2: 90% → 70% (-20%)
     - NIST CSF: 88% → 68% (-20%)
     - ISO 27001: 85% → 62% (-23%)
4. **Show Recommendations:** Actionable mitigation steps

**Talking Points:**
- "In under 2 seconds, we calculated multi-dimensional impact"
- "Notice how compliance scores degrade across all frameworks"
- "This is the kind of insight you can't get from static questionnaires"

**Quote from Interview (JZ) - Business Decision Scenarios:**
> "Do we lose more money in a three‑day outage than it would cost for two years of having two clouds doing the exact same thing? They can actually do a real cost‑benefit analysis and see the impact."

> "AWS broke... Is it worth the money to go multi‑cloud...? Your system can actually help simulate that."

> "This system can really help in a supply chain type of attack where the company might not be attacked itself, but a third party further down the chain gets attacked and now you have the ripple effect."

**Image Placeholder:**
- [IMAGE: Simulation input form (vendor selection, duration)]
- [IMAGE: Simulation results dashboard with impact scores]
- [IMAGE: Compliance score degradation chart]
- [IMAGE: Recommendations list]

---

### **SLIDE 12: Results & Validation** (2 minutes)
**Content:**
- **Headline:** "Proof-of-concept validation"

**PoC Results:**
- **Graph Model:** 40 nodes, 40 relationships (initial PoC)
- **Simulation Performance:** <2 seconds
- **Discovery:** Automated GCP resource scanning
- **Impact Prediction:** Multi-dimensional scoring validated

**GCP Integration Results:**
- **7 Phases Complete:** Secret Manager → Cloud Functions → Cloud Run → BigQuery → Pub/Sub → Cloud Scheduler → Monitoring
- **Production-Ready:** Event-driven, serverless, auto-scaling
- **Automation:** Zero manual steps in discovery → Neo4j flow

**Quote from Interview (JZ) - Academic Validation:**
> "I did my proposal defense yesterday and the four PhDs on the line were like, wow, we really need this. We got to write some papers."

**Image Placeholder:**
- [IMAGE: Performance metrics dashboard]
- [IMAGE: GCP integration phases completion chart]
- [IMAGE: Before/after comparison (manual vs automated)]

---

### **SLIDE 13: Integration with Existing GRC Tools** (2 minutes)
**Content:**
- **Headline:** "We augment, not replace"

**Integration Strategy:**
- **Not a standalone product:** Designed to integrate with existing GRC platforms
- **Target Platforms:** ServiceNow, Archer, MetricStream, Vanta, Drata
- **Integration Method:** API-based, build on top of existing workflows

**Quote from Interview (JZ):**
> "It's a great idea. You'd have to prove it, though. So you'd have to have several use cases... and be able to give a custom example to a client... 'Here's how our product would integrate all those things.'"

**Quote from Interview (JZ) - GRC Dashboard Vision:**
> "Wouldn't it be great if Google had a dashboard that had all of the NIST controls and you just have it spit out a screenshot or a table... proving that you're meeting that requirement across the board? That would really make GRC much, much easier."

**Quote from Interview (Linda):**
> "If those controls could be implemented as well along with that with that capture that would really help because then you would automatically know oh, this automatically goes here."

**Benefits:**
- Leverage existing GRC investments
- Add predictive capabilities to current tools
- Seamless workflow integration

**Image Placeholder:**
- [IMAGE: Integration architecture showing our tool + existing GRC platforms]
- [IMAGE: API integration diagram]
- [IMAGE: Example: ServiceNow integration mockup]

---

### **SLIDE 14: Key Insights from Industry Interviews** (1.5 minutes)
**Content:**
- **Headline:** "Validated by industry experts"

**Insights from Linda (GRC Professional, 17+ years):**
- Evidence gathering is the most time-consuming task
- Coordination between teams is a major challenge
- Automation of evidence capture would be highly valuable
- "If those steps could be captured some kind of way, I think that would really help"

**Insights from JZ (Cybersecurity Expert, 20+ years):**
- Digital twin concept aligns with Industry 5.0
- Simulation before real-world deployment is critical
- "This is a very important project... very interesting to the community"
- "Being able to test that out in a digital twin is huge"
- Trust at machine speed: "Use it as a decision aid, but not as a decision tool... It can speed up your observe–orient–decide–act loop, but the human makes the decision"
- Fidelity matters: "One of the risks is when you abstract to a digital twin, you can get bare functionality, but not necessarily all functionality... you have to be really, really precise"

**Insights from Anurag (Industry Professional):**
- "They're framing it as more dynamic and predictive instead of just compliance checks"
- "It definitely feels like where things are headed slowly but surely"

**Image Placeholder:**
- [IMAGE: Interview quotes collage]
- [IMAGE: Key insights summary infographic]

---

### **SLIDE 15: Technical Achievements** (1.5 minutes)
**Content:**
- **Headline:** "Production-grade cloud-native implementation"

**GCP Services Integrated:**
- ✅ Cloud Functions (Gen2) - Serverless discovery & loaders
- ✅ Cloud Run - Containerized simulation service
- ✅ Pub/Sub - Event-driven automation
- ✅ BigQuery - Analytics & historical tracking
- ✅ Secret Manager - Secure credential management
- ✅ Cloud Storage - Discovery results storage
- ✅ Cloud Scheduler - Automated daily discovery
- ✅ Cloud Monitoring - Observability & dashboards
- ✅ Eventarc - Event routing

**Architecture Highlights:**
- Fully serverless (auto-scaling, pay-per-use)
- Event-driven (zero manual steps)
- Production-ready (monitoring, logging, error handling)
- Secure (Secret Manager, IAM best practices)

**Image Placeholder:**
- [IMAGE: GCP services architecture diagram]
- [IMAGE: Cloud Monitoring dashboard screenshot]

---

### **SLIDE 16: Future Work & Roadmap** (1.5 minutes)
**Content:**
- **Headline:** "What's next?"

**Immediate Next Steps:**
- Phase 8: CI/CD Pipeline (Cloud Build)
- Phase 9: Advanced Features (VPC, Firestore, cost optimization)

**Long-term Vision:**
- Multi-cloud support (AWS, Azure)
- Machine Learning integration (Vertex AI for predictive analytics)
- Enterprise GRC platform integrations (Archer, MetricStream APIs)
- Real-time vendor health monitoring
- Automated compliance evidence capture

**Quote from Interview (JZ) - Future Research:**
> "If you make progress here, write some academic papers, get it out there, that's going to really help you with jobs and grad school."

**Image Placeholder:**
- [IMAGE: Roadmap timeline]
- [IMAGE: Future features visualization]

---

### **SLIDE 17: Conclusion** (1.5 minutes)
**Content:**
- **Headline:** "From reactive to predictive vendor risk management"

**Key Takeaways:**
1. **Problem:** Current TPRM tools are reactive, can't predict vendor failure impact
2. **Solution:** Vendor Risk Digital Twin—automated discovery + simulation + impact prediction
3. **Validation:** PoC demonstrates technical feasibility (<2 sec simulation)
4. **Production:** GCP integration makes it cloud-native and scalable
5. **Impact:** Addresses GRC 7.0 transition and DORA/NIS2 regulatory requirements

**Quote from Interview (Linda):**
> "I see it could be. It's a possibility... everything that happened from that time to this time. It's possible."

**Quote from Interview (JZ):**
> "This is a very important project you guys are working on, very interesting to the community."

**Call to Action:**
- Open-source framework for research and development
- Integration-ready for enterprise GRC platforms
- Addresses critical industry gap

**Image Placeholder:**
- [IMAGE: Summary infographic]
- [IMAGE: Project logo with tagline]

---

### **SLIDE 18: Q&A** (Remaining time)
**Content:**
- **Headline:** "Questions?"

**Prepared Talking Points:**
- Technical architecture details
- Integration possibilities
- Regulatory compliance (DORA, NIS2)
- Industry validation from interviews
- Future roadmap

**Contact Information:**
- GitHub Repository
- Project Documentation
- Team Contact Info

**Image Placeholder:**
- [IMAGE: Contact information slide]

---

## Presentation Timing Breakdown

| Slide | Topic | Duration |
|-------|-------|----------|
| 1 | Title | 0:30 |
| 2 | Problem Statement | 2:00 |
| 3 | Regulatory Drivers | 1:30 |
| 4 | Market Gap | 1:30 |
| 5 | Solution Overview | 2:00 |
| 6 | Architecture | 2:00 |
| 7 | Graph Model | 1:30 |
| 8 | Discovery Process | 1:30 |
| 9 | Simulation Methodology | 2:00 |
| 10 | **DEMO: Discovery** | **3:00** |
| 11 | **DEMO: Simulation** | **3:00** |
| 12 | Results | 2:00 |
| 13 | Integration | 2:00 |
| 14 | Industry Insights | 1:30 |
| 15 | Technical Achievements | 1:30 |
| 16 | Future Work | 1:30 |
| 17 | Conclusion | 1:30 |
| 18 | Q&A | Remaining |

**Total:** ~24 minutes (with buffer for Q&A)

---

## Key Quotes to Use Throughout Presentation

### From Linda (GRC Professional):
- "The hardest part is gathering the evidence and identifying who's going to provide that evidence"
- "If those steps could be captured some kind of way, I think that would really help"
- "I see it could be. It's a possibility"

### From JZ (Cybersecurity Expert):
- "Anytime we're bringing anything into our ecosystem... we thoroughly test it in a sandbox. Almost a digital twin of the real world environment"
- "What you're proposing is similar to what I'm proposing: make a digital twin of the real world system... and you mess with it"
- "What you're suggesting is called Industry 5.0... an AI‑driven model and simulation"
- "This is a very important project you guys are working on, very interesting to the community"
- "Being able to test that out in a digital twin is huge"
- "Wouldn't it be great if Google had a dashboard that had all of the NIST controls and you just have it spit out a screenshot or a table... proving that you're meeting that requirement across the board? That would really make GRC much, much easier"
- "Use it as a decision aid, but not as a decision tool... It can speed up your observe–orient–decide–act loop, but the human makes the decision"

### From Anurag (Industry Professional):
- "They're framing it as more dynamic and predictive instead of just compliance checks"
- "It definitely feels like where things are headed slowly but surely"

### From Azmath:
- "Current GRC tools are not perfect"

---

## Image Requirements Checklist

### Architecture & Technical:
- [ ] System architecture diagram (4-layer design)
- [ ] GCP integration architecture diagram
- [ ] Data flow diagram (Discovery → Pub/Sub → Neo4j)
- [ ] Event-driven flow diagram
- [ ] Graph data model visualization

### Demo Screenshots:
- [ ] Dashboard with "Refresh Vendor Inventory" button
- [ ] Neo4j Browser - Full graph view (40 nodes, 40 relationships)
- [ ] Neo4j Browser - Stripe vendor zoomed view
- [ ] Simulation input form
- [ ] Simulation results dashboard
- [ ] Compliance score degradation chart
- [ ] Recommendations list

### Results & Metrics:
- [ ] Performance metrics dashboard
- [ ] GCP integration phases completion chart
- [ ] Before/after comparison (manual vs automated)
- [ ] Cloud Monitoring dashboard screenshot

### Market & Problem:
- [ ] Vendor failure cascade diagram
- [ ] Traditional GRC tool interface (static)
- [ ] Competitive comparison matrix
- [ ] DORA compliance requirements checklist

### Integration:
- [ ] Integration architecture (our tool + existing GRC platforms)
- [ ] API integration diagram
- [ ] ServiceNow integration mockup (example)

### Other:
- [ ] Project logo
- [ ] Interview quotes collage
- [ ] Key insights summary infographic
- [ ] Roadmap timeline
- [ ] Summary infographic

---

## Presentation Tips

1. **Demo Timing:** Allocate 6 minutes total for demos (3 min each). Practice transitions.
2. **Quote Integration:** Weave quotes naturally into narrative, don't just read them.
3. **Visual Storytelling:** Use images to support points, not just text.
4. **Technical Depth:** Balance technical details with high-level concepts.
5. **Regulatory Context:** Emphasize DORA/NIS2 as key drivers.
6. **Industry Validation:** Highlight that experts validated the approach.
7. **Future Vision:** End on optimistic note about Industry 5.0 and GRC 7.0.

---

**Last Updated:** 2025-11-30  
**Status:** Ready for slide creation

