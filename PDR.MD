# PDR: AI Legal Operations Platform

## Problem Statement
Many law firms struggle with manual, unstructured workflows. This leads to missed deadlines, scattered documents, and poor visibility into case status.

## Target users
- Small and medium legal firms with process gaps
- Legal teams with high document volume and time-sensitive deadlines
- Firms seeking centralized, AI-augmented case operations

## features
A platform to:
- manage cases
- track deadlines with alerts
- organize legal documents in one place
- query firm data using AI insights

## system components
- Backend: Python + FastAPI
- CLI / tools:
  - Claude Code CLI (coding assistant)
  - CodeRabbit CLI (pre-commit review)
  - spec-kit (spec/plan/task structure)
  - git/github

## constraints
- Must use Python + FastAPI
- No AI answers are legally binding; show source citations
- No hardcoded API keys in repo; use vault/secrets

## Scope
- Case management (create, update, list, close)
- Deadline management + scheduling
- Document repository with tagging/search
- User auth and roles
- AI query endpoint (natural language over cases/docs)

## Goals and success metrics
- MVP features implemented: case CRUD, documents, deadlines, AI query
- Nonfunctional: secure access control, reliable alerting, API docs
- Metrics:
  - reduce deadline misses by 75%
  - reduce document retrieval time 2x
  - 70% active usage in pilot group