# Task Breakdown: AI Legal Operations Platform

## Phase 1: Structure

### Task 1.1: Set up PostgreSQL database connection
**Description**: Configure FastAPI to connect to local PostgreSQL database using environment variables
**Acceptance Criteria**:
- Database connection established successfully
- Environment variables loaded from .env file
- Connection pooling configured
**Dependencies**: None
**Effort**: 1 day
**Files**: app/core/config.py, app/db/session.py, .env.example

### Task 1.2: Create User table
**Description**: Implement User table with id, first_name, last_name, username, password, email, phone, role
**Acceptance Criteria**:
- Table created with correct schema
- Role enum supports 'supervisor' and 'basic'
- Proper indexes on username and email
**Dependencies**: Task 1.1
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.3: Create client table
**Description**: Implement client table with id,first_name, last_name,email, phone,
**Acceptance Criteria**:
- Table created with correct schema
**Dependencies**: Task 1.1
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.4: Create Case table
**Description**: Implement Case table with id, title, status, created_at,client_id,case_reference_number
**Acceptance Criteria**:
- Table created with correct schema
- Status defaults to appropriate value
- Created_at timestamp auto-generated
- case_reference_number auto-generated
**Dependencies**: Task 1.1,task 1.3
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.5: Create Watcher table (join table)
**Description**: Implement Watcher table with id, user_id, case_id, access_type (assigned | viewer)
**Acceptance Criteria**:
- Foreign keys to User and Case tables
- Access_type enum with 'assigned' and 'viewer'
- Composite unique constraint on user_id + case_id
**Dependencies**: Tasks 1.2, 1.4
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.6: Create Document table
**Description**: Implement Document table with id, case_id, filename, uploaded_by, tags, uploaded_at
**Acceptance Criteria**:
- Foreign keys to Case and User tables
- Tags stored as JSON array
- Uploaded_at timestamp auto-generated
**Dependencies**: Tasks 1.2, 1.4
**Effort**: 0.5 days
**Files**: app/db/models.py


### Task 1.7: Create Deadline table
**Description**: Implement Deadline table with id, case_id, due_date, description, status
**Acceptance Criteria**:
- Foreign key to Case table
- Status enum with 'pending', 'missed', 'completed'
- Due_date indexed for performance
**Dependencies**: Task 1.4
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.8: Create AuditLog table
**Description**: Implement AuditLog table with id, user_id, action, datetime, change_in
**Acceptance Criteria**:
- Foreign key to User table (nullable)
- Datetime auto-generated
- Change_in stored as JSON
**Dependencies**: Task 1.2
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.9: Create notification table
**Description**: Implement notification table with id,user_id,deadline_id, status, created_at
**Acceptance Criteria**:
- Foreign key to Deadline table,User table
- deadline_id indexed for performance
**Dependencies**: Task 1.7
**Effort**: 0.5 days
**Files**: app/db/models.py

### Task 1.10: Set up FastAPI application structure
**Description**: Create basic FastAPI app with database integration and health endpoint
**Acceptance Criteria**:
- FastAPI app starts successfully
- Health endpoint returns 200 OK
- Database tables created on startup
**Dependencies**: All Phase 1 tasks
**Effort**: 1 day
**Files**: app/main.py, app/api/

## Phase 2: Core Features

### Task 2.1: Implement Case CRUD endpoints
**Description**: Build endpoints for Create, Read, Update, Close case operations
**Acceptance Criteria**:
- POST /cases creates new case
- GET /cases lists all cases
- GET /cases/{id} retrieves specific case
- PUT /cases/{id} updates case
- PUT /cases/{id}/close closes case
**Dependencies**: Phase 1 complete
**Effort**: 2 days
**Files**: app/api/endpoints/cases.py, app/crud/cases.py

### Task 2.2: Implement Document management endpoints
**Description**: Build endpoints for uploading, viewing, and searching documents,files will be stored on the server's disk in a /uploads folder, the Document table stores the file path
**Acceptance Criteria**:
- POST /documents/upload uploads file to case
- GET /documents lists documents with search
- GET /documents/{id} retrieves document
- GET /documents/{id}/download serves file
**Dependencies**: Phase 1 complete
**Effort**: 2 days
**Files**: app/api/endpoints/documents.py, app/crud/documents.py

### Task 2.3: Implement Deadline CRUD endpoints
**Description**: Build endpoints for create, update, delete deadlines linked to cases
**Acceptance Criteria**:
- POST /deadlines creates deadline for case
- GET /deadlines lists deadlines
- PUT /deadlines/{id} updates deadline
- DELETE /deadlines/{id} deletes deadline
**Dependencies**: Phase 1 complete
**Effort**: 1.5 days
**Files**: app/api/endpoints/deadlines.py, app/crud/deadlines.py

### Task 2.4: Implement deadline alert background job
**Description**: Add background job that checks due dates and triggers alerts
**Acceptance Criteria**:
- Job runs periodically (e.g., daily)
- Identifies deadlines within user-desired days
- Creates notification records for users
- Notifications appear on login
**Dependencies**: Task 2.3
**Effort**: 1.5 days
**Files**: app/services/deadline_alerts.py, background job setup

### Task 2.6: Add search and filtering to Case endpoints
**Description**: Add a search and filtering system that checks and organize Cases 
**Acceptance Criteria**:
- GET /cases accepts optional query parameters: status, client_name, assigned_user_id, date_from, date_to, title, case_reference_number 
- returns filtered list of matching cases
**Dependencies**: Phase 2.1 complete
**Files**: app/api/endpoints/cases.py, app/crud/cases.py

### Tasks 2.7: Add filtering to Deadline and Document endpoints
**Description**:filtering system that checks and organize Deadline and document data
**Acceptance Criteria**:
- GET /Deadline parameters: case_id, due_date, status
-GET /Document parameters: case_id,filename, uploaded_by, uploaded_at
**Dependencies**: task 2.2, 2.3
**Files**: app/api/endpoints/deadlines.py, app/crud/deadlines.py , app/api/endpoints/documents.py, app/crud/documents.py

### Task 2.8: Implement AI insights query endpoint
**Description**: Build endpoint that fetches relevant data and queries AI API where it will decides the right case or document by using key words,names 
**Acceptance Criteria**:
- POST /ai/query accepts natural language question
- Fetches relevant case/document data
- Sends to Claude API with context
- Returns AI-generated answer with citations
**Dependencies**: Phase 1 complete
**Effort**: 2 days
**Files**: app/api/endpoints/ai.py, app/services/ai_query.py

### Task 2.9: Implement structured AI assistant endpoint

**Description**:Build endpoint that retrieve depend on the question where it will send to the clauda api and respond 

**Supported Tasks**:
- Case Duration Query
  - Input:"how long has this case been going?"
  - Data source:the ai will go look in the database to the case table and will look for created_at columns
  - Output:"Case: Ahmed Property Dispute
    Reference: CASE-2024-0012
    Created: 02/11/2022
    Duration: 2 years, 5 months
    Status: Active"
- Client Case Count Query
  - Input:"how many cases have we got from the client?"
  - Data source:the ai will go to the client table and will look for first_name, last_name or perhaps even id if given
  - Output:"(this client) has 3 cases"
    (cases 1) carted at: 05/04/2022
    status: active
    (cases2) .... and so on
- Deadline Status Query
  - Input:"has this case reached the deadline for the court hearing"
  - Data source:the ai will look for the deadline table 
  - Output:(case deadline is :02/06/2026)
    Case: Ahmed Property Dispute
    Reference: CASE-2024-0012 
    Deadline: 02/06/2026
    Days Remaining: 92
    Status: Pending


**Routing Logic**:
- "when a user asks 'how long has this case been going' the AI looks for keywords — 'been going' maps to created_at column"
- "how many cases have we got from the client?"'how many case' tell the ai to count 
- "has this case reached the deadline for the court hearing"'case reached the deadline for the court hearing' tells the ai to look for deadline of the court hearing
- "If no keywords match, return a clarification request asking the user to rephrase"

**Acceptance Criteria**:
- look for keywords
- Fetches relevant case/document/deadline data
- Sends to Claude API with context
- Returns AI-generated answer with citations
- /ask endpoint routes correctly to all three defined tasks
- Ambiguous or unrecognized input returns a clarification prompt instead of an error

**Reflection Note**:
- What works:Returns answer with the data that has been question 
- Limitation:the user will need to specify if the user did not specify who or what he is asking for it will not be able to retrieve

**Dependencies**:task 2.8
**Files**:app/api/endpoints/ai_assistant.py app/services/ai_assistant.py


## Phase 3: Frontend

## Task 3.1: Set up React project structure and routing
- Description: Initialize React project with page routing and environment configuration
- Acceptance Criteria:

- React app runs locally
- Routes exist for: login, dashboard, cases, case detail, AI assistant, deadlines
- REACT_APP_API_URL configured in .env for backend connection
- Dependencies: Phase 1-4 complete
- Effort: 1 day
- Files: src/App.js, src/pages/, .env

## Task 3.2: Build Login page
- Description: Build login form connected to POST /auth/login, store JWT token on success
- Acceptance Criteria:

- Form accepts username and password
- JWT token stored on success
- Redirects to dashboard after login
- Error message shown on invalid credentials
- Dependencies: Task 3.1
- Effort: 0.5 days
- Files: src/pages/Login.js, src/services/auth.js

## Task 3.3: Build Dashboard page
- Description: Display overview of active cases, upcoming deadlines, and alerts
- Acceptance Criteria:

- Shows total active cases
- Shows upcoming deadlines
- Shows recent alerts
- Calls Case and Deadline endpoints
- Dependencies: Task 3.1, Task 2.1, Task 2.3
- Effort: 1 day
- Files: src/pages/Dashboard.js, src/services/api.js

## Task 3.4: Build Case Management page
- Description: Display case list with search, filter, and create case functionality
- Acceptance Criteria:

- Lists all accessible cases
- Search and filter by status, client, reference number
- Create new case form works
- Navigates to Case Detail on selection
- Dependencies: Task 3.1, Task 2.1, Task 2.6
- Effort: 1.5 days
- Files: src/pages/Cases.js, src/services/cases.js

## Task 3.5: Build Case Detail page
- Description: Display single case with documents, deadlines, and update/delete actions
- Acceptance Criteria:

- Shows case information
- Lists related documents with download
- Lists related deadlines with status
- Update and delete actions work
- Dependencies: Task 3.4, Task 2.2, Task 2.3
- Effort: 1.5 days
- Files: src/pages/CaseDetail.js

## Task 3.6: Build AI Assistant page
- Description: Build interface for natural language queries connected to /ask endpoint
- Acceptance Criteria:

- Input field accepts natural language question
- Displays structured response
- Shows warning messages when data is insufficient
- Dependencies: Task 3.1, Task 2.9
- Effort: 1 day
- Files: src/pages/AIAssistant.js, src/services/ai.js

## Task 3.7: Build Deadlines page
- Description: Display all deadlines with filter by status and case
- Acceptance Criteria:

- Lists all accessible deadlines
- Filter by status and case works
- Create, update, delete deadline actions work
- Dependencies: Task 3.1, Task 2.3, Task 2.7
- Effort: 1 day
- Files: src/pages/Deadlines.js

## Phase 4: Security & Compliance

### Task 4.1: Implement user registration endpoint
**Description**: Build endpoint for new user registration with automatic basic role assignment
**Acceptance Criteria**:
- POST /auth/register creates user with first_name, last_name, email, phone
- Username and password required
- Role automatically set to 'basic'
- Email uniqueness enforced
**Dependencies**: Phase 1 complete
**Effort**: 1 day
**Files**: app/api/endpoints/auth.py, app/services/auth.py

### Task 4.2: Implement user login endpoint
**Description**: Build endpoint for user authentication
**Acceptance Criteria**:
- POST /auth/login validates username/password
- Returns JWT token on success
- Proper error messages for invalid credentials
**Dependencies**: Task 4.1
**Effort**: 1 day
**Files**: app/api/endpoints/auth.py, app/services/auth.py

### Task 4.3: Implement role-based access control
**Description**: Add middleware and decorators for role-based permissions
**Acceptance Criteria**:
- Only 'supervisor' and 'basic' roles can access core features
- Supervisor can change user roles
- Basic users have standard access
**Dependencies**: Task 4.2
**Effort**: 1.5 days
**Files**: app/api/middleware/rbac.py, app/services/permissions.py

### Task 4.4: Implement audit logging
**Description**: Add automatic logging for all user actions
**Acceptance Criteria**:
- All CRUD operations logged to AuditLog table
- Supervisor role can view audit logs
- Logs include user_id, action, datetime, change_in
**Dependencies**: Phase 1 complete
**Effort**: 1 day
**Files**: app/services/audit.py, app/api/endpoints/audit.py

## Phase 5: Testing & Deployment

### Task 5.1: Test Phase 2 endpoints functionality
**Description**: Verify all CRUD endpoints work correctly
**Acceptance Criteria**:
- Case CRUD operations successful
- Document upload/view/search works
- Deadline CRUD operations functional
- AI query returns valid responses
**Dependencies**: Phase 2 complete
**Effort**: 2 days
**Files**: tests/test_api.py

### Task 5.2: Test role restrictions enforcement
**Description**: Verify security controls work properly
**Acceptance Criteria**:
- Unauthorized users blocked from core features
- Supervisor can change roles and view audit logs
- Basic users have appropriate access
**Dependencies**: Phase 3 complete
**Effort**: 1.5 days
**Files**: tests/test_security.py

### Task 5.3: Test notification system
**Description**: Verify deadline alerts appear on login
**Acceptance Criteria**:
- Background job creates notifications
- Notifications display on user login
- Alert timing respects user preferences
**Dependencies**: Task 2.4, Phase 3 complete
**Effort**: 1 day
**Files**: tests/test_notifications.py

### Task 5.4: Prepare for deployment
**Description**: Set up production configuration and deployment scripts
**Acceptance Criteria**:
- Docker configuration complete
- Environment variables configured
- Basic deployment documentation
**Dependencies**: All phases complete
**Effort**: 1 day
**Files**: Dockerfile, docker-compose.yml, deployment docs