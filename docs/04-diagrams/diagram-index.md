# Diagram Index

The following diagrams are **drafts**. Update after PM-approved scope and roles.

## Use Case — high-level
```mermaid
flowchart LR
  A[Admin] --> B[Warehouse management]
  A --> C[Order and model management]
  A --> D[Production monitoring]
  A --> E[Project closing and reports]
  W[Worker] --> F[View assigned tasks]
  W --> G[Accept task]
  W --> H[Record work and material usage]
```

## Production Activity
```mermaid
flowchart TD
  P[Create project and models] --> A[Arra]
  A --> B[Freza]
  B --> C[Shkurka]
  C --> D[Kraska]
  D --> E[Zbor]
  E --> F[Upakovka]
  F --> G[Delivery and cost entry]
  G --> H[Close and archive in History]
```

## Remaining design work
- Formal UML Use Case with confirmed role permissions
- C4 Context / Container
- ER Diagram based on clarified inventory rules
- Sequence diagrams for material receipt, issue, production discrepancy, project closing
