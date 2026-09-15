"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import { fetchPorts } from "@/lib/api";
import {
  ArrowRight,
  MapPin,
  Clock,
  AlertTriangle,
  DollarSign,
  Activity,
  Navigation,
  Wind,
  Compass,
} from "lucide-react";

interface Destination {
  name: string;
  state: string;
  congestion: string;
  risk: "low" | "medium" | "high";
  draft: string;
  waitingDays?: string;
}

const destinations: Destination[] = [
  { name: "Paradip", state: "Odisha", congestion: "Moderate", risk: "medium", draft: "14.2m", waitingDays: "1.4 Days" },
  { name: "Dhamra", state: "Odisha", congestion: "Low", risk: "low", draft: "16.5m", waitingDays: "0.6 Days" },
  { name: "Visakhapatnam", state: "Andhra Pradesh", congestion: "High", risk: "high", draft: "14.0m", waitingDays: "2.5 Days" },
  { name: "Gangavaram", state: "Andhra Pradesh", congestion: "Low", risk: "low", draft: "18.0m", waitingDays: "0.4 Days" },
  { name: "Gopalpur", state: "Odisha", congestion: "Low", risk: "low", draft: "12.0m", waitingDays: "0.5 Days" },
  { name: "Sagar", state: "West Bengal", congestion: "Moderate", risk: "medium", draft: "12.0m", waitingDays: "1.8 Days" },
  { name: "Haldia", state: "West Bengal", congestion: "High", risk: "high", draft: "8.5m", waitingDays: "4.8 Days" },
];

const riskBadgeStyle: Record<string, string> = {
  low: "text-emerald-700 bg-emerald-50 border-emerald-200",
  medium: "text-amber-700 bg-amber-50 border-amber-200",
  high: "text-red-700 bg-red-50 border-red-200",
};

const riskTextColor: Record<string, string> = {
  low: "text-emerald-600",
  medium: "text-amber-600",
  high: "text-red-600",
};

const congestionDot: Record<string, string> = {
  low: "bg-emerald-500",
  medium: "bg-amber-500",
  high: "bg-red-500",
};

export default function RoutePage() {
  const router = useRouter();
  const [selectedDest, setSelectedDest] = useState("Paradip");
  const [destList, setDestList] = useState<Destination[]>(destinations);
  const [isLiveConnected, setIsLiveConnected] = useState(false);

  useEffect(() => {
    fetchPorts()
      .then((ports) => {
        if (ports && ports.length > 0) {
          const mapped: Destination[] = ports.map((p) => {
            const level = (p.current_congestion_level || "low").toLowerCase();
            const risk: "low" | "medium" | "high" =
              level === "high" ? "high" : level === "moderate" ? "medium" : "low";
            const congestion = level === "high" ? "High" : level === "moderate" ? "Moderate" : "Low";
            return {
              name: p.name.replace(" Port", ""),
              state: p.state || "East Coast",
              congestion,
              risk,
              draft: `${p.draft_max_m}m`,
              waitingDays: `${p.average_waiting_days} Days`,
            };
          });
          setDestList(mapped);
          setIsLiveConnected(true);
        }
      })
      .catch(() => {});
  }, []);

  const destInfo = destList.find((d) => d.name === selectedDest) || destList[0] || destinations[0];

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Origin & Destination Intelligence" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Origin & Destination Intelligence</h1>
            <p className="text-slate-500 text-sm mt-1">Select route and analyse maritime intelligence for your voyage.</p>
          </div>
          <span className={`text-xs px-3 py-1 rounded-full border font-mono flex items-center gap-1.5 ${
            isLiveConnected ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-slate-100 text-slate-600 border-slate-200"
          }`}>
            <span className={`w-2 h-2 rounded-full ${isLiveConnected ? "bg-emerald-500 animate-pulse" : "bg-slate-400"}`} />
            {isLiveConnected ? "Live Ports Connected" : "Connecting Ports..."}
          </span>
        </div>

        {/* Route Selector Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          {/* Origin */}
          <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">Origin Port</p>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2.5 rounded-xl bg-sky-50 text-sky-600 border border-sky-100">
                <Navigation className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xl font-bold text-slate-900">Newcastle</p>
                <p className="text-sm text-slate-500 font-medium">Australia</p>
              </div>
            </div>
            <div className="space-y-1.5 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
              <p>📦 Coal Export Hub</p>
              <p>⚓ Panamax Compatible</p>
            </div>
          </div>

          {/* Arrow + Stats */}
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="flex items-center gap-2 text-slate-400">
              <div className="h-px w-12 bg-gradient-to-r from-transparent to-sky-400" />
              <ArrowRight className="w-6 h-6 text-sky-500" />
              <div className="h-px w-12 bg-gradient-to-r from-sky-400 to-transparent" />
            </div>
            <div className="bg-white border border-sky-100 rounded-2xl px-5 py-4 space-y-2 w-full shadow-sm">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500 font-medium">Distance</span>
                <span className="text-slate-900 font-bold">4,850 NM</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500 font-medium">Sailing Time</span>
                <span className="text-slate-900 font-bold">~20–22 Days</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500 font-medium">Freight (Indicative)</span>
                <span className="text-sky-600 font-bold">$18.40 / MT</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500 font-medium">Route Risk</span>
                <span className="text-emerald-600 font-bold">Low</span>
              </div>
            </div>
          </div>

          {/* Destination Selector */}
          <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">Destination Port</p>
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2.5 rounded-xl bg-amber-50 text-amber-600 border border-amber-100">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xl font-bold text-slate-900">{selectedDest}</p>
                <p className="text-sm text-slate-500 font-medium">East Coast, India</p>
              </div>
            </div>
            <select
              value={selectedDest}
              onChange={(e) => setSelectedDest(e.target.value)}
              className="w-full bg-sky-50/80 border border-sky-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 font-semibold focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all"
            >
              {destList.map((d) => (
                <option key={d.name} value={d.name}>{d.name}, {d.state}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Destination Details */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Congestion", value: destInfo.congestion, icon: <Activity className="w-4 h-4 text-sky-500" />, color: destInfo.risk },
            { label: "Allowed Draft", value: destInfo.draft, icon: <Wind className="w-4 h-4 text-sky-500" />, color: "low" },
            { label: "Avg. Waiting Time", value: destInfo.waitingDays || (destInfo.congestion === "High" ? "4–6 Days" : destInfo.congestion === "Moderate" ? "2–3 Days" : "0–1 Day"), icon: <Clock className="w-4 h-4 text-sky-500" />, color: destInfo.risk },
            { label: "Freight Indication", value: "$18.40 / MT", icon: <DollarSign className="w-4 h-4 text-sky-500" />, color: "low" },
          ].map((stat) => (
            <div key={stat.label} className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-2 text-slate-500">
                {stat.icon}
                <span className="text-xs uppercase tracking-wider font-bold">{stat.label}</span>
              </div>
              <p className={`text-xl font-black ${riskTextColor[stat.color]}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Alternative Destination Ports */}
        <div className="bg-white border border-sky-100 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-4">East Coast India — Port Overview</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider text-slate-400 border-b border-slate-100">
                  <th className="pb-3 pr-6 font-bold">Port</th>
                  <th className="pb-3 pr-6 font-bold">State</th>
                  <th className="pb-3 pr-6 font-bold">Max Draft</th>
                  <th className="pb-3 pr-6 font-bold">Congestion</th>
                  <th className="pb-3 font-bold">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {destList.map((d) => (
                  <tr
                    key={d.name}
                    onClick={() => setSelectedDest(d.name)}
                    className={`cursor-pointer transition-colors hover:bg-sky-50/50 ${selectedDest === d.name ? "bg-sky-50" : ""}`}
                  >
                    <td className="py-3.5 pr-6 font-bold text-slate-900">
                      {d.name} {selectedDest === d.name && <span className="text-sky-600 text-xs ml-1 font-semibold">● Selected</span>}
                    </td>
                    <td className="py-3.5 pr-6 text-slate-600">{d.state}</td>
                    <td className="py-3.5 pr-6 text-slate-700 font-medium">{d.draft}</td>
                    <td className="py-3.5 pr-6">
                      <span className="flex items-center gap-1.5">
                        <span className={`w-2 h-2 rounded-full ${congestionDot[d.risk]}`} />
                        <span className="text-slate-700 font-medium">{d.congestion}</span>
                      </span>
                    </td>
                    <td className="py-3.5">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${riskBadgeStyle[d.risk]}`}>
                        {d.risk.charAt(0).toUpperCase() + d.risk.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Action */}
        <div className="flex items-center gap-4 pb-8">
          <button
            onClick={() => router.push("/dashboard/vessels")}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            Continue to Vessel Search <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </main>
    </div>
  );
}
