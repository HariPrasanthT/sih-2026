"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Topbar from "@/components/layout/Topbar";
import {
  FileText, Download, Share2, Send, CheckCircle, TrendingDown,
  Ship, MapPin, BarChart2, Brain, Shield, Star, Sparkles,
} from "lucide-react";

const sections = [
  { icon: <FileText className="w-4 h-4 text-sky-600" />, title: "Cargo Requirement", content: "80,000 MT Coal (6000 GAR) | Priority: Balanced | Contract: Short-Term" },
  { icon: <MapPin className="w-4 h-4 text-sky-600" />, title: "Origin & Destination", content: "Newcastle, Australia → Paradip, India | Distance: 4,850 NM | ETA: 20–22 Days" },
  { icon: <Ship className="w-4 h-4 text-sky-600" />, title: "Selected Vessel", content: "MV Pacific Voyager (IMO: 9412567) | Panamax | 82,000 MT | Draft: 14.2m | AI Score: 94" },
  { icon: <MapPin className="w-4 h-4 text-sky-600" />, title: "Port Compatibility", content: "Paradip: Compatible ✓ | Draft clearance: 14.2m / 14.2m | Risk: Medium | Est. Waiting: 2–3 Days" },
  { icon: <BarChart2 className="w-4 h-4 text-sky-600" />, title: "Freight Forecast", content: "Current: $18.40/MT | 30-Day Forecast: $17.10/MT | Trend: Bearish | Optimal Window: 10–24 Sep" },
  { icon: <TrendingDown className="w-4 h-4 text-emerald-600" />, title: "Cost Analysis", content: "Short-Term: $9.7M | Spot: $10.2M | Medium-Term: $9.4M | Recommended: Short-Term" },
  { icon: <Shield className="w-4 h-4 text-sky-600" />, title: "Idle Time Prediction", content: "Expected Idle: 2.5 Days | Demurrage Exposure: $45–80K | Delay Probability: 38%" },
  { icon: <CheckCircle className="w-4 h-4 text-emerald-600" />, title: "Contract Strategy", content: "SHORT-TERM MULTI-VOYAGE recommended | 3–6 voyages over 6–12 months" },
  { icon: <Brain className="w-4 h-4 text-sky-600" />, title: "Risk Analysis", content: "Overall Risk: MEDIUM | Key risks: Paradip congestion, freight volatility | Manageable" },
  { icon: <Star className="w-4 h-4 text-amber-500" />, title: "AI Recommendation", content: "Charter MV Pacific Voyager on Short-Term contract. Entry window: 10–24 Sep 2026" },
  { icon: <TrendingDown className="w-4 h-4 text-emerald-600" />, title: "Expected Savings", content: "vs Spot: $500K | vs Market Average: $720K | AI Confidence: 86%" },
];

export default function ReportPage() {
  const router = useRouter();
  const [generated, setGenerated] = useState(false);

  return (
    <div className="flex flex-col min-h-screen bg-[#f0f7ff] text-slate-900">
      <Topbar title="Charter Intelligence Report" />

      <main className="flex-1 p-6 lg:p-8 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Charter Intelligence Report</h1>
            <p className="text-slate-500 text-sm mt-1">Complete AI-generated charter analysis — ready for management review.</p>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-sky-100 shadow-sm">
            <span className="text-xs text-slate-400 font-medium">Report ID:</span>
            <span className="text-xs font-mono font-bold text-sky-700">FIQ-2026-0902-001</span>
          </div>
        </div>

        {/* Report Preview */}
        <div className="bg-white border border-sky-100 rounded-3xl overflow-hidden shadow-sm">
          {/* Report Header */}
          <div className="bg-gradient-to-r from-sky-500 via-blue-600 to-cyan-500 p-8 text-white">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-white/80 mb-2">FreightIQ Charter Intelligence</p>
                <h2 className="text-3xl font-black text-white mb-1">Charter Decision Report</h2>
                <p className="text-white/80 text-sm">Generated: 02 September 2026 | SAIL Chartering Division</p>
              </div>
              <div className="text-right bg-white/15 backdrop-blur-md p-4 rounded-2xl border border-white/20">
                <div className="text-4xl font-black text-white">91</div>
                <div className="text-[10px] font-bold text-white/80 uppercase tracking-wider mt-0.5">AI Charter Score</div>
              </div>
            </div>
          </div>

          {/* Report Sections */}
          <div className="p-6 divide-y divide-slate-100">
            {sections.map((s, i) => (
              <div key={i} className="py-4 flex items-start gap-4 hover:bg-slate-50/50 px-2 rounded-xl transition-colors">
                <div className="p-2.5 rounded-xl bg-sky-50 border border-sky-100 shrink-0 mt-0.5">{s.icon}</div>
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                    {String(i + 1).padStart(2, "0")} — {s.title}
                  </p>
                  <p className="text-sm font-semibold text-slate-800">{s.content}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Final Decision Box */}
          <div className="m-6 p-6 bg-gradient-to-br from-sky-50 to-blue-50 border border-sky-200 rounded-2xl shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-sky-700 mb-1">Final AI Recommendation</p>
                <p className="text-xl font-black text-slate-900">Charter MV Pacific Voyager</p>
                <p className="text-slate-600 text-sm mt-1">Short-Term Multi-Voyage | Newcastle → Paradip | Entry: 10–24 Sep 2026</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-500 font-semibold">Expected Savings</p>
                <p className="text-3xl font-black text-emerald-600">$720K</p>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-4 pb-8">
          <button
            onClick={() => setGenerated(true)}
            className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-bold hover:from-sky-400 hover:to-blue-500 transition-all shadow-md shadow-sky-200 hover:shadow-lg hover:shadow-sky-300"
          >
            <FileText className="w-4 h-4" />
            {generated ? "PDF Generated ✓" : "Generate PDF Report"}
          </button>
          <button className="flex items-center gap-2 px-5 py-3 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-sky-300 transition-all font-semibold shadow-sm">
            <Download className="w-4 h-4 text-slate-400" /> Download Report
          </button>
          <button className="flex items-center gap-2 px-5 py-3 rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 hover:border-sky-300 transition-all font-semibold shadow-sm">
            <Share2 className="w-4 h-4 text-slate-400" /> Share with Management
          </button>
          <button
            onClick={() => router.push("/dashboard/decision")}
            className="flex items-center gap-2 px-5 py-3 rounded-xl border border-emerald-200 text-emerald-700 bg-emerald-50 hover:bg-emerald-100 transition-all font-bold ml-auto shadow-sm"
          >
            <Send className="w-4 h-4" /> Proceed to Final Decision
          </button>
        </div>
      </main>
    </div>
  );
}
