"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Anchor,
  Package,
  Navigation,
  Ship,
  MapPin,
  TrendingUp,
  GitCompare,
  AlertTriangle,
  FileText,
  Settings,
  LogOut,
  ChevronRight,
  LayoutDashboard,
  Bot,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { step: "00", label: "Control Center", icon: LayoutDashboard, href: "/dashboard" },
  { step: "AI", label: "AI Charter Assistant", icon: Bot, href: "/dashboard/chat" },
  { step: "01", label: "Cargo Requirement", icon: Package, href: "/dashboard/cargo" },
  { step: "02", label: "Route Intelligence", icon: Navigation, href: "/dashboard/route" },
  { step: "03", label: "Vessel Search", icon: Ship, href: "/dashboard/vessels" },
  { step: "04", label: "Port Compatibility", icon: MapPin, href: "/dashboard/ports" },
  { step: "05", label: "Freight Forecast", icon: TrendingUp, href: "/dashboard/forecast" },
  { step: "06", label: "Charter Strategy", icon: GitCompare, href: "/dashboard/strategy" },
  { step: "07", label: "Risk Analysis", icon: AlertTriangle, href: "/dashboard/risk" },
  { step: "08", label: "Report Generation", icon: FileText, href: "/dashboard/report" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-sky-100 flex flex-col z-40 shadow-lg shadow-sky-100/50">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-sky-100 bg-gradient-to-r from-sky-50 to-blue-50">
        <div className="p-2 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 text-white shadow-md shadow-sky-200">
          <Anchor className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-black tracking-tight text-slate-900 leading-none">
            Freight<span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-blue-600">IQ</span>
          </h1>
          <p className="text-[10px] text-sky-600 font-bold tracking-widest uppercase mt-1">
            Maritime Terminal
          </p>
        </div>
      </div>

      {/* Navigation Workflow Links */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <div className="flex items-center justify-between px-3 mb-3">
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">Workflow Engine</p>
          <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
        </div>

        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all group relative",
                isActive
                  ? "bg-gradient-to-r from-sky-500 to-blue-600 text-white shadow-md shadow-sky-200"
                  : "text-slate-600 hover:bg-sky-50 hover:text-sky-800 border border-transparent hover:border-sky-100"
              )}
            >
              <span
                className={cn(
                  "text-[10px] font-mono font-bold w-4 text-center",
                  isActive ? "text-white/80" : "text-slate-400 group-hover:text-sky-500"
                )}
              >
                {item.step}
              </span>
              <Icon className={cn("w-4 h-4 shrink-0", isActive ? "text-white" : "text-slate-400 group-hover:text-sky-600")} />
              <span className="flex-1 truncate">{item.label}</span>
              {isActive && <ChevronRight className="w-3.5 h-3.5 text-white/80 shrink-0" />}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Footer Section */}
      <div className="border-t border-sky-100 px-3 py-3 space-y-1 bg-slate-50">
        <Link
          href="/dashboard"
          className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-slate-500 hover:bg-sky-50 hover:text-sky-700 transition-all"
        >
          <Settings className="w-3.5 h-3.5" />
          <span>System Config</span>
        </Link>
        <Link
          href="/login"
          className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-slate-500 hover:bg-red-50 hover:text-red-600 transition-all"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Exit Session</span>
        </Link>
      </div>
    </aside>
  );
}
