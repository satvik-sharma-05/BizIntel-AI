---
title: RAG Upload UX + Toast Notifications + Competition Analysis
status: requirements
created: 2026-03-26
updated: 2026-03-26
---

# Feature Specification: RAG Upload UX + Toast Notifications + Competition Analysis

## Overview
Enhance the BizIntel AI platform with three major improvements:
1. Visual RAG document upload progress with step-by-step UI
2. Replace all alert() calls with professional toast notifications
3. Implement comprehensive Competition Analysis module with real API data

## Business Goals
- Improve user experience during document uploads with transparent progress tracking
- Modernize UI feedback system with non-blocking toast notifications
- Provide actionable competitive intelligence to help businesses understand their market position

---

## 1. RAG Document Upload Progress UI

### Requirements

#### R1.1 Visual Upload Pipeline
**Priority:** High  
**Description:** Display real-time progress steps when users upload documents for RAG processing

**Acceptance Criteria:**
- [ ] Show 7-step progress indicator during document upload
- [ ] Each step updates in real-time as backend processes the document
- [ ] Steps include: Upload → Extract → Clean → Chunk → Embed → Store → Complete
- [ ] Visual feedback (spinner, checkmark, error icon) for each step
- [ ] Error handling shows which step failed with clear message
- [ ] Progress persists if user navigates away and returns

**Steps to Display:**
1. Uploading document
2. Extracting text
3. Cleaning text
4. Splitting into chunks
5. Generating embeddings
6. Storing in vector database
7. Saving metadata
8. Document ready for AI search

#### R1.2 Document Chunking Configuration
**Priority:** High  
**Description:** Implement proper text chunking with overlap for optimal RAG retrieval

**Acceptance Criteria:**
- [ ] Chunk size: 500 characters
- [ ] Chunk overlap: 50 characters
- [ ] Split strategy: paragraphs → sentences → characters
- [ ] Each chunk stores: chunk_id, document_id, business_id, text, embedding, page_number, chunk_index, source_file
- [ ] Embeddings stored in FAISS
- [ ] Metadata stored in MongoDB

#### R1.3 Backend Progress Events
**Priority:** High  
**Description:** Backend emits progress events during document processing

**Acceptance Criteria:**
- [ ] Backend sends progress updates via WebSocket or polling endpoint
- [ ] Each processing step triggers a progress event
- [ ] Events include: step_name, status (in_progress, completed, failed), timestamp, message
- [ ] Error events include error details and recovery suggestions

---

## 2. Toast Notification System

### Requirements

#### R2.1 Replace All Alerts
**Priority:** High  
**Description:** Remove all alert() and confirm() calls, replace with toast notifications

**Acceptance Criteria:**
- [ ] No alert() or confirm() calls remain in codebase
- [ ] All user feedback uses toast notifications
- [ ] Toast library installed (react-hot-toast or sonner)
- [ ] Toast types: success, error, info, warning, loading
- [ ] Toasts auto-dismiss after appropriate duration
- [ ] Multiple toasts stack properly without overlapping

#### R2.2 Toast Implementation Patterns
**Priority:** High  
**Description:** Standardize toast usage across all user actions

**Toast Types by Action:**
- **Success:** Login, document upload, analysis complete, report generated
- **Error:** API failures, validation errors, network issues
- **Info:** Background tasks started, data refreshing
- **Warning:** Quota limits, missing data, deprecated features
- **Loading:** Long-running operations (forecast generation, analysis)

**Acceptance Criteria:**
- [ ] Success toasts: green, checkmark icon, 3s duration
- [ ] Error toasts: red, error icon, 5s duration, dismissible
- [ ] Info toasts: blue, info icon, 4s duration
- [ ] Warning toasts: yellow, warning icon, 4s duration
- [ ] Loading toasts: spinner, persist until operation completes
- [ ] Toast position: top-right or bottom-right (consistent)

#### R2.3 Toast Messages
**Priority:** Medium  
**Description:** Clear, actionable toast messages

**Acceptance Criteria:**
- [ ] Messages are concise (< 60 characters)
- [ ] Error messages suggest next steps
- [ ] Success messages confirm what happened
- [ ] Loading messages indicate what's happening
- [ ] No technical jargon in user-facing messages

---

## 3. Competition Analysis Module

### Requirements

#### R3.1 Competition Data Collection
**Priority:** High  
**Description:** Fetch competitor data from multiple real APIs

**Data Sources:**
- Overpass API (OpenStreetMap) - business locations
- Google Places API (if available) - business details
- Government MSME data - registered businesses
- News API - competitor news and activities
- Economic data - market size and growth

**Acceptance Criteria:**
- [ ] Fetch businesses in same industry and city
- [ ] Collect: name, location, category, rating (if available)
- [ ] Store in MongoDB collection: competition_analysis
- [ ] Cache results for 24 hours
- [ ] Handle API rate limits gracefully
- [ ] Fallback to cached data if APIs fail

#### R3.2 Competition Analysis Output
**Priority:** High  
**Description:** Generate comprehensive competition analysis report

**Analysis Components:**
1. **Competition Overview**
   - Total competitor count
   - Competition density score (Low/Medium/High)
   - Market saturation level
   - Demand vs competition ratio

2. **Geographic Analysis**
   - High competition areas (list of neighborhoods/zones)
   - Low competition areas (opportunities)
   - Competition heat map data

3. **Top Competitors**
   - List of 5-10 major competitors
   - Their locations
   - Estimated market share (if available)

4. **Market Gaps**
   - Underserved segments
   - Pricing gaps
   - Service gaps
   - Geographic gaps

5. **AI Recommendations**
   - Differentiation strategies
   - Target market suggestions
   - Pricing strategy
   - Location recommendations
   - Marketing approach

**Acceptance Criteria:**
- [ ] Analysis completes in < 30 seconds
- [ ] All sections populated with real data
- [ ] AI recommendations based on actual market data
- [ ] Results stored in MongoDB
- [ ] Results cached for 7 days
- [ ] Re-analysis available on demand

#### R3.3 Competition Analysis UI
**Priority:** High  
**Description:** Create dedicated Competition Analysis page

**UI Components:**
- Competition overview cards (total competitors, density, saturation)
- Geographic breakdown (high/low competition areas)
- Top competitors list with details
- Market gaps section with opportunities
- AI recommendations panel
- Refresh button to re-run analysis
- Export to PDF button

**Acceptance Criteria:**
- [ ] Page accessible from sidebar menu
- [ ] Requires business selection
- [ ] Shows loading state during analysis
- [ ] Data visualizations (charts for density, saturation)
- [ ] Responsive design (mobile-friendly)
- [ ] Error handling with retry option

#### R3.4 Competition Data Structure
**Priority:** High  
**Description:** Define MongoDB schema for competition analysis

```javascript
{
  business_id: ObjectId,
  city: String,
  industry: String,
  total_competitors: Number,
  competition_density: String, // "Low", "Medium", "High"
  market_saturation: String, // "Low", "Medium", "High"
  demand_vs_competition_ratio: Number,
  top_competitors: [
    {
      name: String,
      location: String,
      category: String,
      distance_km: Number,
      estimated_market_share: Number
    }
  ],
  high_competition_areas: [String],
  low_competition_areas: [String],
  market_gaps: [
    {
      gap_type: String, // "pricing", "service", "geographic", "segment"
      description: String,
      opportunity_score: Number
    }
  ],
  pricing_estimate: {
    min: Number,
    max: Number,
    average: Number
  },
  ai_recommendations: {
    differentiation: [String],
    target_market: [String],
    pricing_strategy: String,
    location_strategy: String,
    marketing_approach: String
  },
  created_at: Date,
  updated_at: Date,
  expires_at: Date // Cache expiry
}
```

**Acceptance Criteria:**
- [ ] Schema implemented in MongoDB
- [ ] Indexes on: business_id, city, industry, created_at
- [ ] TTL index on expires_at for auto-cleanup
- [ ] Validation rules enforced

---

## 4. Integration Requirements

### R4.1 Sidebar Menu Update
**Priority:** Medium  
**Description:** Add Competition Analysis to navigation

**New Menu Structure:**
- Overview
- Insights
- Market Analysis
- Location Intelligence
- **Competition Analysis** (NEW)
- Forecast
- Reports
- Documents (RAG)
- Agents
- Data Explorer
- Settings

**Acceptance Criteria:**
- [ ] Competition Analysis menu item added
- [ ] Icon selected (e.g., users-icon or target-icon)
- [ ] Route: /competition
- [ ] Active state highlighting
- [ ] Requires business selection

### R4.2 API Endpoints
**Priority:** High  
**Description:** Create backend endpoints for new features

**Endpoints:**
1. `POST /api/documents/upload` - Upload with progress events
2. `GET /api/documents/upload-status/{upload_id}` - Poll upload progress
3. `GET /api/competition/analyze/{business_id}` - Get/generate competition analysis
4. `POST /api/competition/refresh/{business_id}` - Force re-analysis
5. `GET /api/competition/competitors/{business_id}` - Get competitor list

**Acceptance Criteria:**
- [ ] All endpoints implemented
- [ ] Authentication required
- [ ] Business ownership verified
- [ ] Rate limiting applied
- [ ] Error handling with proper status codes
- [ ] API documentation updated

---

## 5. Technical Specifications

### Frontend Stack
- React (existing)
- Toast library: react-hot-toast or sonner
- Progress UI: Custom stepper component or react-step-progress-bar
- Charts: recharts or chart.js (for competition visualizations)

### Backend Stack
- FastAPI (existing)
- MongoDB (existing)
- FAISS (existing)
- Neo4j (existing)
- OpenRouter LLM (existing)
- External APIs: Overpass, News API, Weather API

### Data Flow

#### Document Upload Flow
```
User selects file
  ↓
Frontend: Show progress UI
  ↓
Backend: Receive file
  ↓
Backend: Extract text → Emit progress
  ↓
Backend: Clean text → Emit progress
  ↓
Backend: Chunk text → Emit progress
  ↓
Backend: Generate embeddings → Emit progress
  ↓
Backend: Store in FAISS → Emit progress
  ↓
Backend: Save metadata to MongoDB → Emit progress
  ↓
Frontend: Show completion toast
```

#### Competition Analysis Flow
```
User clicks "Analyze Competition"
  ↓
Frontend: Show loading toast
  ↓
Backend: Check cache (< 7 days old)
  ↓
If cached: Return cached data
  ↓
If not cached:
  - Fetch from Overpass API
  - Fetch from MSME data
  - Fetch from News API
  - Process and analyze
  - Generate AI recommendations
  - Store in MongoDB
  - Return results
  ↓
Frontend: Display analysis
Frontend: Show success toast
```

---

## 6. Success Metrics

### User Experience
- Document upload completion rate > 95%
- Average time to understand upload progress < 5 seconds
- User satisfaction with toast notifications > 4.5/5
- Competition analysis page views > 30% of active users

### Technical Performance
- Document processing time < 60 seconds for 10-page PDF
- Toast render time < 100ms
- Competition analysis generation < 30 seconds
- API error rate < 2%
- Cache hit rate for competition data > 70%

### Business Impact
- Increased document uploads by 40%
- Reduced support tickets about upload status by 60%
- Competition analysis used in 50% of business decisions
- User retention improved by 15%

---

## 7. Dependencies

### External APIs
- Overpass API (OpenStreetMap) - Free, no key required
- News API - Requires API key (check .env)
- Google Places API - Optional, requires API key
- Government MSME API - Free, may require registration

### Libraries to Install
```bash
# Frontend
npm install react-hot-toast
# or
npm install sonner

# Backend (if not already installed)
pip install overpy  # Overpass API client
pip install newsapi-python  # News API client
```

---

## 8. Risks and Mitigations

### Risk 1: API Rate Limits
**Impact:** High  
**Mitigation:**
- Implement aggressive caching (7 days for competition data)
- Use multiple API sources as fallbacks
- Queue requests during high traffic
- Show cached data with "last updated" timestamp

### Risk 2: Document Processing Failures
**Impact:** Medium  
**Mitigation:**
- Implement retry logic with exponential backoff
- Store partial progress to resume from failure point
- Clear error messages with recovery steps
- Manual retry button for users

### Risk 3: Inaccurate Competition Data
**Impact:** Medium  
**Mitigation:**
- Use multiple data sources and cross-validate
- Show data confidence scores
- Allow users to report inaccuracies
- Regular data quality audits

### Risk 4: Performance Degradation
**Impact:** Medium  
**Mitigation:**
- Async processing for document uploads
- Background jobs for competition analysis
- Database indexing for fast queries
- CDN for static assets

---

## 9. Testing Requirements

### Unit Tests
- [ ] Document chunking logic
- [ ] Toast notification helpers
- [ ] Competition analysis calculations
- [ ] API client error handling

### Integration Tests
- [ ] Document upload end-to-end
- [ ] Competition analysis with real APIs
- [ ] Toast notifications across all pages
- [ ] Cache invalidation logic

### User Acceptance Tests
- [ ] Upload various document types (PDF, DOCX, TXT)
- [ ] Verify progress steps display correctly
- [ ] Test toast notifications for all actions
- [ ] Review competition analysis accuracy
- [ ] Test on mobile devices

---

## 10. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Install toast library
- [ ] Create toast utility functions
- [ ] Replace all alert() calls with toasts
- [ ] Create progress UI component
- [ ] Set up competition_analysis MongoDB collection

### Phase 2: RAG Upload UX (Week 1-2)
- [ ] Implement backend progress events
- [ ] Update document upload endpoint
- [ ] Integrate progress UI in frontend
- [ ] Implement proper text chunking
- [ ] Add error handling and retry logic
- [ ] Test with various document types

### Phase 3: Competition Analysis (Week 2-3)
- [ ] Integrate Overpass API
- [ ] Integrate News API
- [ ] Implement competition analysis logic
- [ ] Create AI recommendation engine
- [ ] Build competition analysis UI
- [ ] Add to sidebar navigation
- [ ] Implement caching strategy

### Phase 4: Polish & Testing (Week 3-4)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] UI/UX refinements
- [ ] Documentation updates
- [ ] User training materials
- [ ] Deploy to production

---

## 11. Open Questions

1. **Toast Library Choice:** react-hot-toast vs sonner vs shadcn toast?
   - Recommendation: react-hot-toast (most popular, well-maintained)

2. **Progress Updates:** WebSocket vs polling?
   - Recommendation: Polling (simpler, works with existing infrastructure)

3. **Competition Data Refresh:** Manual only or automatic background refresh?
   - Recommendation: Manual with option for auto-refresh (user preference)

4. **Google Places API:** Required or optional?
   - Recommendation: Optional (Overpass API sufficient for MVP)

5. **Export Format:** PDF only or also Excel/CSV?
   - Recommendation: Start with PDF, add Excel in future iteration

---

## 12. Next Steps

After requirements approval:
1. Create detailed design document
2. Break down into implementation tasks
3. Estimate effort for each task
4. Assign tasks to development sprints
5. Begin Phase 1 implementation

---

## Appendix

### A. Example Toast Messages

```javascript
// Success
toast.success("Document uploaded successfully");
toast.success("Competition analysis generated");
toast.success("Market report downloaded");

// Error
toast.error("Failed to upload document. Please try again.");
toast.error("Unable to fetch competition data. Check your connection.");

// Loading
const toastId = toast.loading("Analyzing competition...");
// Later: toast.success("Analysis complete!", { id: toastId });

// Info
toast.info("Your analysis is being generated in the background");

// Warning
toast.warning("API rate limit approaching. Results may be cached.");
```

### B. Example Competition Analysis Output

```json
{
  "total_competitors": 134,
  "competition_density": "High",
  "market_saturation": "Medium",
  "high_competition_areas": ["City Center", "Malviya Nagar"],
  "low_competition_areas": ["Jagatpura", "Vaishali Nagar"],
  "top_competitors": [
    {"name": "Restaurant A", "location": "City Center", "distance_km": 2.5},
    {"name": "Restaurant B", "location": "Malviya Nagar", "distance_km": 3.1}
  ],
  "market_gaps": [
    {"gap_type": "service", "description": "Healthy food segment", "opportunity_score": 8},
    {"gap_type": "service", "description": "Late-night delivery", "opportunity_score": 7}
  ],
  "ai_recommendations": {
    "differentiation": ["Focus on healthy options", "Offer meal subscriptions"],
    "target_market": ["Health-conscious professionals", "Office workers"],
    "pricing_strategy": "Premium pricing for quality ingredients",
    "location_strategy": "Start in Jagatpura (low competition)",
    "marketing_approach": "Digital marketing + office partnerships"
  }
}
```

---

**Document Status:** Requirements Complete  
**Next Phase:** Design  
**Estimated Effort:** 3-4 weeks  
**Priority:** High
