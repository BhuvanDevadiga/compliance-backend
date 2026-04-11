import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import DashboardPage from "../Index";
import { apiPost, API_BASE_URL } from "./lib/api";

type LoginResponse = {
  access_token: string;
  token_type: string;
};

function LoginView(props: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await apiPost<LoginResponse>("/auth/login", {
        email,
        password,
      });
      props.onLogin(data.access_token);
    } catch (submitError: unknown) {
      setError(
        submitError instanceof Error ? submitError.message : "Login failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 420,
          background: "#ffffff",
          borderRadius: 20,
          padding: 28,
          boxShadow: "0 24px 60px rgba(15, 23, 42, 0.12)",
        }}
      >
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 30, fontWeight: 700, color: "#0f172a" }}>
            Sign In
          </div>
          <div style={{ color: "#64748b", marginTop: 8 }}>
            Connect to the backend at <code>{API_BASE_URL}</code>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "grid", gap: 14 }}>
          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 14, color: "#334155" }}>Email</span>
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              style={{
                padding: "12px 14px",
                borderRadius: 12,
                border: "1px solid #cbd5e1",
                outline: "none",
              }}
            />
          </label>

          <label style={{ display: "grid", gap: 6 }}>
            <span style={{ fontSize: 14, color: "#334155" }}>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              style={{
                padding: "12px 14px",
                borderRadius: 12,
                border: "1px solid #cbd5e1",
                outline: "none",
              }}
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: 6,
              padding: "12px 16px",
              borderRadius: 12,
              border: "none",
              background: "#2563eb",
              color: "#ffffff",
              fontWeight: 700,
              cursor: loading ? "wait" : "pointer",
            }}
          >
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>

        {error ? (
          <div style={{ marginTop: 14, color: "#dc2626", fontSize: 14 }}>
            {error}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem("token")
  );

  useEffect(() => {
    const handleLogout = () => {
      setToken(null);
    };

    window.addEventListener("auth:logout", handleLogout);
    return () => {
      window.removeEventListener("auth:logout", handleLogout);
    };
  }, []);

  function handleLogin(nextToken: string) {
    localStorage.setItem("token", nextToken);
    setToken(nextToken);
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  if (!token) {
    return <LoginView onLogin={handleLogin} />;
  }

  return (
    <main className="app-shell">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 20,
        }}
      >
        <div style={{ color: "#64748b", fontSize: 14 }}>
          Authenticated dashboard
        </div>
        <button
          type="button"
          onClick={handleLogout}
          style={{
            padding: "10px 14px",
            borderRadius: 12,
            border: "1px solid #cbd5e1",
            background: "#ffffff",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </div>
      <DashboardPage />
    </main>
  );
}
