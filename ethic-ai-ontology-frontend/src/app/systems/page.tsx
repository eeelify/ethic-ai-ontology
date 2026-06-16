"use client";

import { useEffect, useState } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Activity, ShieldAlert, FileText, ChevronRight, Loader2, Database } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import api from "@/services/api";

type SystemData = {
  name: string;
  composite_risk_score?: number;
  risk_level?: string;
};

export default function SystemsPage() {
  const router = useRouter();
  const [systems, setSystems] = useState<SystemData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystems();
  }, []);

  const fetchSystems = async () => {
    try {
      setLoading(true);
      const res = await api.get("/systems");
      setSystems(res.data);
    } catch (err) {
      console.error(err);
      toast.error("Failed to fetch systems from Neo4j.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk?: string) => {
    if (!risk) return "bg-zinc-500/20 text-zinc-400 border-zinc-500/50";
    if (risk.includes("Prohibited") || risk.includes("Unacceptable")) return "bg-red-500/20 text-red-400 border-red-500/50";
    if (risk.includes("High")) return "bg-orange-500/20 text-orange-400 border-orange-500/50";
    if (risk.includes("Limited")) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50";
    if (risk.includes("Minimal")) return "bg-blue-500/20 text-blue-400 border-blue-500/50";
    return "bg-zinc-500/20 text-zinc-400 border-zinc-500/50";
  };

  return (
    <div className="relative min-h-screen py-10 px-4">
      <AnimatedBackground />
      <div className="max-w-7xl mx-auto space-y-8">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Database className="w-8 h-8 text-indigo-400" />
              Evaluated Systems (History)
            </h1>
            <p className="text-zinc-400 mt-2">
              Browse previously assessed AI systems stored in the Neo4j Knowledge Graph.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
          </div>
        ) : systems.length === 0 ? (
          <Card className="bg-black/40 border-white/10 backdrop-blur-md">
            <CardContent className="flex flex-col items-center justify-center py-20 text-center">
              <ShieldAlert className="w-12 h-12 text-zinc-500 mb-4" />
              <p className="text-zinc-300 text-lg">No AI systems found.</p>
              <p className="text-zinc-500 text-sm mt-1">Start by analyzing a system or running a manual assessment.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systems.map((sys, idx) => (
              <Card key={idx} className="bg-black/40 border-white/10 backdrop-blur-md hover:border-indigo-500/50 transition-all group">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-xl text-white/90 group-hover:text-white transition-colors line-clamp-1">
                      {sys.name}
                    </CardTitle>
                    {sys.composite_risk_score !== undefined && sys.composite_risk_score !== null && (
                      <div className="flex flex-col items-end">
                        <span className="text-xs text-zinc-500 uppercase">Composite Score</span>
                        <span className="text-2xl font-bold text-indigo-400">
                          {sys.composite_risk_score}
                        </span>
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Badge variant="outline" className={getRiskColor(sys.risk_level)}>
                      {sys.risk_level || "No Risk Data"}
                    </Badge>
                  </div>
                  <div className="pt-2 flex gap-2">
                    <Button 
                      variant="outline" 
                      className="w-full bg-white/5 border-white/10 hover:bg-white/10"
                      onClick={() => router.push(`/report?system_name=${encodeURIComponent(sys.name)}`)}
                    >
                      <FileText className="w-4 h-4 mr-2 text-indigo-400" />
                      View Full Report
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
