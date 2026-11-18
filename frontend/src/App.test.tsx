// @vitest-environment jsdom
import { afterEach, expect, test, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
  waitFor,
  fireEvent,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "./App";

afterEach(() => {
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
  vi.unstubAllGlobals();
  location.hash = "";
});
const user = {
  id: 1,
  username: "operator",
  first_name: "",
  last_name: "",
  roles: [],
  role_codes: [],
};
const material = {
  id: 41,
  name: "MDF",
  display_name: "MDF 18 mm",
  unit: "sheet",
  category: { id: 1, name: "MDF" },
};
function response(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}
function baseFetch(path: string) {
  if (path === "/api/auth/me/") return response(user);
  if (path === "/api/auth/csrf/")
    return response({ csrfToken: "rotated-token" });
  if (path.startsWith("/api/v1/materials/"))
    return response({ results: [material], count: 1, next: null });
  if (path === "/api/v1/receipts/")
    return response({ results: [], next: null, count: 0 });
  return response({}, 404);
}

test("login uses a fresh CSRF token and the selected language", async () => {
  const calls: [string, RequestInit][] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string, init: RequestInit) => {
      calls.push([path, init]);
      if (path === "/api/auth/me/") return response({}, 403);
      if (path === "/api/auth/login/") return response({ user });
      return baseFetch(path);
    }),
  );
  render(<App />);
  await screen.findByLabelText("Foydalanuvchi nomi");
  fireEvent.change(screen.getByRole("combobox", { name: "Language" }), {
    target: { value: "en" },
  });
  await userEvent.type(screen.getByLabelText("Username"), "operator");
  await userEvent.type(screen.getByLabelText("Password"), "password");
  await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
  await screen.findByRole("heading", { name: "Material receipts" });
  const login = calls.find(([path]) => path === "/api/auth/login/")![1];
  expect(new Headers(login.headers).get("X-CSRFToken")).toBe("rotated-token");
  expect(new Headers(login.headers).get("Accept-Language")).toBe("en");
  expect(localStorage.getItem("profur.language")).toBe("en");
});

test("a failed receipt reuses its exact USD payload and key after remount", async () => {
  localStorage.setItem("profur.language", "en");
  const writes: RequestInit[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string, init: RequestInit) => {
      if (path === "/api/v1/receipts/" && init.method === "POST") {
        writes.push(init);
        if (writes.length === 1) throw new TypeError("Connection lost");
        return response({
          id: 19,
          quantity_on_hand_after: "20.00",
          quantity: "20",
          total_amount: "540.00",
          currency: "USD",
          unit_price: "27",
          received_on: "2026-11-18",
          material,
        });
      }
      return baseFetch(path);
    }),
  );
  const first = render(<App />);
  await screen.findByRole("option", { name: "MDF 18 mm · sheet" });
  fireEvent.change(screen.getByLabelText("Material"), {
    target: { value: "41" },
  });
  fireEvent.change(screen.getByLabelText("Quantity"), {
    target: { value: "20" },
  });
  fireEvent.change(screen.getByLabelText("Total amount"), {
    target: { value: "540.00" },
  });
  await userEvent.click(screen.getByRole("button", { name: "Save receipt" }));
  await screen.findByRole("button", { name: "Retry the same request" });
  first.unmount();
  render(<App />);
  const retry = await screen.findByRole("button", {
    name: "Retry the same request",
  });
  await userEvent.click(retry);
  await screen.findByText(/Receipt saved/);
  expect(writes).toHaveLength(2);
  expect(writes[0].body).toBe(writes[1].body);
  expect(JSON.parse(String(writes[0].body)).currency).toBe("USD");
  expect(new Headers(writes[0].headers).get("Idempotency-Key")).toBe(
    new Headers(writes[1].headers).get("Idempotency-Key"),
  );
  expect(sessionStorage.getItem("profur.receipt.pending.1")).toBeNull();
});

test("unavailable catalogue cannot submit a fabricated receipt", async () => {
  const fetchMock = vi.fn(async (path: string) =>
    path === "/api/auth/me/" ? response(user) : response({}, 404),
  );
  vi.stubGlobal("fetch", fetchMock);
  render(<App />);
  await screen.findAllByText(
    "Bu xizmat hozircha ishlamayapti. Keyinroq qayta tekshiring.",
  );
  await waitFor(() =>
    expect(
      screen
        .getByRole("button", { name: "Kirimni saqlash" })
        .hasAttribute("disabled"),
    ).toBe(true),
  );
  expect(
    fetchMock.mock.calls.some(([path]) => path === "/api/v1/receipts/"),
  ).toBe(false);
});

test("mobile viewport receipt form submission saves single batch and calculates unit price", async () => {
  localStorage.setItem("profur.language", "uz");
  const writes: RequestInit[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (path: string, init?: RequestInit) => {
      if (path === "/api/auth/me/") return response(user);
      if (path === "/api/v1/receipts/" && init?.method === "POST") {
        writes.push(init);
        return response({
          id: 77,
          quantity_on_hand_after: "15.00",
          quantity: "15.00",
          total_amount: "450.00",
          currency: "USD",
          unit_price: "30.000000",
          received_on: "2026-11-18",
          material,
        });
      }
      return baseFetch(path);
    }),
  );
  render(<App />);
  await screen.findByRole("option", { name: "MDF 18 mm · list" });
  fireEvent.change(screen.getByLabelText("Material"), {
    target: { value: "41" },
  });
  fireEvent.change(screen.getByLabelText("Miqdor"), {
    target: { value: "15" },
  });
  fireEvent.change(screen.getByLabelText("Jami summa"), {
    target: { value: "450.00" },
  });
  const saveBtn = screen.getByRole("button", { name: "Kirimni saqlash" });
  await userEvent.click(saveBtn);
  await screen.findByText(/Partiya #77/);
  expect(writes).toHaveLength(1);
  const payload = JSON.parse(String(writes[0].body));
  expect(payload.currency).toBe("USD");
  expect(payload.quantity).toBe("15");
  expect(payload.total_amount).toBe("450.00");
  expect(new Headers(writes[0].headers).get("Idempotency-Key")).toBeTruthy();
});

