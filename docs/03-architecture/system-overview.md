# System Architecture — Proposed, Not Approved

## Candidate system boundaries

- **Admin Web App** — warehouse, orders, production monitoring, finances, history.
- **Worker Mobile App** — role-aware tasks, acceptance, stage progress, material usage.
- **Backend API** — validation, business rules, authorization, transaction orchestration, calculations.
- **Relational Database** — persistent catalog, inventory ledger, orders, models, worker activities and accounting data.
- **Notifications** — task and discrepancy alerts.

## Important invariants
1. Inventory must never be reduced twice for one physical movement.
2. Costs depend on the customer-approved stock valuation rule (OQ-001).
3. Model totals must reconcile with order quantity.
4. Stage mismatch and excess material require alerts and saved explanations.
5. A project can close only after packaging and delivery stages.
6. History must retain historical facts after closure.
7. Worker data visibility must be enforced in backend authorization, not only UI.

## Decisions not made
Backend framework, web stack, mobile platform, database engine, hosting, notification provider, offline mode and authentication implementation. Select through documented ADR after P0 business clarification.

See [decision log](../09-decisions/decision-log.md).
