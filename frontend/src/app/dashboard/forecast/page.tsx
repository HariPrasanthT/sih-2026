"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, ReferenceLine, Area, AreaChart,
} from "recharts";
import { ArrowRight, TrendingDown, Calendar, AlertCircle, Brain, Sparkles, Activity } from "lucide-react";
import { fetchFreightForecast, ForecastPoint } from "@/lib/api";

const generateData = () => {
  const data = [];
  const baseRate = 22;
  let rate = baseRate;
  const today = new Date(2026, 8, 1); // Sep 1 2026

  for (let i = -90; i <= 60; i++) {
    const d = new Date(today);
    d.setDate(d.getDate() + i);
    const label = `${d.getDate()} ${d.toLocaleString("default", { month: "short" })}`;
    const noise = (Math.random() - 0.5) * 1.2;
    rate = Math.max(14, Math.min(26, rate + noise - 0.05));

    const isHistory = i <= 0;
    data.push({
      date: label,
      historical: isHistory ? parseFloat(rate.toFixed(2)) : null,
      forecast: i >= -5 ? parseFloat((rate + (isHistory ? 0 : -0.08 * (i - 0))).toFixed(2)) : null,
      upperCI: !isHistory ? parseFloat((rate - 0.08 * (i - 0) + 1.5).toFixed(2)) : null,
      lowerCI: !isHistory ? parseFloat((rate - 0.08 * (i - 0) - 1.5).toFixed(2)) : null,
    });
  }
  return data;
};

const defaultData = generateData();

const defaultFactors = [
  { label: "Historical Freight Trend", impact: 85, color: "cyan" },
  { label: "Vessel Availability", impact: 70, color: "blue" },
  { label: "Seasonal Demand", impact: 60, color: "indigo" },
  { label: "Port Congestion (Paradip)", impact: 45, color: "amber" },
  { label: "Fuel Price (VLSFO)", impact: 55, color: "orange" },
  { label: "Route Conditions", impact: 30, color: "green" },
  { label: "Market Volatility", impact: 40, color: "red" },
];

const ranges = ["7D", "30D", "90D", "180D"];

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number | null; color: string }>; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-sky-200 rounded-xl p-3 text-xs shadow-xl shadow-sky-100/60">
        <p className="text-slate-500 mb-1.5 font-bold">{label}</p>
        {payload.map((p) => p.value !== null && (
          <p key={p.name} style={{ color: p.color }} className="font-bold text-xs py-0.5">
            {p.name}: ${Number(p.value).toFixed(2)}/MT
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function ForecastPage() {
  const router = useRouter();
  const [range, setRange] = useState("90D");
  const [chartData, setChartData] = useState<any[]>([]);
  const [currentRate, setCurrentRate] = useState<string>("$18.40");
  const [forecastRate, setForecastRate] = useState<string>("$17.10");
  const [trend, setTrend] = useState<string>("Bearish");
  const [optimalWindow, setOptimalWindow] = useState<string>("10–24 Sep");
  const [confidence, setConfidence] = useState<string>("91.4%");
  const [insight, setInsight] = useState<string>(
    "Freight rates are showing a softening trend. Panamax availability remains favorable. Paradip congestion is expected to increase moderately over the next 14 days."
  );
  const [factors, setFactors] = useState(defaultFactors);
  const [isLive, setIsLive] = useState<boolean>(false);

  useEffect(() => {
    const daysMap: Record<string, number> = { "7D": 7, "30D": 30, "90D": 90, "180D": 180 };
    const days = daysMap[range] || 90;

    let isMounted = true;
    fetchFreightForecast("Newcastle", "Paradip", days)
      .then((res: any) => {
        if (!isMounted) return;
        if (res && (res.points || res.data)) {
          const pts = res.points || res.data;
          setChartData(pts);
          if (res.current_rate) setCurrentRate(`$${Number(res.current_rate).toFixed(2)}`);
          if (res.forecast_30d) setForecastRate(`$${Number(res.forecast_30d).toFixed(2)}`);
          if (res.trend) setTrend(res.trend);
          if (res.optimal_window) setOptimalWindow(res.optimal_window);
          if (res.confidence_score || res.confidence_pct) {
            setConfidence(`${res.confidence_score || res.confidence_pct}%`);
          }
          if (res.factors && res.factors.length > 0) setFactors(res.factors);
          if (res.insight) setInsight(res.insight);
          setIsLive(true);
        }
      })
      .catch((err) => {
        console.warn("Using fallback forecast data:", err);
        // Fallback slice
        const sliceCount = range === "7D" ? 7 : range === "30D" ? 30 : range === "90D" ? 90 : 150;
        const midIndex = defaultData.findIndex(d => d.historical !== null && d.forecast !== null);
        const start = Math.max(0, midIndex - sliceCount * 0.6);
        setChartData(defaultData.slice(Math.floor(start), Math.floor(start) + sliceCount));
      });

    return () => {
      isMounted = false;
    };
  }, [range]);

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="AI Freight Rate Forecast" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">AI Freight Rate Forecast</h1>
            <p className="text-slate-500 text-sm mt-1">Newcastle → Paradip • Panamax • AI-Powered Predictive Model</p>
          </div>
          {isLive && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live API Model Feed</span>
            </div>
          )}
        </div>

        {/* KPI Strip */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { label: "Current Rate", value: currentRate, sub: "/ MT", color: "text-slate-900" },
            { label: "Forecast Rate", value: forecastRate, sub: "/ MT", color: "text-emerald-600" },
            { label: "Trend", value: trend, sub: "Softening", color: "text-emerald-600" },
            { label: "Optimal Entry", value: optimalWindow, sub: "Window", color: "text-sky-600" },
            { label: "Confidence", value: confidence, sub: "AI Score", color: "text-sky-700" },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-white border border-sky-100 rounded-2xl p-4 shadow-sm">
              <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">{kpi.label}</p>
              <p className={`text-2xl font-black ${kpi.color}`}>{kpi.value}</p>
              <p className="text-xs text-slate-400 font-medium mt-0.5">{kpi.sub}</p>
            </div>
          ))}
        </div>

        {/* Chart */}
        <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl border border-emerald-100">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Freight Rate History & Forecast</h3>
                <p className="text-xs text-slate-400">Historical Baltic & fixture rates vs machine learning trajectory</p>
              </div>
            </div>
            <div className="flex gap-1 bg-slate-50 p-1 rounded-xl border border-slate-200">
              {ranges.map((r) => (
                <button
                  key={r}
                  onClick={() => setRange(r)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                    range === r ? "bg-white text-sky-700 shadow-sm border border-sky-200" : "text-slate-500 hover:text-slate-800"
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="histGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="foreGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={{ stroke: "#e2e8f0" }} interval="preserveStartEnd" />
              <YAxis tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} domain={["auto", "auto"]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "12px", color: "#64748b" }} />
              <Area type="monotone" dataKey="upperCI" stroke="transparent" fill="#10b98115" name="Confidence Band" />
              <Area type="monotone" dataKey="lowerCI" stroke="transparent" fill="#10b98115" />
              <Area type="monotone" dataKey="historical" stroke="#0ea5e9" fill="url(#histGrad)" strokeWidth={2.5} dot={false} name="Historical Rate" />
              <Area type="monotone" dataKey="forecast" stroke="#10b981" fill="url(#foreGrad)" strokeWidth={2.5} dot={false} strokeDasharray="6 3" name="AI Forecast" />
              <ReferenceLine x="1 Sep" stroke="#f59e0b" strokeDasharray="4 2" label={{ value: "Today", fill: "#d97706", fontSize: 11, fontWeight: "bold" }} />
              <ReferenceLine x="10 Sep" stroke="#0284c7" strokeDasharray="4 2" label={{ value: "Entry", fill: "#0284c7", fontSize: 11, fontWeight: "bold" }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* AI Explanation */}
        <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 bg-sky-50 text-sky-600 rounded-xl border border-sky-100">
              <Brain className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">Why This Forecast?</h3>
          </div>
          <div className="space-y-3">
            {factors.map((f) => (
              <div key={f.label} className="flex items-center gap-4">
                <p className="text-sm text-slate-600 font-medium w-56 shrink-0">{f.label}</p>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-sky-500 to-blue-600 transition-all"
                    style={{ width: `${f.impact}%` }}
                  />
                </div>
                <span className="text-xs text-slate-700 font-bold w-10 text-right">{f.impact}%</span>
              </div>
            ))}
          </div>
          <div className="mt-5 p-4 rounded-xl bg-amber-50 border border-amber-200 flex gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <p className="text-sm text-slate-700 leading-relaxed">
              {insight} <strong className="text-sky-700 font-bold">Optimal entry window: {optimalWindow} 2026</strong>.
            </p>
          </div>
        </div>

        {/* Action */}
        <div className="pb-8">
          <button
            onClick={() => router.push("/dashboard/strategy")}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            Continue to Charter Strategy <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </main>
    </div>
  );
}
