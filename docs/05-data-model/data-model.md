# Data Model — Initial Concepts

Suggested entities (not yet final tables):

- User, Role, Permission, RolePermission (dynamic RBAC still pending PM approval).
- MaterialCategory, Material, MaterialReceipt, InventoryMovement.
- Project, ProjectPayment, Model, ModelVariant, MaterialNorm.
- Worker, WorkTask, WorkLog, ProductionStage, StageDiscrepancy.
- Expense, PackagingRecord, Delivery, ProjectClosure.

## Relationships
- One Project has many Models, Payments, Tasks and Expenses.
- One Model can have multiple variants and per-detail material norms.
- InventoryMovement references Material and, where applicable, Project/Worker.
- WorkLog references Worker/Group, Task, Stage, parts and actual quantities.
- Closure produces retained project-level financial and production summaries.

## Validation risks
Valuation method, reservation timing, group-account identity, piecework rate, loss and rework behavior are unresolved; avoid finalizing ERD migrations until P0 decisions.
