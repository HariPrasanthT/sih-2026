"use client";

import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { TrendingDown, Calendar, Sparkles } from "lucide-react";
import { fetchFreightForecast, ForecastPoint } from "@/lib/api";

const fallbackData: ForecastPoint[] = [
  { date: "15 Aug", historical: 18.9, forecast: null, upper: null, lower: null },
  { date: "22 Aug", historical: 18.4, forecast: null, upper: null, lower: null },
  { date: "29 Aug", historical: 17.8, forecast: null, upper: null, lower: null },
  { date: "04 Sep (Today)", historical: 17.4, forecast: 17.4, upper: 17.4, lower: 17.4 },
  { date: "10 Sep", historical: null, forecast: 16.9, upper: 17.3, lower: 16.5 },
  { date: "16 Sep", historical: null, forecast: 16.6, upper: 17.1, lower: 16.1 },
  { date: "22 Sep", historical: null, forecast: 16.8, upper: 17.5, lower: 16.2 },
  { date: "28 Sep", historical: null, forecast: 17.3, upper: 18.2, lower: 16.6 },
  { date: "05 Oct", historical: null, forecast: 17.9, upper: 18.9, lower: 17.0 },
];

export default function FreightForecastChart() {
  const [data, setData] = useState<ForecastPoint[]>(fallbackData);
  const [confidence, setConfidence] = useState<number>(91.4);
  const [optimalWindow, setOptimalWindow] = useState<string>("10 Sep – 20 Sep");
  const [insight, setInsight] = useState<string>("Rates projected to bottom out at $16.60/MT around 16 Sep before rebound.");
  const [yDomain, setYDomain] = useState<[number, number]>([15.5, 19.5]);
  const [todayMarker, setTodayMarker] = useState<string>("04 Sep (Today)");
  const [isLive, setIsLive] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    fetchFreightForecast("Newcastle", "Paradip", 30)
      .then((res) => {
        if (isMounted && res?.data && res.data.length > 0) {
          setData(res.data);
          if (res.confidence_pct) setConfidence(res.confidence_pct);
          if (res.optimal_window) setOptimalWindow(res.optimal_window);
          if (res.insight) setInsight(res.insight);
          if (res.y_domain) setYDomain(res.y_domain);
          if (res.today_marker) setTodayMarker(res.today_marker);
          setIsLive(true);
        }
      })
      .catch((err) => {
        console.warn("Forecast fetch fallback to initial data:", err);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="bg-white border border-sky-100 rounded-2xl p-5 shadow-sm hover:shadow-md shadow-sky-50 relative overflow-hidden">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-sky-500" />
            <h3 className="text-sm font-bold text-slate-900 tracking-wide uppercase">AI Freight Rate Forecast</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
              Confidence {confidence}%
            </span>
            {isLive && (
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200 uppercase font-semibold">
                ● Live API
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Panamax Newcastle → Paradip ($/MT) • Historical vs 30-Day Predictive Envelope
          </p>
        </div>

        {/* Optimal Window Highlight Badge */}
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl">
          <Calendar className="w-3.5 h-3.5 text-emerald-600" />
          <span className="text-xs text-slate-600">
            Optimal Charter Window: <strong className="text-emerald-700">{optimalWindow}</strong>
          </span>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-[260px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="confidenceArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.18} />
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.8} vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#e2e8f0" }}
              tick={{ fill: "#64748b" }}
            />
            <YAxis
              domain={yDomain}
              stroke="#94a3b8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#e2e8f0" }}
              tick={{ fill: "#64748b" }}
              unit=" $"
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-white border border-sky-200 rounded-xl p-3 text-xs shadow-lg shadow-sky-100">
                      <p className="font-bold text-slate-800 mb-1.5">{label}</p>
                      {payload.map((entry, idx) => (
                        <div key={idx} className="flex justify-between gap-4 text-slate-600">
                          <span style={{ color: entry.color }}>{entry.name}:</span>
                          <span className="font-mono font-bold text-slate-900">
                            ${Number(entry.value).toFixed(2)}/MT
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />

            {/* Confidence Band Area */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="transparent"
              fill="url(#confidenceArea)"
              name="Upper Bound"
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="transparent"
              fill="transparent"
              name="Lower Bound"
            />

            {/* Historical Actual Line */}
            <Line
              type="monotone"
              dataKey="historical"
              stroke="#64748b"
              strokeWidth={2.5}
              dot={{ r: 3, fill: "#64748b", strokeWidth: 0 }}
              name="Historical Actual"
            />

            {/* AI Forecast Projected Line */}
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#0ea5e9"
              strokeWidth={2.5}
              strokeDasharray="4 4"
              dot={{ r: 4, fill: "#0ea5e9", strokeWidth: 0 }}
              name="AI Predicted Rate"
            />

            {/* Today Marker */}
            <ReferenceLine x={todayMarker} stroke="#d97706" strokeDasharray="3 3" label={{ value: "TODAY", fill: "#d97706", fontSize: 10, position: "insideTopLeft" }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Footer Insight Strip */}
      <div className="flex flex-wrap items-center justify-between gap-3 mt-3 pt-3 border-t border-slate-100 text-xs">
        <div className="flex items-center gap-2 text-slate-600">
          <TrendingDown className="w-4 h-4 text-emerald-500 shrink-0" />
          <span>{insight}</span>
        </div>
        <div className="flex items-center gap-4 text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-0.5 bg-slate-500 inline-block" /> Actual Rate</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-0.5 bg-sky-400 border-dashed inline-block" /> AI Projection</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2 bg-sky-200 inline-block rounded" /> 90% Confidence Envelope</span>
        </div>
      </div>
    </div>
  );
}
