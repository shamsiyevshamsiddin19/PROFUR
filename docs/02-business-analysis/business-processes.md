# Business Processes — Draft

## Primary workflow

1. Admin creates order/project (client, sum, quantity, deadline).
2. Add models/variants and material norms.
3. Calculate planned material needs and availability.
4. Assign workers by model and production stage.
5. Worker accepts mobile task and records work/material usage.
6. Progress: Arra -> Freza -> Shkurka -> Kraska -> Zbor.
7. Compare actual versus planned usage and stage-to-stage counts; record discrepancies and reasons.
8. Package finished products, record delivery cost.
9. Close project and retain historic costs, worker output, payment state and financial statistics.

## Actors
- **Admin** — sees active projects, production progress, warehouse and reports (exact permissions to confirm).
- **Worker** — sees role-relevant tasks, accepts them and records work.
- **Worker group** — special shared-account case for cutting (per TZ; attribution open).
- **PM / Customer** — project approval stakeholders, not necessarily software accounts.

## Cross-cutting rules
All operations should retain time/history as required by TZ. Detail-level access policies are not fully specified. See [open questions](../01-requirements/open-questions.md).
