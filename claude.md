## project context
the project is platform that manage cases track deadlines with alerts organize legal documents in one place query firm data using AI insights as a lot of legal firms struggle with manual, unstructured workflows. This leads to missed deadlines, scattered documents, and poor visibility into case status.

## rules and constraints
- Must use Python + FastAPI
- No AI answers are legally binding; show source citations
- No hardcoded API keys in repo; use vault/secrets

## what Claude should not do
- don't make assumption to missing data
- don't put hardcoded API
- don't put stuff your not asked to

## standards the repository should follow
- .gitignore for .env
- API keys vaulted via secret manager
- request/response schema docs up to date
- formatting (Python)
