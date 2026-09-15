"use client";

import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import { ArrowRight, Star, CheckCircle, AlertTriangle, Brain, TrendingDown } from "lucide-react";
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from "recharts";

const strategies = [
  {
    type: "SPOT",
    cost: "$10.2M",
    risk: "High",
    riskColor: "text-red-600",
    aiScore: 62,
    scoreColor: "text-red-600",
    flexibility: "Maximum",
    voyages: "1",
    savings: "—",
    description: "Single voyage at current market rate. Full exposure to rate volatility.",
    badge: null,
  },
  {
    type: "SHORT-TERM",
    cost: "$9.7M",
    risk: "Medium",
    riskColor: "text-amber-600",
    aiScore: 84,
    scoreColor: "text-sky-600",
    flexibility: "High",
    voyages: "3–6",
    savings: "$500K",
    description: "Multi-voyage contract over 6–12 months. Optimal balance of cost and flexibility.",
    badge: "RECOMMENDED",
  },
  {
    type: "MEDIUM-TERM",
    cost: "$9.4M",
    risk: "Low",
    riskColor: "text-emerald-600",
    aiScore: 91,
    scoreColor: "text-emerald-600",
    flexibility: "Medium",
    voyages: "12+",
    savings: "$800K",
    description: "Long-term contract lock-in. Lowest cost but reduced market flexibility.",
    badge: null,
  },
];

const radarData = [
  { factor: "Cost", SPOT: 40, "SHORT-TERM": 75, "MEDIUM-TERM": 90 },
  { factor: "Flexibility", SPOT: 100, "SHORT-TERM": 75, "MEDIUM-TERM": 45 },
  { factor: "Risk Control", SPOT: 30, "SHORT-TERM": 70, "MEDIUM-TERM": 90 },
  { factor: "Savings", SPOT: 20, "SHORT-TERM": 70, "MEDIUM-TERM": 90 },
  { factor: "Reliability", SPOT: 50, "SHORT-TERM": 80, "MEDIUM-TERM": 95 },
];

export default function StrategyPage() {
  const router = useRouter();

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Spot vs Contract Strategy" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Charter Strategy Comparison</h1>
          <p className="text-slate-500 text-sm mt-1">Newcastle → Paradip • 80,000 MT Coal • MV Pacific Voyager</p>
        </div>

        {/* Strategy Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {strategies.map((s) => (
            <div
              key={s.type}
              className={`relative bg-white border rounded-2xl p-6 transition-all ${
                s.badge
                  ? "border-sky-500 shadow-md shadow-sky-100 ring-2 ring-sky-500/20"
                  : "border-sky-100 hover:border-sky-300 shadow-sm"
              }`}
            >
              {s.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-sky-500 to-blue-600 text-white text-[10px] font-black uppercase tracking-widest shadow-sm">
                    <Star className="w-3 h-3 fill-white" /> {s.badge}
                  </span>
                </div>
              )}

              <h3 className="text-lg font-black text-slate-900 mb-1 mt-2">{s.type}</h3>
              <p className="text-3xl font-black text-slate-900 mb-1">{s.cost}</p>
              <p className="text-xs text-slate-400 font-semibold mb-4">Expected Total Cost</p>

              <div className="space-y-2.5 mb-5 bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                {[
                  { label: "Risk", value: s.risk, cls: s.riskColor },
                  { label: "AI Score", value: `${s.aiScore} / 100`, cls: s.scoreColor },
                  { label: "Flexibility", value: s.flexibility, cls: "text-slate-700 font-medium" },
                  { label: "Voyages Covered", value: s.voyages, cls: "text-slate-700 font-medium" },
                  { label: "Expected Savings vs Spot", value: s.savings, cls: "text-emerald-600 font-bold" },
                ].map((row) => (
                  <div key={row.label} className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 font-medium">{row.label}</span>
                    <span className={`font-semibold ${row.cls}`}>{row.value}</span>
                  </div>
                ))}
              </div>

              {/* Score Bar */}
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-4">
                <div
                  className={`h-full rounded-full ${s.aiScore >= 80 ? "bg-gradient-to-r from-sky-500 to-emerald-500" : s.aiScore >= 60 ? "bg-amber-500" : "bg-red-500"}`}
                  style={{ width: `${s.aiScore}%` }}
                />
              </div>

              <p className="text-xs text-slate-500 leading-relaxed">{s.description}</p>
            </div>
          ))}
        </div>

        {/* Radar Chart & AI Recommendation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4">Strategy Factor Comparison</h3>
            <ResponsiveContainer width="100%" height={280}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="factor" tick={{ fill: "#64748b", fontSize: 11 }} />
                <Radar name="SPOT" dataKey="SPOT" stroke="#ef4444" fill="#ef4444" fillOpacity={0.12} />
                <Radar name="SHORT-TERM" dataKey="SHORT-TERM" stroke="#0284c7" fill="#0284c7" fillOpacity={0.2} />
                <Radar name="MEDIUM-TERM" dataKey="MEDIUM-TERM" stroke="#10b981" fill="#10b981" fillOpacity={0.15} />
              </RadarChart>
            </ResponsiveContainer>
            <div className="flex gap-6 justify-center mt-2">
              {[{ color: "#ef4444", label: "SPOT" }, { color: "#0284c7", label: "SHORT-TERM" }, { color: "#10b981", label: "MEDIUM-TERM" }].map(l => (
                <span key={l.label} className="flex items-center gap-1.5 text-xs text-slate-600 font-semibold">
                  <span className="w-3 h-1 rounded-full inline-block" style={{ background: l.color }} />
                  {l.label}
                </span>
              ))}
            </div>
          </div>

          {/* AI Recommendation */}
          <div className="bg-gradient-to-br from-sky-50 to-blue-50 border border-sky-200 rounded-2xl p-6 flex flex-col justify-between shadow-sm">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-white rounded-xl shadow-sm text-sky-600 border border-sky-100">
                  <Brain className="w-5 h-5" />
                </div>
                <p className="text-xs font-black text-sky-800 uppercase tracking-wider">AI Recommendation</p>
              </div>
              <p className="text-2xl font-black text-slate-900 mb-2">SHORT-TERM MULTI-VOYAGE</p>
              <p className="text-slate-600 text-sm leading-relaxed mb-4">
                Provides the best balance between cost savings, market flexibility and operational risk. Current softening freight trend makes short-term contracts advantageous over locking into medium-term.
              </p>
              <div className="space-y-2 bg-white/70 p-4 rounded-xl border border-sky-100">
                {[
                  { icon: <CheckCircle className="w-4 h-4 text-emerald-600" />, text: "Saves $500K vs Spot chartering" },
                  { icon: <CheckCircle className="w-4 h-4 text-emerald-600" />, text: "Retains flexibility as rates soften further" },
                  { icon: <TrendingDown className="w-4 h-4 text-sky-600" />, text: "Optimal entry window: 10–24 Sep" },
                  { icon: <AlertTriangle className="w-4 h-4 text-amber-500" />, text: "Medium risk — manageable with current vessel choice" },
                ].map((p, i) => (
                  <div key={i} className="flex items-start gap-2.5 text-sm text-slate-700">
                    <div className="shrink-0 mt-0.5">{p.icon}</div>
                    <p className="font-medium text-xs">{p.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action */}
        <div className="pb-8">
          <button
            onClick={() => router.push("/dashboard/risk")}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            Continue to Risk Analysis <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </main>
    </div>
  );
}
