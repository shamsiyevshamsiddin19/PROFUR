import { can, type User } from "./api";

export const operationAccess = {
  issues: { create: "inventory.add_issue", approve: null },
  returns: {
    create: "inventory.add_return",
    approve: "inventory.approve_return",
  },
  "write-offs": {
    create: "inventory.add_write_off",
    approve: "inventory.approve_write_off",
  },
} as const;

export type OperationKind = keyof typeof operationAccess;

export function availableOperations(user: User): OperationKind[] {
  if (!can(user, "inventory.view_stock")) return [];
  return (Object.keys(operationAccess) as OperationKind[]).filter((kind) => {
    const { create, approve } = operationAccess[kind];
    return can(user, create) || (approve !== null && can(user, approve));
  });
}

export function screenAllowed(user: User, screen: string): boolean {
  switch (screen) {
    case "settings":
      return true;
    case "administration":
      return Boolean(user.is_superuser || user.role_codes.includes("ADMIN"));
    case "receiving":
      return (
        can(user, "inventory.view_stock") &&
        can(user, "catalog.view_material") &&
        can(user, "inventory.add_receipt")
      );
    case "operations":
      return availableOperations(user).length > 0;
    case "materials":
      return can(user, "catalog.view_material");
    case "expenses":
      return can(user, "expenses.view_expense");
    case "expenseTypes":
      return can(user, "expenses.view_expensetype");
    case "stock":
    case "history":
    case "notifications":
      return can(user, "inventory.view_stock");
    default:
      return false;
  }
}
