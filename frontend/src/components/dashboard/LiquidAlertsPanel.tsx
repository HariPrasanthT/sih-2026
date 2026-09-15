"use client";

import React, { useState } from "react";
import { AlertTriangle, ShieldCheck, AlertCircle, Bell, Clock, ChevronRight, Waves, Flame } from "lucide-react";

export interface MaritimeAlert {
  id: string;
  type: "critical" | "elevated" | "watch" | "stable";
  category: "Port Risk" | "Market Alert" | "Fuel / Bunker" | "Weather / Swell";
  title: string;
  description: string;
  timestamp: string;
  impact: string;
  metric?: string;
}

const initialAlerts: MaritimeAlert[] = [
  {
    id: "1",
    type: "critical",
    category: "Port Risk",
    title: "Paradip Port Congestion Surge",
    description: "Iron ore & coal berth waiting times lengthened to 2.4 days due to heavy inbound arrivals.",
    timestamp: "12m ago",
    impact: "+$14,200 Demurrage Risk",
    metric: "72% Congestion Index",
  },
  {
    id: "2",
    type: "watch",
    category: "Market Alert",
    title: "Panamax Spot Rates Softening",
    description: "Australia to East Coast India tonnage supply increased by 4 vessels. Spot rates dropped by 3.2%.",
    timestamp: "38m ago",
    impact: "Favourable for 10–18 Sep Laycan",
    metric: "-$0.55 / MT",
  },
  {
    id: "3",
    type: "elevated",
    category: "Weather / Swell",
    title: "Bay of Bengal Monsoon Swell",
    description: "Monsoon swell wave height exceeding 3.8m expected between 14–18 Sep off Andhra/Odisha coast.",
    timestamp: "1h ago",
    impact: "Potential 6h transit delay",
    metric: "Wave Height 3.8m",
  },
  {
    id: "4",
    type: "stable",
    category: "Fuel / Bunker",
    title: "VLSFO Fuel Price Spread Singapore",
    description: "Very Low Sulphur Fuel Oil bunkering rates stabilized at $540/MT at Singapore hub.",
    timestamp: "3h ago",
    impact: "Voyage cost baseline maintained",
    metric: "$540 / MT",
  },
];

export default function LiquidAlertsPanel() {
  const [filter, setFilter] = useState<string>("all");

  const badgeStyles = {
    critical: {
      border: "border-red-200",
      bg: "bg-red-50",
      text: "text-red-600",
      dot: "bg-red-500",
      icon: <AlertCircle className="w-3.5 h-3.5 text-red-500" />,
    },
    elevated: {
      border: "border-amber-200",
      bg: "bg-amber-50",
      text: "text-amber-700",
      dot: "bg-amber-500",
      icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />,
    },
    watch: {
      border: "border-sky-200",
      bg: "bg-sky-50",
      text: "text-sky-700",
      dot: "bg-sky-500",
      icon: <Bell className="w-3.5 h-3.5 text-sky-500" />,
    },
    stable: {
      border: "border-emerald-200",
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      dot: "bg-emerald-500",
      icon: <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />,
    },
  };

  const filtered = filter === "all" ? initialAlerts : initialAlerts.filter((a) => a.type === filter);

  return (
    <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm relative overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
          </span>
          <h3 className="text-sm font-bold text-slate-900 tracking-wide uppercase">Live Maritime Alerts</h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200">
            {initialAlerts.length} Active Feeds
          </span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-[11px]">
          {["all", "critical", "elevated", "watch", "stable"].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilter(lvl)}
              className={`px-2.5 py-0.5 rounded capitalize font-medium transition-all ${
                filter === lvl
                  ? "bg-white text-sky-700 border border-sky-200 shadow-sm"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Alert Cards List */}
      <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
        {filtered.map((alert) => {
          const style = badgeStyles[alert.type];
          return (
            <div
              key={alert.id}
              className={`group relative p-3.5 rounded-xl border hover:border-sky-300 hover:shadow-md transition-all duration-200 cursor-pointer ${style.border} ${style.bg}`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-2.5">
                  <div className="mt-0.5 shrink-0">{style.icon}</div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                      {alert.category}
                    </span>
                    <span className="text-slate-400">·</span>
                    <span className="text-[10px] text-slate-400 font-mono">{alert.timestamp}</span>
                    </div>
                    <h4 className="text-xs font-bold text-slate-900 mt-0.5">{alert.title}</h4>
                    <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">{alert.description}</p>
                  </div>
                </div>

                {alert.metric && (
                  <div className="text-right shrink-0">
                    <span className={`text-[11px] font-mono font-bold ${style.text}`}>
                      {alert.metric}
                    </span>
                    <p className="text-[10px] text-slate-400 mt-0.5">{alert.impact}</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
