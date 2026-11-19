import { can, type User } from "./api";

export type Screen =
  | "home"
  | "settings"
  | "receiving"
  | "materials"
  | "stock"
  | "operations"
  | "expenses"
  | "history"
  | "expenseTypes"
  | "administration"
  | "notifications";
export const operationPermissions = {
  issues: ["inventory.add_issue"],
  returns: ["inventory.add_return", "inventory.approve_return"],
  "write-offs": ["inventory.add_write_off", "inventory.approve_write_off"],
};
export function operationAllowed(
  user: User,
  kind: keyof typeof operationPermissions,
) {
  return (
    can(user, "inventory.view_stock") &&
    operationPermissions[kind].some((code) => can(user, code))
  );
}
export function screenAllowed(user: User, screen: Screen): boolean {
  switch (screen) {
    case "home":
    case "settings":
      return true;
    case "administration":
      return Boolean(user.is_superuser || user.role_codes.includes("ADMIN"));
    case "materials":
      return can(user, "catalog.view_material");
    case "receiving":
      return (
        can(user, "inventory.view_stock") &&
        can(user, "catalog.view_material") &&
        can(user, "inventory.add_receipt")
      );
    case "operations":
      return (
        Object.keys(
          operationPermissions,
        ) as (keyof typeof operationPermissions)[]
      ).some((kind) => operationAllowed(user, kind));
    case "expenses":
      return can(user, "expenses.view_expense");
    case "expenseTypes":
      return can(user, "expenses.view_expensetype");
    default:
      return can(user, "inventory.view_stock");
  }
}
