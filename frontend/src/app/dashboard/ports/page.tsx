"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import { ArrowRight, CheckCircle, AlertTriangle, XCircle } from "lucide-react";
import { fetchPorts, PortData } from "@/lib/api";

interface ApiPortItem extends Partial<PortData> {
  port_name?: string;
  max_draft_m?: number;
  max_loa_m?: number;
  max_beam_m?: number;
  avg_turnaround_days?: number;
}

const defaultPorts = [
  {
    name: "Paradip", state: "Odisha", congestion: "Moderate", berth: "72%", waiting: "2–3 Days",
    maxDraft: "14.2m", maxLOA: "225m", maxBeam: "32m", handling: "12 MT/hr",
    predictedCongestion: "Increasing", action: "Monitor", risk: "medium",
  },
  {
    name: "Dhamra", state: "Odisha", congestion: "Low", berth: "45%", waiting: "0–1 Day",
    maxDraft: "16.5m", maxLOA: "300m", maxBeam: "50m", handling: "15 MT/hr",
    predictedCongestion: "Stable", action: "Proceed", risk: "low",
  },
  {
    name: "Visakhapatnam", state: "Andhra Pradesh", congestion: "High", berth: "88%", waiting: "5–7 Days",
    maxDraft: "14.0m", maxLOA: "220m", maxBeam: "32m", handling: "10 MT/hr",
    predictedCongestion: "High", action: "Avoid", risk: "high",
  },
  {
    name: "Gangavaram", state: "Andhra Pradesh", congestion: "Low", berth: "50%", waiting: "0–1 Day",
    maxDraft: "18.0m", maxLOA: "350m", maxBeam: "60m", handling: "18 MT/hr",
    predictedCongestion: "Stable", action: "Recommended", risk: "low",
  },
  {
    name: "Gopalpur", state: "Odisha", congestion: "Low", berth: "38%", waiting: "0–1 Day",
    maxDraft: "12.0m", maxLOA: "180m", maxBeam: "28m", handling: "8 MT/hr",
    predictedCongestion: "Stable", action: "Limited Capacity", risk: "low",
  },
  {
    name: "Haldia", state: "West Bengal", congestion: "High", berth: "91%", waiting: "6–8 Days",
    maxDraft: "8.5m", maxLOA: "180m", maxBeam: "28m", handling: "8 MT/hr",
    predictedCongestion: "Very High", action: "Avoid", risk: "high",
  },
];

// Vessel x Port compatibility matrix
const vessels = ["Pacific Voyager", "Eastern Star", "Atlas Pride", "Cape Meridian"];
const compatibility: Record<string, Record<string, "compatible" | "restricted" | "incompatible">> = {
  "Pacific Voyager": { "Paradip": "compatible", "Dhamra": "compatible", "Visakhapatnam": "compatible", "Gangavaram": "compatible", "Gopalpur": "restricted", "Haldia": "incompatible" },
  "Eastern Star": { "Paradip": "compatible", "Dhamra": "compatible", "Visakhapatnam": "compatible", "Gangavaram": "compatible", "Gopalpur": "restricted", "Haldia": "incompatible" },
  "Atlas Pride": { "Paradip": "compatible", "Dhamra": "compatible", "Visakhapatnam": "compatible", "Gangavaram": "compatible", "Gopalpur": "compatible", "Haldia": "restricted" },
  "Cape Meridian": { "Paradip": "restricted", "Dhamra": "compatible", "Visakhapatnam": "restricted", "Gangavaram": "compatible", "Gopalpur": "incompatible", "Haldia": "incompatible" },
};

const riskBadge: Record<string, string> = {
  low: "text-emerald-700 bg-emerald-50 border-emerald-200",
  medium: "text-amber-700 bg-amber-50 border-amber-200",
  high: "text-red-700 bg-red-50 border-red-200",
};

const compatIcon: Record<string, React.ReactNode> = {
  compatible: <CheckCircle className="w-4 h-4 text-emerald-600" />,
  restricted: <AlertTriangle className="w-4 h-4 text-amber-500" />,
  incompatible: <XCircle className="w-4 h-4 text-red-500" />,
};

export default function PortsPage() {
  const router = useRouter();
  const [ports, setPorts] = useState(defaultPorts);
  const [selected, setSelected] = useState("Paradip");
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    let isMounted = true;
    fetchPorts()
      .then((apiPorts) => {
        if (!isMounted || !apiPorts || apiPorts.length === 0) return;
        const mapped = (apiPorts as ApiPortItem[]).map((p: ApiPortItem) => {
          const pName = p.name || p.port_name || "Unknown Port";
          const state = pName.includes("Paradip") || pName.includes("Dhamra") || pName.includes("Gopalpur")
            ? "Odisha"
            : pName.includes("Haldia")
            ? "West Bengal"
            : "Andhra Pradesh";
          const level = (p.current_congestion_level || "low").toLowerCase();
          const risk = level === "high" ? "high" : level === "moderate" ? "medium" : "low";
          const action = risk === "high" ? "Avoid" : risk === "medium" ? "Monitor" : "Proceed";
          const berth = risk === "high" ? "88%" : risk === "medium" ? "72%" : "48%";

          const maxDraft = p.draft_max_m ?? p.max_draft_m ?? 14.5;
          const maxLOA = p.loa_max_m ?? p.max_loa_m ?? 230;
          const maxBeam = p.beam_max_m ?? p.max_beam_m ?? 32.2;
          const waitingDays = p.average_waiting_days ?? p.avg_turnaround_days ?? 2.1;
          const handling = p.daily_handling_capacity_mt
            ? `${Math.round(p.daily_handling_capacity_mt / 3500)} MT/hr`
            : "3,200 MT/hr";

          return {
            name: pName,
            state,
            congestion: level.charAt(0).toUpperCase() + level.slice(1),
            berth,
            waiting: `${waitingDays} Days`,
            maxDraft: `${maxDraft}m`,
            maxLOA: `${maxLOA}m`,
            maxBeam: `${maxBeam}m`,
            handling,
            predictedCongestion: risk === "high" ? "High" : risk === "medium" ? "Increasing" : "Stable",
            action,
            risk: risk as "low" | "medium" | "high",
          };
        });
        setPorts(mapped);
        setIsLive(true);
      })
      .catch((err) => {
        console.warn("Using default ports list:", err);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const port = ports.find((p) => p.name === selected) || ports[0];

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Port Compatibility Intelligence" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Port Compatibility Intelligence</h1>
            <p className="text-slate-500 text-sm mt-1">East Coast India port analysis for MV Pacific Voyager (Draft: 14.2m, LOA: 225m)</p>
          </div>
          {isLive && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Live Port Limits API</span>
            </div>
          )}
        </div>

        {/* Port Selector Tabs */}
        <div className="flex flex-wrap gap-2">
          {ports.map((p) => (
            <button
              key={p.name}
              onClick={() => setSelected(p.name)}
              className={`px-4 py-2.5 rounded-xl text-sm font-semibold border transition-all flex items-center gap-2 ${
                selected === p.name
                  ? "bg-gradient-to-r from-sky-500 to-blue-600 border-sky-500 text-white shadow-sm shadow-sky-200"
                  : "bg-white border-slate-200 text-slate-700 hover:border-sky-300 hover:bg-sky-50 shadow-sm"
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${selected === p.name ? "bg-white" : p.risk === "low" ? "bg-emerald-500" : p.risk === "medium" ? "bg-amber-500" : "bg-red-500"}`} />
              {p.name}
            </button>
          ))}
        </div>

        {/* Selected Port Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-sky-100 rounded-2xl p-6 space-y-4 shadow-sm">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold text-slate-900">{port.name} Port</h3>
                <p className="text-slate-500 text-sm font-medium">{port.state}, India</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${riskBadge[port.risk]}`}>
                {port.risk.toUpperCase()} RISK
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              {[
                { label: "Congestion", value: port.congestion },
                { label: "Berth Utilization", value: port.berth },
                { label: "Avg. Waiting Time", value: port.waiting },
                { label: "Max Draft", value: port.maxDraft },
                { label: "Max LOA", value: port.maxLOA },
                { label: "Max Beam", value: port.maxBeam },
                { label: "Cargo Handling", value: port.handling },
                { label: "Predicted Congestion", value: port.predictedCongestion },
              ].map((item) => (
                <div key={item.label} className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">{item.label}</p>
                  <p className="text-sm font-bold text-slate-800 mt-0.5">{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Action */}
          <div className="bg-white border border-sky-100 rounded-2xl p-6 flex flex-col justify-between shadow-sm">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Recommended Action</p>
              <p className={`text-3xl font-black mb-3 ${port.risk === "low" ? "text-emerald-600" : port.risk === "medium" ? "text-amber-600" : "text-red-600"}`}>
                {port.action}
              </p>
              <p className="text-slate-600 text-sm leading-relaxed">
                {port.risk === "low"
                  ? `${port.name} is well within vessel parameters. Berth utilization is at ${port.berth} and congestion is minimal. Proceed with chartering as planned.`
                  : port.risk === "medium"
                  ? `${port.name} shows moderate congestion at ${port.berth} berth utilization. Expected waiting time of ${port.waiting}. Factor idle costs into your charter analysis.`
                  : `${port.name} is experiencing high congestion (${port.berth} berth utilization). Waiting time of ${port.waiting} will significantly increase total voyage cost. Consider an alternative port.`}
              </p>
            </div>
            <div className="mt-6 p-4 bg-sky-50/70 border border-sky-100 rounded-xl">
              <p className="text-xs text-slate-500 uppercase tracking-wider font-bold mb-2">Vessel Draft vs Port Limit</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${port.risk === "low" ? "bg-emerald-500" : port.risk === "medium" ? "bg-amber-500" : "bg-red-500"}`}
                    style={{ width: `${(14.2 / parseFloat(port.maxDraft)) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-800 font-bold">14.2m / {port.maxDraft}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Compatibility Matrix */}
        <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-4">Vessel × Port Compatibility Matrix</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider text-slate-400 border-b border-slate-100">
                  <th className="pb-3 pr-6 font-bold">Vessel</th>
                  {ports.map((p) => (
                    <th key={p.name} className="pb-3 pr-4 text-center font-bold">{p.name}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {vessels.map((v) => (
                  <tr key={v} className="hover:bg-sky-50/40 transition-colors">
                    <td className="py-3.5 pr-6 font-bold text-slate-900">{v}</td>
                    {ports.map((p) => {
                      const c = compatibility[v]?.[p.name] ?? "incompatible";
                      return (
                        <td key={p.name} className="py-3.5 pr-4 text-center">
                          <div className="flex justify-center">{compatIcon[c]}</div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="flex gap-6 mt-4 pt-4 border-t border-slate-100">
              <span className="flex items-center gap-2 text-xs text-slate-600 font-medium"><CheckCircle className="w-4 h-4 text-emerald-600" /> Compatible</span>
              <span className="flex items-center gap-2 text-xs text-slate-600 font-medium"><AlertTriangle className="w-4 h-4 text-amber-500" /> Restricted</span>
              <span className="flex items-center gap-2 text-xs text-slate-600 font-medium"><XCircle className="w-4 h-4 text-red-500" /> Not Recommended</span>
            </div>
          </div>
        </div>

        {/* Action */}
        <div className="pb-8">
          <button
            onClick={() => router.push("/dashboard/forecast")}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            Continue to Freight Forecast <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </main>
    </div>
  );
}
