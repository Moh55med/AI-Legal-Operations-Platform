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

## Phase 3: Security & Compliance

### Task 3.1: Implement user registration endpoint
**Description**: Build endpoint for new user registration with automatic basic role assignment
**Acceptance Criteria**:
- POST /auth/register creates user with first_name, last_name, email, phone
- Username and password required
- Role automatically set to 'basic'
- Email uniqueness enforced
**Dependencies**: Phase 1 complete
**Effort**: 1 day
**Files**: app/api/endpoints/auth.py, app/services/auth.py

### Task 3.2: Implement user login endpoint
**Description**: Build endpoint for user authentication
**Acceptance Criteria**:
- POST /auth/login validates username/password
- Returns JWT token on success
- Proper error messages for invalid credentials
**Dependencies**: Task 3.1
**Effort**: 1 day
**Files**: app/api/endpoints/auth.py, app/services/auth.py

### Task 3.3: Implement role-based access control
**Description**: Add middleware and decorators for role-based permissions
**Acceptance Criteria**:
- Only 'supervisor' and 'basic' roles can access core features
- Supervisor can change user roles
- Basic users have standard access
**Dependencies**: Task 3.2
**Effort**: 1.5 days
**Files**: app/api/middleware/rbac.py, app/services/permissions.py

### Task 3.4: Implement audit logging
**Description**: Add automatic logging for all user actions
**Acceptance Criteria**:
- All CRUD operations logged to AuditLog table
- Supervisor role can view audit logs
- Logs include user_id, action, datetime, change_in
**Dependencies**: Phase 1 complete
**Effort**: 1 day
**Files**: app/services/audit.py, app/api/endpoints/audit.py

## Phase 4: Testing & Deployment

### Task 4.1: Test Phase 2 endpoints functionality
**Description**: Verify all CRUD endpoints work correctly
**Acceptance Criteria**:
- Case CRUD operations successful
- Document upload/view/search works
- Deadline CRUD operations functional
- AI query returns valid responses
**Dependencies**: Phase 2 complete
**Effort**: 2 days
**Files**: tests/test_api.py

### Task 4.2: Test role restrictions enforcement
**Description**: Verify security controls work properly
**Acceptance Criteria**:
- Unauthorized users blocked from core features
- Supervisor can change roles and view audit logs
- Basic users have appropriate access
**Dependencies**: Phase 3 complete
**Effort**: 1.5 days
**Files**: tests/test_security.py

### Task 4.3: Test notification system
**Description**: Verify deadline alerts appear on login
**Acceptance Criteria**:
- Background job creates notifications
- Notifications display on user login
- Alert timing respects user preferences
**Dependencies**: Task 2.4, Phase 3 complete
**Effort**: 1 day
**Files**: tests/test_notifications.py

### Task 4.4: Prepare for deployment
**Description**: Set up production configuration and deployment scripts
**Acceptance Criteria**:
- Docker configuration complete
- Environment variables configured
- Basic deployment documentation
**Dependencies**: All phases complete
**Effort**: 1 day
**Files**: Dockerfile, docker-compose.yml, deployment docs