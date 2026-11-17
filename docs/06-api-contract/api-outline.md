# API Contract — Draft Boundaries

Proposed resource groups, not final endpoint commitments:

- Authentication / session and role access
- Material categories, materials, receipts, inventory movements, stock snapshots
- Projects, models, variants, material norms, payment terms
- Production tasks, acceptance, work logs, stage counts, discrepancies
- Notifications
- Packaging, delivery, closure, historical reports

## Contract rules
An API endpoint requires request/response schemas, permission rule, validation, error conditions, transactional semantics and acceptance tests. Worker-owned data must be scoped server-side.

Do not implement arbitrary role management or a cost formula until the PM approves the relevant questions.
