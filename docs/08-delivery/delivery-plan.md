# Delivery Plan — AI-assisted Team

## Team structure
PM: instructor. Team Lead: technical coordination. Three additional engineers: recommended backend/database, admin web, worker mobile; exact assignments TBD.

## Current Jira state
- Four epics: PCRM-1–4.
- Requirement-backed Stories: PCRM-5–24, PCRM-27–30 (24).
- PCRM-25 and PCRM-26 flagged duplicates, do not schedule.
- Planning Tasks: PCRM-31–37.
- Sprint not started.

## Proposed stage gates
1. PM review of open P0 questions.
2. User stories and approved scope.
3. Architecture/ERD/API contract review.
4. GitHub branch protection and AI coding guidelines.
5. Small vertical slice: receive warehouse material -> persist transaction -> update stock -> test.
6. Iterative web/mobile integration with code reviews and CI.
7. Customer UAT and release.

## AI coding review checklist
- Trace implementation to approved user story.
- Never paste secrets/customer data into agent prompts.
- Require automated tests, human review and reproducible run instructions.
- No direct push to main; use pull requests.
- Merge only when behavior, security and data invariants pass checks.
