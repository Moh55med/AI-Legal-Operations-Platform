# Implementation Plan


## Phase 1: Structure
- Create table for users, cases, deadline, document, auditlog, watcher where:
User
- id, first_name, last_name,username,password, email, phone, role (supervisor | basic)

Case
- id, title, status, created_at

Watcher (join table: User ↔ Case)
- id, user_id, case_id, access_type (assigned | viewer)

Document
- id, case_id, filename, uploaded_by, tags, uploaded_at

Deadline
- id, case_id, due_date, description, status (pending | missed | completed)

AuditLog
- id, user_id, action, datetime, change_in


- Connect to local PostgreSQL through FastAPI to get data

## Phase 2: Core Features
- build a case Crud which Create, read, update, close a case
- build a document management end point where a user can uploading, viewing, or searching documents
- Build deadline endpoints: create, update, delete a deadline linked to a case. Add a background job that checks for due dates and triggers an alert when a deadline is within the user desired days the alert will be a notifications when the user log in 
- Query firm data using AI insights were when the user asks a question fetches the relevant case or document data, sends it to an AI API like Claude, and returns the answer

## Phase 3 Security & Compliance
- every one will need to make a username and a password one a new user enter he must put his fist name and last name and email and phone and he will automatically be assigned the role basic 
- the supervisor role is the only one who can change user role and see auditlog
- Only supervisor and basic users can use core features


## Phase 4 Testing & Deployment
- verify each Phase 2 endpoint works correctly, verify role restrictions are enforced, verify notifications appear on login after a deadline is due