"use client";

import { useState, useEffect } from "react";
import Topbar from "@/components/layout/Topbar";
import {
  CheckCircle, Ship, MapPin, Calendar, DollarSign,
  TrendingDown, Shield, Star, Bell, AlertTriangle, Sparkles, Activity,
} from "lucide-react";
import Link from "next/link";
import { fetchRecommendations, fetchLiveMarket, fetchPorts, RecommendationItem } from "@/lib/api";

const defaultAlerts = [
  { icon: <AlertTriangle className="w-4 h-4 text-amber-600" />, text: "Paradip congestion expected to increase over next 7 days", time: "Live", type: "warning" },
  { icon: <AlertTriangle className="w-4 h-4 text-amber-600" />, text: "Vessel ETA delayed by 2 days due to adverse weather", time: "2h ago", type: "warning" },
  { icon: <AlertTriangle className="w-4 h-4 text-amber-600" />, text: "Panamax availability tightening in Q4 2026", time: "5h ago", type: "warning" },
  { icon: <TrendingDown className="w-4 h-4 text-emerald-600" />, text: "Freight rates decreased 4.8% — within optimal window", time: "1h ago", type: "positive" },
  { icon: <CheckCircle className="w-4 h-4 text-emerald-600" />, text: "Optimal charter window approaching: 10–24 Sep 2026", time: "12h ago", type: "positive" },
];

export default function DecisionPage() {
  const [score, setScore] = useState<number>(94);
  const [confidence, setConfidence] = useState<number>(91);
  const [riskLevel, setRiskLevel] = useState<string>("Low");
  const [vesselName, setVesselName] = useState<string>("MV PACIFIC VOYAGER");
  const [vesselSub, setVesselSub] = useState<string>("Panamax, 82,000 MT");
  const [routeStr, setRouteStr] = useState<string>("Newcastle → Paradip");
  const [charterWindow, setCharterWindow] = useState<string>("10 Sep – 24 Sep 2026");
  const [contractType, setContractType] = useState<string>("Short-Term Multi-Voyage");
  const [totalCost, setTotalCost] = useState<string>("$1.39M");
  const [savings, setSavings] = useState<string>("$720K");
  const [forecastRate, setForecastRate] = useState<string>("$17.40 / MT");
  const [isLive, setIsLive] = useState<boolean>(false);

  const [alerts, setAlerts] = useState(defaultAlerts);

  const [monitorStats, setMonitorStats] = useState([
    { label: "Vessel Position", value: "Bay of Bengal", icon: <Ship className="w-5 h-5 text-sky-500" />, sub: "ETA: 12 Sep 2026 (Revised)" },
    { label: "Port Status", value: "Paradip — Moderate", icon: <MapPin className="w-5 h-5 text-amber-500" />, sub: "Congestion increasing" },
    { label: "Current Freight", value: "$17.40 / MT", icon: <DollarSign className="w-5 h-5 text-sky-500" />, sub: "Softening trend" },
    { label: "Cargo Status", value: "Loading — 60%", icon: <Star className="w-5 h-5 text-emerald-500" />, sub: "On track" },
    { label: "Idle Time", value: "1.4 Days", icon: <Calendar className="w-5 h-5 text-amber-500" />, sub: "Expected at Paradip" },
    { label: "Berth Availability", value: "3 Berths Free", icon: <Shield className="w-5 h-5 text-emerald-500" />, sub: "As of today" },
  ]);

  useEffect(() => {
    let isMounted = true;

    const applyRecommendation = (topRec: RecommendationItem, cargoReq?: any) => {
      if (topRec?.scores?.composite_score) {
        setScore(Math.round(topRec.scores.composite_score));
      }
      if (topRec?.vessel?.name) {
        setVesselName(topRec.vessel.name.toUpperCase());
        const type = topRec.vessel.vessel_type || "Panamax";
        const dwt = (topRec.vessel.deadweight_tonnage || 82000).toLocaleString();
        setVesselSub(`${type}, ${dwt} MT`);
      }
      if (cargoReq?.origin_port && cargoReq?.destination_port) {
        setRouteStr(`${cargoReq.origin_port} → ${cargoReq.destination_port}`);
      }
      if (topRec?.timeline?.laycan_window) {
        setCharterWindow(topRec.timeline.laycan_window);
      }
      if (cargoReq?.contract_type) {
        setContractType(cargoReq.contract_type);
      }
      if (topRec?.financials?.total_cost_usd) {
        const costMillions = topRec.financials.total_cost_usd / 1_000_000;
        setTotalCost(`$${costMillions.toFixed(2)}M`);
      }
      if (topRec?.financials?.estimated_savings_usd) {
        const savingsK = Math.round(topRec.financials.estimated_savings_usd / 1000);
        setSavings(`$${savingsK}K`);
      }
      if (topRec?.financials?.cost_per_ton_usd) {
        setForecastRate(`$${topRec.financials.cost_per_ton_usd.toFixed(2)} / MT`);
      }
      if (topRec?.risk_assessment?.risk_level) {
        setRiskLevel(topRec.risk_assessment.risk_level.charAt(0).toUpperCase() + topRec.risk_assessment.risk_level.slice(1));
      }
      setIsLive(true);
    };

    // 1. Try reading from sessionStorage
    if (typeof window !== "undefined") {
      const stored = sessionStorage.getItem("freightiq_decision");
      const storedCargo = sessionStorage.getItem("freightiq_cargo");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          const parsedCargo = storedCargo ? JSON.parse(storedCargo) : null;
          if (parsed.recommendations && parsed.recommendations.length > 0) {
            applyRecommendation(parsed.recommendations[0], parsedCargo);
            return;
          }
        } catch (e) {
          console.warn("Error parsing session decision data:", e);
        }
      }
    }

    // 2. Fetch fresh recommendation from backend
    fetchRecommendations({
      origin_port: "Newcastle",
      destination_port: "Paradip",
      quantity_mt: 80000,
      priority: "Balanced",
      cargo_type: "Coal",
    })
      .then((res) => {
        if (!isMounted || !res?.recommendations?.length) return;
        applyRecommendation(res.recommendations[0], {
          origin_port: "Newcastle",
          destination_port: "Paradip",
          contract_type: "Short-Term Multi-Voyage",
        });
      })
      .catch((err) => {
        console.warn("Using offline decision values:", err);
      });

    // 3. Update live market telemetry
    fetchLiveMarket()
      .then((m) => {
        if (!isMounted || !m) return;
        setMonitorStats((prev) =>
          prev.map((s) => {
            if (s.label === "Current Freight" && m.panamax_rate) {
              return { ...s, value: `$${m.panamax_rate.toFixed(2)} / MT` };
            }
            return s;
          })
        );
      })
      .catch(() => {});

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Final Charter Decision" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        {/* Final Decision Hero */}
        <div className="relative bg-white border border-sky-100 rounded-3xl p-8 overflow-hidden shadow-sm">
          <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-sky-100/60 to-transparent rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10">
            <div className="flex items-center justify-between gap-4 mb-2">
              <div className="flex items-center gap-2 text-sky-700 font-bold text-xs uppercase tracking-widest">
                <Sparkles className="w-4 h-4 text-sky-500" />
                <span>AI Charter Recommendation Score</span>
              </div>
              {isLive && (
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span>Live Pareto MCDM Solution</span>
                </div>
              )}
            </div>

            <div className="flex flex-wrap items-end gap-6 mb-6">
              <div className="text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-sky-600 via-blue-600 to-emerald-600 leading-none">
                {score}
              </div>
              <div className="mb-2">
                <p className="text-xs text-slate-400 uppercase font-semibold">out of</p>
                <p className="text-2xl font-bold text-slate-400">100</p>
              </div>
              <div className="mb-2 flex flex-col gap-1.5">
                <span className="flex items-center gap-2 text-xs text-emerald-700 font-bold bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
                  <CheckCircle className="w-4 h-4" /> Confidence: {confidence}%
                </span>
                <span className="flex items-center gap-2 text-xs text-amber-700 font-bold bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
                  <Shield className="w-4 h-4" /> Risk: {riskLevel}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 bg-slate-50 p-5 rounded-2xl border border-slate-100">
              {[
                { label: "Recommended Vessel", value: vesselName, sub: vesselSub },
                { label: "Route", value: routeStr, sub: "4,850 NM | 20–22 Days" },
                { label: "Charter Window", value: charterWindow, sub: "AI Optimal Entry" },
                { label: "Contract Type", value: contractType, sub: "3–6 Voyages" },
              ].map((item) => (
                <div key={item.label}>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">{item.label}</p>
                  <p className="text-base font-bold text-slate-900">{item.value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{item.sub}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {[
                { label: "Expected Total Cost", value: totalCost, color: "text-slate-900" },
                { label: "Expected Savings", value: savings, color: "text-emerald-600" },
                { label: "Forecast Rate", value: forecastRate, color: "text-sky-600" },
              ].map((kpi) => (
                <div key={kpi.label} className="bg-white rounded-2xl p-4 border border-sky-100 shadow-sm">
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold mb-1">{kpi.label}</p>
                  <p className={`text-2xl font-black ${kpi.color}`}>{kpi.value}</p>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap gap-4">
              <button className="flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-black text-base hover:from-sky-400 hover:to-blue-500 transition-all shadow-lg shadow-sky-200 hover:shadow-xl hover:shadow-sky-300">
                <CheckCircle className="w-5 h-5" /> PROCEED WITH CHARTER
              </button>
              <Link href="/dashboard/report">
                <button className="flex items-center gap-2 px-6 py-4 rounded-xl border border-slate-200 bg-white text-slate-700 font-bold hover:bg-slate-50 hover:border-sky-300 transition-all text-base shadow-sm">
                  Review Analysis
                </button>
              </Link>
            </div>
          </div>
        </div>

        {/* Monitoring Section */}
        <div>
          <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-sky-500" /> Live Voyage Monitoring
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {monitorStats.map((s) => (
              <div key={s.label} className="bg-white border border-sky-100 rounded-2xl p-5 flex items-start gap-4 shadow-sm">
                <div className="p-2.5 rounded-xl bg-sky-50 border border-sky-100 shrink-0">{s.icon}</div>
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-0.5">{s.label}</p>
                  <p className="text-base font-bold text-slate-900">{s.value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{s.sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alerts */}
        <div>
          <h2 className="text-lg font-bold text-slate-900 mb-4">Intelligence Alerts</h2>
          <div className="space-y-3">
            {alerts.map((a, i) => (
              <div
                key={i}
                className={`flex items-start gap-3 p-4 rounded-2xl border shadow-sm ${
                  a.type === "warning"
                    ? "bg-amber-50/70 border-amber-200"
                    : "bg-emerald-50/70 border-emerald-200"
                }`}
              >
                <div className="shrink-0 mt-0.5">{a.icon}</div>
                <p className="text-sm text-slate-700 font-medium flex-1">{a.text}</p>
                <span className="text-xs text-slate-400 font-semibold shrink-0">{a.time}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
