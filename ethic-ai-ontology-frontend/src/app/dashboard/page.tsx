"use client";

import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from "recharts";
import { Activity, AlertTriangle, ShieldCheck, TrendingUp } from "lucide-react";

// Mock Data for Demo Purposes
const riskDistribution = [
  { name: "ProhibitedRisk", value: 35, color: "#ef4444" },
  { name: "HighRisk", value: 45, color: "#f97316" },
  { name: "LimitedRisk", value: 15, color: "#eab308" },
  { name: "MinimalRisk", value: 5, color: "#3b82f6" },
];

const topRegulations = [
  { name: "GDPR Art. 9", count: 120 },
  { name: "EU AI Act Art. 5", count: 95 },
  { name: "KVKK Art. 6", count: 80 },
  { name: "GDPR Art. 22", count: 65 },
  { name: "EU AI Act Art. 9", count: 50 },
];

const scanTimeline = [
  { month: "Jan", scans: 120, risksDetected: 40 },
  { month: "Feb", scans: 150, risksDetected: 55 },
  { month: "Mar", scans: 200, risksDetected: 80 },
  { month: "Apr", scans: 180, risksDetected: 60 },
  { month: "May", scans: 250, risksDetected: 110 },
  { month: "Jun", scans: 310, risksDetected: 140 },
];

export default function DashboardPage() {
  return (
    <div className="relative min-h-screen py-10 px-4">
      <AnimatedBackground />
      <div className="max-w-7xl mx-auto space-y-8">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <Activity className="w-8 h-8 text-blue-400" />
              Governance Dashboard
            </h1>
            <p className="text-zinc-400 mt-1">Real-time overview of AI compliance and ethical risks.</p>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-black/40 border-white/10 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-400 font-medium">Total Systems Analyzed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">1,210</div>
              <p className="text-xs text-emerald-400 mt-1 flex items-center"><TrendingUp className="w-3 h-3 mr-1"/> +12% from last month</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-white/10 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-400 font-medium">Prohibited Risks Detected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-400">423</div>
              <p className="text-xs text-red-400/80 mt-1 flex items-center">Requires immediate action</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-white/10 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-400 font-medium">Top Violated Principle</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-400">Privacy</div>
              <p className="text-xs text-orange-400/80 mt-1">45% of total violations</p>
            </CardContent>
          </Card>

          <Card className="bg-black/40 border-white/10 backdrop-blur-md">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-400 font-medium">Compliance Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">68%</div>
              <p className="text-xs text-emerald-400/80 mt-1">Global average across portfolio</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Distribution Pie */}
          <Card className="bg-black/40 border-white/10 backdrop-blur-md h-[400px] flex flex-col">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                Risk Level Distribution
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 min-h-0 relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={120}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }}
                    itemStyle={{ color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              {/* Legend overlay */}
              <div className="absolute right-4 top-1/2 -translate-y-1/2 space-y-2">
                {riskDistribution.map((item) => (
                  <div key={item.name} className="flex items-center gap-2 text-sm text-zinc-300">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    {item.name}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Regulation Bar Chart */}
          <Card className="bg-black/40 border-white/10 backdrop-blur-md h-[400px] flex flex-col">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
                Most Triggered Regulations
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topRegulations} layout="vertical" margin={{ left: 40, right: 20 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#a1a1aa' }} />
                  <Tooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', borderColor: 'rgba(255,255,255,0.1)' }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Timeline Line Chart */}
        <Card className="bg-black/40 border-white/10 backdrop-blur-md h-[400px] flex flex-col">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-400" />
              Scan Volume & Risk Detection Timeline
            </CardTitle>
            <CardDescription className="text-zinc-400">Total scans vs High/Prohibited risks detected over the last 6 months.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={scanTimeline} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="month" stroke="#a1a1aa" tickLine={false} axisLine={false} />
                <YAxis stroke="#a1a1aa" tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', borderColor: 'rgba(255,255,255,0.1)' }}
                />
                <Line type="monotone" dataKey="scans" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: "#3b82f6" }} name="Total Scans" />
                <Line type="monotone" dataKey="risksDetected" stroke="#ef4444" strokeWidth={3} dot={{ r: 4, fill: "#ef4444" }} name="Risks Detected" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
