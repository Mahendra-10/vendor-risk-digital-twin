# Final Presentation Outline 2: Vendor Risk Digital Twin
**Optimized Structure Based on Perplexity Recommendations**  
**Duration:** ~18 slides, 20-24 minutes  
**Format:** Story-driven + Demo  
**Target Audience:** Academic/Industry (Cloud Computing Course)

---

## Comparison with Original Outline

### Key Differences:
- **More focused:** 18 slides vs 18 slides (same count, but restructured)
- **Story-first approach:** Opens with vivid outage story
- **Condensed technical details:** Architecture and graph model on single slides
- **CI/CD integration:** Added automated deployment pipeline details
- **Streamlined demos:** 2 focused demos (3 min each)
- **Better flow:** Problem → Solution → Demo → Validation → Future

### What's Enhanced:
- ✅ CI/CD pipeline integration in Technical Achievements
- ✅ Automated deployment mentioned in Discovery Flow
- ✅ Production-ready DevOps practices highlighted
- ✅ Event-driven architecture with CI/CD automation

---

## Slide Structure (18 slides)

### **SLIDE 1: Title & One-Sentence Hook** (30 seconds)
**Content:**
- **Title:** "Vendor Risk Digital Twin: A Cloud-Native Framework for Predicting Third-Party Failure Impact"
- **Authors:** Mahendra Shahi, Jalil Rezek, Clifford Odhiambo
- **Institution:** Johns Hopkins University | Cloud Computing Course
- **Date:** November 2025

**One line under title:**
> **"Simulate vendor failures before they break your cloud."**

**Image Placeholder:**
- [IMAGE: Project logo with tagline]

---

### **SLIDE 2: Story: When Stripe (or CrowdStrike) Breaks** (2 minutes)
**Content:**
- **Headline:** "A real outage story"

**Very short narrative:**
- "June 2024: Stripe API outage affects payment processing"
- "Cascading impact: Checkout fails → Revenue loss → Customer complaints → Compliance gaps"
- "Question: Could you have predicted this before it happened?"

**Simple cascade diagram:**
```
Stripe Outage
    ↓
Payment Service Down
    ↓
Checkout Process Fails
    ↓
Revenue Loss + Compliance Degradation
```

**End with question:**
> **"Could you have predicted this before it happened?"**

**Image Placeholder:**
- [IMAGE: Outage cascade diagram]
- [IMAGE: Real outage timeline (Stripe/CrowdStrike)]

---

### **SLIDE 3: Problem: Vendor Failure Blindness** (1.5 minutes)
**Content:**
- **Headline:** "The problem: We're flying blind"

**3 bullets only:**
1. **30–50 SaaS vendors per organization**
   - Cloud-native companies depend on dozens of third-party services
   - Each vendor is a potential point of failure

2. **$500K–$2M per major incident**
   - Revenue loss, customer churn, compliance penalties
   - Average recovery time: 4-8 hours

3. **Nobody can answer: "What exactly breaks if Vendor X fails for 4 hours?"**
   - No simulation capability
   - No real-time impact prediction
   - Static questionnaires don't help during incidents

**Image Placeholder:**
- [IMAGE: Vendor dependency complexity diagram]
- [IMAGE: Cost of downtime statistics]

---

### **SLIDE 4: Why Current Tools Fail** (1.5 minutes)
**Content:**
- **Headline:** "Existing solutions are reactive, not predictive"

**3 columns comparison:**

| Questionnaires | Ratings | GRC Platforms |
|---------------|---------|---------------|
| • Annual/biannual updates | • External scores only | • Manual data entry |
| • Static snapshots | • No infrastructure mapping | • No simulation |
| • Can't simulate failures | • Don't understand your stack | • Reactive compliance |

**Key point:**
- None can answer: **"What if Vendor X fails?"**

**Image Placeholder:**
- [IMAGE: 3-column comparison table]
- [IMAGE: Traditional GRC tool screenshot (static)]

---

### **SLIDE 5: Regulatory Pressure (DORA & NIS2)** (1.5 minutes)
**Content:**
- **Headline:** "Regulators now demand resilience, not just checklists"

**One headline:**
> **"DORA & NIS2: Testing and resilience are now mandatory"**

**3 bullets:**
1. **DORA (Effective January 2025):**
   - **Article 25:** Mandates "digital operational resilience testing"
   - **Article 28:** Requires "Register of Information" for all third-party providers
   - **Shift:** From compliance to demonstrable resilience

2. **NIS2 Directive:**
   - Operational resilience through testing
   - Incident response capabilities validation
   - Supply chain risk management

3. **Gap: No way to run realistic, vendor-specific simulations**
   - Current tools: Checklists and questionnaires
   - Need: Automated testing and impact prediction

**Image Placeholder:**
- [IMAGE: DORA/NIS2 compliance requirements]
- [IMAGE: Regulatory timeline]

---

### **SLIDE 6: One Big Idea: Vendor Risk Digital Twin** (2 minutes)
**Content:**
- **Headline:** "Our solution: A graph-based digital twin"

**Single, clean visual with 1-liner:**
> **"A graph-based digital twin of your vendors, services, business processes, and controls."**

**3 bullets:**
1. **Auto-discover vendor dependencies from cloud**
   - GCP API integration
   - Pattern-based detection
   - Zero manual spreadsheets

2. **Simulate failures**
   - "What if Stripe fails for 4 hours?"
   - Real-time graph traversal
   - Multi-dimensional impact

3. **Quantify operational, financial, and compliance impact**
   - Services affected, customers impacted
   - Revenue loss calculation
   - Compliance score degradation (SOC 2, NIST, ISO)

**Quote from Interview (JZ):**
> "What you're suggesting is called Industry 5.0... an AI‑driven model and simulation... This is a very important project you guys are working on."

**Image Placeholder:**
- [IMAGE: Digital twin concept diagram]
- [IMAGE: Solution workflow: Discovery → Graph → Simulation]

---

### **SLIDE 7: Architecture on One Slide** (1.5 minutes)
**Content:**
- **Headline:** "Cloud-native, event-driven architecture"

**4-layer diagram (simple):**

```
┌─────────────────────────────────────┐
│  Presentation Layer                 │
│  (Dashboard, Neo4j Browser)         │
├─────────────────────────────────────┤
│  Application Layer                  │
│  (Discovery, Simulation, Loaders)   │
├─────────────────────────────────────┤
│  Data Layer                         │
│  (Neo4j, Cloud Storage, BigQuery)   │
├─────────────────────────────────────┤
│  External Systems                   │
│  (GCP APIs, Compliance Frameworks)   │
└─────────────────────────────────────┘
```

**Only 1 bullet per layer:**
- **Presentation:** Interactive dashboard and graph visualization
- **Application:** Serverless functions (Cloud Functions, Cloud Run)
- **Data:** Graph database + cloud storage + analytics
- **External:** GCP APIs + compliance framework mappings

**CI/CD Integration Note:**
- All services deployed via automated Cloud Build pipeline
- Event-driven: Code push → Auto-build → Auto-deploy

**Image Placeholder:**
- [IMAGE: 4-layer architecture diagram]
- [IMAGE: GCP services integration overview]

---

### **SLIDE 8: Graph Model on One Slide** (1.5 minutes)
**Content:**
- **Headline:** "Modeling complex dependencies as a graph"

**Neo4j screenshot style visual:**

**4 node types + 3 relationship types:**

**Node Types:**
- **Vendor:** Stripe, Auth0, SendGrid
- **Service:** Cloud Functions, Cloud Run services
- **BusinessProcess:** checkout, user_login
- **ComplianceControl:** SOC 2, NIST, ISO controls

**Relationship Types:**
- **DEPENDS_ON:** Service → Vendor
- **SUPPORTS:** Service → BusinessProcess
- **SATISFIES:** Vendor → ComplianceControl

**One example path:**
```
(payment-api:Service) 
  → DEPENDS_ON → (Stripe:Vendor)
  → SUPPORTS → (checkout:BusinessProcess)
  → SATISFIES → (CC6.6:SOC2_Control)
```

**Image Placeholder:**
- [IMAGE: Neo4j graph visualization]
- [IMAGE: Close-up of example path]

---

### **SLIDE 9: Discovery Flow (Condensed)** (1.5 minutes)
**Content:**
- **Headline:** "From manual spreadsheets to automated discovery"

**Small flow diagram:**
```
Cloud Scheduler (Daily 2 AM)
    ↓
Discovery Function
    ↓
Cloud Storage (JSON Results)
    ↓
Pub/Sub Event
    ↓
Graph Loader Function
    ↓
Neo4j Graph (Updated)
```

**3 bullets:**
1. **Automatic daily scan**
   - Cloud Scheduler triggers discovery
   - Queries GCP APIs (Cloud Functions, Cloud Run)
   - Pattern-based vendor detection (STRIPE_, AUTH0_, etc.)

2. **Pattern-based vendor detection**
   - Environment variable analysis
   - Vendor signature matching
   - Dependency extraction

3. **Graph refreshed without manual spreadsheets**
   - Pub/Sub triggers automatic graph loading
   - Zero manual intervention
   - Always up-to-date digital twin

**CI/CD Integration:**
- Discovery and loader functions deployed via Cloud Build
- Automated testing before deployment
- Production-ready with monitoring and error handling

**Image Placeholder:**
- [IMAGE: Discovery flow diagram]
- [IMAGE: Cloud Scheduler + Pub/Sub flow]

---

### **SLIDE 10: Simulation Logic (Condensed)** (1.5 minutes)
**Content:**
- **Headline:** "Multi-dimensional impact calculation"

**Simple "Input → Graph Traverse → Scores" diagram:**
```
Input: Vendor + Duration
    ↓
Graph Traversal
    ↓
Find Affected Services & Processes
    ↓
Calculate Impact Scores
    ↓
Output: Operational / Financial / Compliance Deltas
```

**3 bullets:**
1. **Input: vendor + duration**
   - Select vendor (e.g., Stripe)
   - Choose failure duration (1, 2, 4, 8, 24, 72 hours)

2. **Traverse: find affected services + processes**
   - Graph traversal from vendor node
   - Identify all dependent services
   - Map to business processes

3. **Output: operational / financial / compliance deltas**
   - **Operational:** Services affected, customers impacted
   - **Financial:** Revenue loss calculation
   - **Compliance:** Score degradation (SOC 2, NIST, ISO)

**Performance:**
- Sub-2-second simulation time
- Real-time impact prediction

**Image Placeholder:**
- [IMAGE: Simulation flow diagram]
- [IMAGE: Impact calculation breakdown]

---

### **SLIDE 11: DEMO 1: Discovery & Graph (3 minutes)**
**Content:**
- **Headline:** "Let's see it in action: The digital twin"

**Only 2–3 clear actions:**

1. **Click "Refresh Vendor Inventory"**
   - Show dashboard button
   - Trigger discovery process
   - Show Cloud Scheduler (if time permits)

2. **Show graph; zoom on Stripe**
   - Display Neo4j Browser
   - Full graph view (40 nodes, 40 relationships)
   - Zoom into Stripe vendor node
   - Show connections: services → business processes → compliance controls

3. **Say explicitly: "This is the digital twin."**
   - "This is a live model of your vendor dependencies"
   - "Notice how Stripe connects to multiple services"
   - "Each service supports different business processes"
   - "Compliance controls are mapped to vendors"

**Talking Points:**
- "Automated discovery means this graph is always current"
- "No manual spreadsheets needed"
- "This is what a digital twin looks like"

**Image Placeholder:**
- [IMAGE: Dashboard with "Refresh Vendor Inventory" button]
- [IMAGE: Neo4j Browser - Full graph view]
- [IMAGE: Stripe vendor zoomed view]

---

### **SLIDE 12: DEMO 2: Simulation (3 minutes)**
**Content:**
- **Headline:** "Simulate a vendor failure"

**Run: "Stripe fails for 4 hours."**

**Show:**
1. **X services, Y customers**
   - "2 services affected"
   - "50,000 customers impacted"

2. **$Z loss**
   - "$550,000 revenue loss"
   - "Based on transaction volume and duration"

3. **SOC 2 / NIST / ISO drops**
   - SOC 2: 90% → 70% (-20%)
   - NIST CSF: 88% → 68% (-20%)
   - ISO 27001: 85% → 62% (-23%)

4. **Recommendations**
   - Actionable mitigation steps
   - Vendor redundancy suggestions

**One quote from JZ to anchor in expert validation:**
> "Being able to do what you're suggesting—simulate, 'Okay, I'm going to do this thing or this service breaks'... in a real world only, that's risky... So being able to test that out in a digital twin is huge."

**Talking Points:**
- "In under 2 seconds, we calculated multi-dimensional impact"
- "Notice how compliance scores degrade across all frameworks"
- "This is the kind of insight you can't get from static questionnaires"

**Image Placeholder:**
- [IMAGE: Simulation input form]
- [IMAGE: Simulation results dashboard]
- [IMAGE: Compliance score degradation chart]

---

### **SLIDE 13: Results & Validation** (2 minutes)
**Content:**
- **Headline:** "Proof-of-concept validation"

**3 bullets:**
1. **PoC scale (nodes, latency)**
   - Graph model: 40 nodes, 40 relationships
   - Simulation performance: <2 seconds
   - Discovery: Automated GCP resource scanning

2. **Full GCP automation chain**
   - **8 Phases Complete:** Secret Manager → Cloud Functions → Cloud Run → BigQuery → Pub/Sub → Cloud Scheduler → Monitoring → **CI/CD Pipeline**
   - Production-ready: Event-driven, serverless, auto-scaling
   - **CI/CD:** Automated build, test, and deployment pipeline
   - Zero manual steps in discovery → Neo4j flow

3. **Expert feedback highlights (Linda + JZ)**
   - **JZ:** "This is a very important project... very interesting to the community"
   - **JZ:** "I did my proposal defense yesterday and the four PhDs on the line were like, wow, we really need this. We got to write some papers."
   - **Linda:** "If those steps could be captured some kind of way, I think that would really help"

**Image Placeholder:**
- [IMAGE: Performance metrics dashboard]
- [IMAGE: GCP integration phases completion chart]
- [IMAGE: Expert feedback quotes]

---

### **SLIDE 14: Where It Fits in GRC Stack** (1.5 minutes)
**Content:**
- **Headline:** "We augment, not replace"

**Diagram: Your Twin in the middle; arrows to ServiceNow / Archer / Vanta**

```
┌──────────┐      ┌──────────────┐      ┌──────────┐
│ServiceNow│ ←──→ │ Vendor Risk  │ ←──→ │  Archer  │
│          │      │ Digital Twin │      │          │
└──────────┘      └──────────────┘      └──────────┘
                          ↕
                   ┌──────────┐
                   │  Vanta   │
                   └──────────┘
```

**3 bullets:**
1. **Augment, not replace**
   - Leverage existing GRC investments
   - Add predictive capabilities to current tools
   - API-based integration

2. **Feeds evidence**
   - Automated evidence capture
   - Real-time compliance status
   - Audit trail generation

3. **Gives predictive analytics**
   - "What if" scenarios
   - Impact prediction
   - Risk quantification

**Quote from Interview (JZ):**
> "It's a great idea. You'd have to prove it, though. So you'd have to have several use cases... and be able to give a custom example to a client... 'Here's how our product would integrate all those things.'"

**Image Placeholder:**
- [IMAGE: Integration architecture diagram]
- [IMAGE: API integration flow]

---

### **SLIDE 15: Technical Achievements (Very Focused)** (1.5 minutes)
**Content:**
- **Headline:** "Production-grade cloud-native implementation"

**4–5 bullets max:**
1. **Fully serverless & event-driven**
   - Cloud Functions (Gen2), Cloud Run
   - Auto-scaling, pay-per-use
   - Pub/Sub event routing

2. **Automated discovery → graph with zero manual steps**
   - Cloud Scheduler → Discovery → Storage → Pub/Sub → Neo4j
   - Pattern-based vendor detection
   - Always up-to-date digital twin

3. **Sub-2-second simulations**
   - Real-time graph traversal
   - Multi-dimensional impact calculation
   - Instant results

4. **Security basics (Secrets, IAM)**
   - Secret Manager for credentials
   - IAM best practices
   - Secure service-to-service communication

5. **CI/CD Pipeline (NEW)**
   - **Automated build and deployment:** Cloud Build pipeline
   - **Automated testing:** Tests run before deployment
   - **Event-driven deployment:** Code push → Auto-build → Auto-deploy
   - **Production-ready DevOps:** Monitoring, logging, error handling
   - **Multi-service automation:** Single pipeline deploys all services (Cloud Run + Cloud Functions)

**GCP Services Integrated:**
- ✅ Cloud Functions (Gen2) - Serverless discovery & loaders
- ✅ Cloud Run - Containerized simulation service
- ✅ Pub/Sub - Event-driven automation
- ✅ BigQuery - Analytics & historical tracking
- ✅ Secret Manager - Secure credential management
- ✅ Cloud Storage - Discovery results storage
- ✅ Cloud Scheduler - Automated daily discovery
- ✅ Cloud Monitoring - Observability & dashboards
- ✅ **Cloud Build - CI/CD pipeline (NEW)**

**Image Placeholder:**
- [IMAGE: GCP services architecture diagram]
- [IMAGE: CI/CD pipeline flow diagram]
- [IMAGE: Cloud Build dashboard screenshot]

---

### **SLIDE 16: Future Work & Research** (1.5 minutes)
**Content:**
- **Headline:** "What's next?"

**Split into:**

**Short-term:**
- ✅ **CI/CD:** Cloud Build pipeline (COMPLETE)
- Multi-cloud support (AWS, Azure)
- Advanced CI/CD: GitHub Actions integration
- Enhanced monitoring and alerting

**Long-term:**
- Machine Learning integration (Vertex AI for predictive analytics)
- Real-time vendor health monitoring
- Full GRC integrations (Archer, MetricStream APIs)
- Automated compliance evidence capture
- Supply chain attack simulation

**Quote from Interview (JZ) - Future Research:**
> "If you make progress here, write some academic papers, get it out there, that's going to really help you with jobs and grad school."

**Image Placeholder:**
- [IMAGE: Roadmap timeline]
- [IMAGE: Future features visualization]

---

### **SLIDE 17: Conclusion: From Reactive to Predictive** (1.5 minutes)
**Content:**
- **Headline:** "From reactive to predictive vendor risk management"

**3 bullets only:**
1. **Problem: No way to predict vendor failure impact**
   - Current tools: Reactive, static, manual
   - Gap: No simulation capability

2. **Contribution: Cloud-native digital twin + simulation**
   - Automated discovery from cloud infrastructure
   - Graph-based modeling
   - Real-time failure simulation
   - Multi-dimensional impact prediction
   - **Production-ready with CI/CD automation**

3. **Impact: Helps meet DORA/NIS2 and GRC 7.0 vision**
   - Regulatory compliance (DORA Article 25, NIS2)
   - Industry 5.0 alignment
   - Predictive risk management
   - Enterprise-ready architecture

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
- CI/CD pipeline implementation
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
| 1 | Title & Hook | 0:30 |
| 2 | Story: Outage | 2:00 |
| 3 | Problem | 1:30 |
| 4 | Why Current Tools Fail | 1:30 |
| 5 | Regulatory Pressure | 1:30 |
| 6 | One Big Idea | 2:00 |
| 7 | Architecture | 1:30 |
| 8 | Graph Model | 1:30 |
| 9 | Discovery Flow | 1:30 |
| 10 | Simulation Logic | 1:30 |
| 11 | **DEMO: Discovery** | **3:00** |
| 12 | **DEMO: Simulation** | **3:00** |
| 13 | Results & Validation | 2:00 |
| 14 | GRC Stack Integration | 1:30 |
| 15 | Technical Achievements | 1:30 |
| 16 | Future Work | 1:30 |
| 17 | Conclusion | 1:30 |
| 18 | Q&A | Remaining |

**Total:** ~24 minutes (with buffer for Q&A)

---

## Key Differences from Original Outline

### Structure Improvements:
1. **Story-first approach:** Opens with vivid outage story (Slide 2)
2. **Condensed technical:** Architecture and graph model on single slides
3. **Better flow:** Problem → Solution → Demo → Validation
4. **CI/CD integration:** Added throughout (Slides 7, 9, 13, 15)

### CI/CD Integration Points:
- **Slide 7 (Architecture):** Mentioned automated deployment
- **Slide 9 (Discovery Flow):** Added CI/CD note about automated deployment
- **Slide 13 (Results):** Highlighted CI/CD as Phase 8 completion
- **Slide 15 (Technical Achievements):** Dedicated bullet on CI/CD pipeline
- **Slide 16 (Future Work):** CI/CD marked as complete

### Content Enhancements:
- More focused on core message
- Better use of quotes (JZ, Linda)
- Clearer demo structure
- Stronger regulatory emphasis
- Production-ready emphasis with CI/CD

---

## Key Quotes to Use Throughout Presentation

### From JZ (Cybersecurity Expert):
- "What you're suggesting is called Industry 5.0... an AI‑driven model and simulation"
- "This is a very important project you guys are working on, very interesting to the community"
- "Being able to test that out in a digital twin is huge"
- "I did my proposal defense yesterday and the four PhDs on the line were like, wow, we really need this. We got to write some papers."

### From Linda (GRC Professional):
- "If those steps could be captured some kind of way, I think that would really help"
- "The hardest part is gathering the evidence and identifying who's going to provide that evidence"

---

## Image Requirements Checklist

### Architecture & Technical:
- [ ] System architecture diagram (4-layer design)
- [ ] GCP integration architecture diagram
- [ ] **CI/CD pipeline flow diagram (NEW)**
- [ ] Data flow diagram (Discovery → Pub/Sub → Neo4j)
- [ ] Graph data model visualization

### Demo Screenshots:
- [ ] Dashboard with "Refresh Vendor Inventory" button
- [ ] Neo4j Browser - Full graph view
- [ ] Neo4j Browser - Stripe vendor zoomed view
- [ ] Simulation input form
- [ ] Simulation results dashboard
- [ ] Compliance score degradation chart

### Results & Metrics:
- [ ] Performance metrics dashboard
- [ ] GCP integration phases completion chart (including CI/CD)
- [ ] **Cloud Build dashboard screenshot (NEW)**
- [ ] Before/after comparison (manual vs automated)

### Market & Problem:
- [ ] Vendor failure cascade diagram
- [ ] Outage story timeline
- [ ] Traditional GRC tool interface (static)
- [ ] Competitive comparison matrix
- [ ] DORA compliance requirements checklist

### Integration:
- [ ] Integration architecture (our tool + existing GRC platforms)
- [ ] API integration diagram

---

## Presentation Tips

1. **Demo Timing:** Allocate 6 minutes total for demos (3 min each). Practice transitions.
2. **Story Opening:** Start with the outage story to hook audience immediately.
3. **CI/CD Emphasis:** Highlight production-ready DevOps practices (Slide 15).
4. **Quote Integration:** Weave quotes naturally into narrative, don't just read them.
5. **Visual Storytelling:** Use images to support points, not just text.
6. **Technical Depth:** Balance technical details with high-level concepts.
7. **Regulatory Context:** Emphasize DORA/NIS2 as key drivers.
8. **Industry Validation:** Highlight that experts validated the approach.
9. **Future Vision:** End on optimistic note about Industry 5.0 and GRC 7.0.

---

**Last Updated:** 2025-12-01  
**Status:** Optimized outline with CI/CD integration  
**Based on:** Perplexity recommendations + Original outline
