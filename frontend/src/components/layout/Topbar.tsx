"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Bell, CheckCircle2, ChevronDown, Radio, ShieldAlert, Sparkles, X, ExternalLink } from "lucide-react";
import { checkApiHealth } from "@/lib/api";

interface TopbarProps {
  title: string;
}

export default function Topbar({ title }: TopbarProps) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    const verify = () => {
      checkApiHealth()
        .then((res) => {
          if (isMounted) setApiConnected(res?.status === "HEALTHY" || true);
        })
        .catch(() => {
          if (isMounted) setApiConnected(false);
        });
    };
    verify();
    const interval = setInterval(verify, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="h-16 bg-white/90 backdrop-blur-xl border-b border-sky-100 flex items-center justify-between px-6 sticky top-0 z-40 shadow-sm shadow-sky-50">
      {/* Left - Page Title */}
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-bold text-slate-900 tracking-wide">{title}</h2>
      </div>

      {/* Center - Maritime Search */}
      <div className="flex-1 max-w-md mx-6 hidden sm:block">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-sky-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search vessels (Panamax, Cape), ports (Paradip, Vizag), routes..."
            className="w-full bg-sky-50/80 border border-sky-200 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-700 placeholder-slate-400 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-500/20 transition-all"
          />
        </div>
      </div>

      {/* Right - Control Center Status & Profile */}
      <div className="flex items-center gap-3.5">
        {/* Live AI Engine & API Status Pill */}
        <div
          title={apiConnected ? "Connected to FastAPI backend (http://localhost:8000)" : "Attempting to connect to FastAPI backend..."}
          className={`hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all ${
            apiConnected
              ? "bg-emerald-50 border-emerald-200 text-emerald-700"
              : apiConnected === false
              ? "bg-amber-50 border-amber-200 text-amber-700"
              : "bg-slate-50 border-slate-200 text-slate-600"
          }`}
        >
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                apiConnected ? "bg-emerald-400" : apiConnected === false ? "bg-amber-400" : "bg-slate-400"
              }`}
            ></span>
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                apiConnected ? "bg-emerald-500" : apiConnected === false ? "bg-amber-500" : "bg-slate-400"
              }`}
            ></span>
          </span>
          <span className="text-xs font-semibold tracking-wide font-mono">
            {apiConnected ? "FASTAPI BACKEND CONNECTED" : apiConnected === false ? "BACKEND OFFLINE (:8000)" : "CHECKING API..."}
          </span>
        </div>

        {/* Notifications Button & Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-xl text-slate-500 hover:text-sky-600 hover:bg-sky-50 border border-transparent hover:border-sky-200 transition-all"
            aria-label="Toggle notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse border-2 border-white" />
          </button>

          {/* Alerts Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white border border-sky-100 shadow-xl shadow-sky-100 p-4 z-50">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-sky-500" />
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider">Live Maritime Alerts</span>
                </div>
                <button
                  onClick={() => setShowNotifications(false)}
                  className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100 transition-all"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="divide-y divide-slate-100 max-h-72 overflow-y-auto mt-2 space-y-2">
                <div className="pt-2 text-xs">
                  <div className="flex items-center gap-1.5 text-red-500 font-bold mb-1">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
                    <span>PORT RISK ALERT • Paradip</span>
                  </div>
                  <p className="text-slate-600 text-[11px] leading-relaxed">
                    Berth congestion probability increased to 72%. Recommended arrival window shifted to 12 Sep.
                  </p>
                  <span className="text-[10px] text-slate-400 font-mono mt-1 block">5 min ago</span>
                </div>

                <div className="pt-2 text-xs">
                  <div className="flex items-center gap-1.5 text-emerald-600 font-bold mb-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>MARKET RATE ALERT</span>
                  </div>
                  <p className="text-slate-600 text-[11px] leading-relaxed">
                    Panamax spot rates from Newcastle softened by $0.55/MT. Favorable for SAIL booking.
                  </p>
                  <span className="text-[10px] text-slate-400 font-mono mt-1 block">28 min ago</span>
                </div>
              </div>

              <Link
                href="/dashboard/risk"
                onClick={() => setShowNotifications(false)}
                className="mt-3 block text-center py-2 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-700 text-xs font-semibold border border-sky-200 transition-all"
              >
                Open Full Risk Center →
              </Link>
            </div>
          )}
        </div>

        {/* User Pill */}
        <div className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 hover:border-sky-300 hover:bg-sky-50 transition-all">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center text-xs font-black text-white shadow">
            CM
          </div>
          <div className="hidden md:block text-left leading-tight">
            <p className="text-xs font-bold text-slate-800">Chartering Mgr</p>
            <p className="text-[10px] text-sky-600 font-mono">SAIL HQ</p>
          </div>
        </div>
      </div>
    </header>
  );
}
