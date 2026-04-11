import { useEffect, useMemo, useState } from "react";
import { apiGet } from "./src/lib/api";

type SummaryResponse = {
  tenant_id: string;
  audit_readiness: number;
  average_risk: number;
  total_controls: number;
  distribution: {
    high: number;
    medium: number;
    low: number;
  };
};

type DistributionResponse = {
  tenant_id: string;
  distribution: {
    high: number;
    medium: number;
    low: number;
  };
};

type TrendResponseItem = {
  risk_score: number;
  created_at: string;
};

type InsightsResponse = {
  tenant_id: string;
  items: string[];
};

type DistributionItem = {
  name: "High" | "Medium" | "Low";
  value: number;
  color: string;
};

const COLORS: Record<DistributionItem["name"], string> = {
  High: "#ef4444",
  Medium: "#f59e0b",
  Low: "#22c55e",
};

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function StatCard(props: { title: string; value: string | number }) {
  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: 14,
        padding: 16,
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.07)",
        border: "1px solid #e2e8f0",
      }}
    >
      <div style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>{props.title}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: "#0f172a", lineHeight: 1.2 }}>
        {props.value}
      </div>
    </div>
  );
}

function DistributionBars({ items }: { items: DistributionItem[] }) {
  const maxValue = Math.max(...items.map((item) => item.value), 1);

  return (
    <div style={{ display: "grid", gap: 14 }}>
      {items.map((item) => (
        <div
          key={item.name}
          style={{
            display: "grid",
            gridTemplateColumns: "88px 1fr 34px",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span style={{ color: "#334155", fontWeight: 600, fontSize: 13 }}>{item.name}</span>
          <div
            style={{
              height: 12,
              background: "#e2e8f0",
              borderRadius: 999,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${(item.value / maxValue) * 100}%`,
                height: "100%",
                background: item.color,
                borderRadius: 999,
              }}
            />
          </div>
          <span style={{ color: "#0f172a", fontWeight: 700, fontSize: 13 }}>{item.value}</span>
        </div>
      ))}
    </div>
  );
}

function TrendChart({ points }: { points: TrendResponseItem[] }) {
  if (points.length === 0) {
    return <div style={{ color: "#64748b" }}>No trend data available yet.</div>;
  }

  const width = 560;
  const height = 210;
  const padding = 24;
  const minY = 0;
  const maxY = 1;

  const chartPoints = points.map((point, index) => {
    const x =
      padding +
      (index * (width - padding * 2)) / Math.max(points.length - 1, 1);
    const normalizedY = (point.risk_score - minY) / Math.max(maxY - minY, 0.0001);
    const y = height - padding - normalizedY * (height - padding * 2);
    return {
      x,
      y,
      label: new Date(point.created_at).toLocaleDateString(),
      value: point.risk_score,
    };
  });

  const pathData = chartPoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  return (
    <div style={{ width: "100%" }}>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: "100%", height: "auto" }}>
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#cbd5e1" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#cbd5e1" />
        <path d={pathData} fill="none" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" />
        {chartPoints.map((point) => (
          <g key={`${point.label}-${point.value}`}>
            <circle cx={point.x} cy={point.y} r="3.5" fill="#2563eb" />
          </g>
        ))}
      </svg>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${chartPoints.length}, minmax(0, 1fr))`,
          gap: 8,
          marginTop: 10,
          fontSize: 11,
          color: "#64748b",
        }}
      >
        {chartPoints.map((point) => (
          <div key={point.label} style={{ textAlign: "center" }}>
            {point.label}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [distribution, setDistribution] = useState<DistributionResponse | null>(null);
  const [trend, setTrend] = useState<TrendResponseItem[]>([]);
  const [insights, setInsights] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    Promise.all([
      apiGet<SummaryResponse>("/dashboard/summary"),
      apiGet<DistributionResponse>("/dashboard/distribution"),
      apiGet<TrendResponseItem[]>("/dashboard/trend"),
      apiGet<InsightsResponse>("/insights"),
    ])
      .then(([summaryResponse, distributionResponse, trendResponse, insightsResponse]) => {
        if (!mounted) {
          return;
        }

        setSummary(summaryResponse);
        setDistribution(distributionResponse);
        setTrend(trendResponse);
        setInsights(insightsResponse.items);
      })
      .catch((fetchError: unknown) => {
        if (!mounted) {
          return;
        }

        const message =
          fetchError instanceof Error ? fetchError.message : "Failed to load dashboard";
        setError(message);
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const distributionItems = useMemo<DistributionItem[]>(() => {
    if (!distribution) {
      return [];
    }

    return [
      { name: "High", value: distribution.distribution.high, color: COLORS.High },
      { name: "Medium", value: distribution.distribution.medium, color: COLORS.Medium },
      { name: "Low", value: distribution.distribution.low, color: COLORS.Low },
    ];
  }, [distribution]);

  if (loading) {
    return <div style={{ padding: 32, color: "#64748b" }}>Loading dashboard...</div>;
  }

  if (error) {
    return <div style={{ padding: 32, color: "#dc2626" }}>{error}</div>;
  }

  return (
    <div style={{ display: "grid", gap: 24 }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, color: "#0f172a", margin: 0 }}>Dashboard</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 14,
        }}
      >
        <StatCard title="Audit Readiness" value={summary ? formatPercent(summary.audit_readiness) : "--"} />
        <StatCard title="Average Risk" value={summary ? formatPercent(summary.average_risk) : "--"} />
        <StatCard title="Total Controls" value={summary?.total_controls ?? "--"} />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: 16,
          alignItems: "start",
        }}
      >
        <div
          style={{
            background: "#ffffff",
            borderRadius: 14,
            padding: 20,
            boxShadow: "0 8px 24px rgba(15, 23, 42, 0.07)",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ margin: "0 0 14px", fontSize: 17, color: "#0f172a" }}>Risk Distribution</h2>
          <DistributionBars items={distributionItems} />
        </div>

        <div
          style={{
            background: "#ffffff",
            borderRadius: 14,
            padding: 20,
            boxShadow: "0 8px 24px rgba(15, 23, 42, 0.07)",
            border: "1px solid #e2e8f0",
          }}
        >
          <h2 style={{ margin: "0 0 14px", fontSize: 17, color: "#0f172a" }}>Risk Trend</h2>
          <TrendChart points={trend} />
        </div>
      </div>

      <div
        style={{
          background: "#ffffff",
          borderRadius: 14,
          padding: 20,
          boxShadow: "0 8px 24px rgba(15, 23, 42, 0.07)",
          border: "1px solid #e2e8f0",
        }}
      >
        <h2 style={{ margin: "0 0 14px", fontSize: 17, color: "#0f172a" }}>Insights</h2>
        {insights.length === 0 ? (
          <div style={{ color: "#64748b", fontSize: 14 }}>No insights available.</div>
        ) : (
          <ul style={{ margin: 0, paddingLeft: 18, color: "#334155", display: "grid", gap: 8, fontSize: 14 }}>
            {insights.map((insight, index) => (
              <li key={`${index}-${insight}`}>{insight}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
