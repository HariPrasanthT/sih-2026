"use client";

import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import { ArrowRight, Brain, BarChart2, ShieldCheck, AlertTriangle } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";

const risks = [
  { name: "Freight Market Risk", level: "Medium", score: 55, color: "#d97706" },
  { name: "Port Congestion Risk", level: "Medium", score: 60, color: "#d97706" },
  { name: "Vessel Availability Risk", level: "Low", score: 25, color: "#059669" },
  { name: "Idle Time Risk", level: "Medium", score: 50, color: "#d97706" },
  { name: "Weather Risk", level: "Low", score: 20, color: "#059669" },
  { name: "Demurrage Risk", level: "Medium", score: 58, color: "#d97706" },
  { name: "Fuel Price Risk", level: "Low", score: 35, color: "#059669" },
  { name: "Route Risk", level: "Low", score: 15, color: "#059669" },
];

const idleData = [
  { port: "Paradip", current: 2.5, predicted: 3.8 },
  { port: "Dhamra", current: 0.5, predicted: 0.6 },
  { port: "Vizag", current: 5.2, predicted: 6.1 },
  { port: "Gangavaram", current: 0.8, predicted: 0.9 },
];

const aiBreakdown = [
  { label: "Freight Forecast", value: 85, color: "#0284c7" },
  { label: "Port Compatibility", value: 92, color: "#059669" },
  { label: "Vessel Availability", value: 94, color: "#059669" },
  { label: "Idle Risk", value: 68, color: "#d97706" },
  { label: "Total Cost", value: 80, color: "#0284c7" },
  { label: "Contract Economics", value: 84, color: "#0284c7" },
  { label: "Market Risk", value: 72, color: "#d97706" },
  { label: "Confidence Score", value: 86, color: "#059669" },
];

function RiskBar({ risk }: { risk: typeof risks[0] }) {
  return (
    <div className="flex items-center gap-4">
      <p className="text-sm text-slate-700 font-medium w-52 shrink-0">{risk.name}</p>
      <div className="flex-1 h-2.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${risk.score}%`, background: risk.color }}
        />
      </div>
      <span
        className="text-xs font-bold w-16 text-right"
        style={{ color: risk.color }}
      >
        {risk.level}
      </span>
    </div>
  );
}

export default function RiskPage() {
  const router = useRouter();

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Risk & Operational Analysis" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Risk & Operational Analysis</h1>
          <p className="text-slate-500 text-sm mt-1">Comprehensive risk intelligence for the recommended charter decision.</p>
        </div>

        {/* Risk Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-5">
              <div className="p-2 bg-amber-50 text-amber-600 rounded-xl border border-amber-100">
                <BarChart2 className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">Risk Factor Analysis</h3>
            </div>
            <div className="space-y-3.5">
              {risks.map((r) => <RiskBar key={r.name} risk={r} />)}
            </div>
          </div>

          {/* Idle Time Prediction */}
          <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Idle Time Prediction (Days)</h3>
            <p className="text-xs text-slate-400 mb-5">Current vs Predicted port waiting times</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={idleData} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="port" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: "#ffffff", border: "1px solid #e0f2fe", borderRadius: "12px", boxShadow: "0 8px 24px rgba(14,165,233,0.1)" }}
                  labelStyle={{ color: "#0f172a", fontWeight: "bold" }}
                />
                <Bar dataKey="current" name="Current" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="predicted" name="Predicted" radius={[4, 4, 0, 0]}>
                  {idleData.map((d) => (
                    <Cell key={d.port} fill={d.predicted > 3 ? "#dc2626" : d.predicted > 1 ? "#d97706" : "#059669"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-3 mt-4">
              {[
                { label: "Expected Idle Time (Paradip)", value: "2.5 Days", color: "text-amber-600" },
                { label: "Predicted Congestion", value: "Increasing", color: "text-amber-600" },
                { label: "Demurrage Exposure", value: "$45K–$80K", color: "text-amber-600" },
                { label: "Delay Probability", value: "38%", color: "text-amber-600" },
              ].map((m) => (
                <div key={m.label} className="bg-slate-50 border border-slate-100 rounded-xl p-3">
                  <p className="text-xs text-slate-500 font-medium">{m.label}</p>
                  <p className={`text-lg font-bold ${m.color} mt-0.5`}>{m.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Recommendation Breakdown */}
        <div className="bg-gradient-to-br from-sky-50 to-blue-50 border border-sky-200 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-white text-sky-600 rounded-xl shadow-sm border border-sky-100">
              <Brain className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-black text-sky-800 uppercase tracking-wider">Why This Recommendation?</h3>
              <p className="text-xs text-slate-500 mt-0.5">AI confidence breakdown across all decision factors</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {aiBreakdown.map((item) => (
              <div key={item.label} className="flex items-center gap-4 bg-white/70 p-3 rounded-xl border border-sky-100">
                <p className="text-sm text-slate-700 font-medium w-44 shrink-0">{item.label}</p>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${item.value}%`, background: item.color }} />
                </div>
                <span className="text-xs font-bold w-10 text-right" style={{ color: item.color }}>{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Action */}
        <div className="pb-8">
          <button
            onClick={() => router.push("/dashboard/report")}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            Generate Charter Report <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </main>
    </div>
  );
}
