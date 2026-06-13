"use client";

import { useState } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Activity, ShieldAlert, Cpu, Lock, FileText, CheckCircle, Scale, AlertTriangle, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import api from "@/services/api";

export default function AssessPage() {
  const [systemName, setSystemName] = useState("");
  const [ethicalScore, setEthicalScore] = useState<number>(0);
  const [legalScore, setLegalScore] = useState<number>(0);
  const [dataScore, setDataScore] = useState<number>(0);
  const [technicalScore, setTechnicalScore] = useState<number>(0);
  const [oversightScore, setOversightScore] = useState<number>(0);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAssess = async () => {
    if (!systemName.trim()) {
      toast.error("Please enter a valid System Name.");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/assess", {
        system_name: systemName,
        ethical_score: ethicalScore,
        legal_score: legalScore,
        data_score: dataScore,
        technical_score: technicalScore,
        oversight_score: oversightScore
      });
      setResult(response.data);
      toast.success("Risk composite calculated and saved to Neo4j successfully.");
    } catch (error: any) {
      console.error(error);
      const detail = error?.response?.data?.detail;
      toast.error(detail || "Assessment failed. Check if system exists in Neo4j.");
    } finally {
      setLoading(false);
    }
  };

  const ScoreInput = ({ 
    label, 
    value, 
    setValue, 
    icon: Icon, 
    color,
    weight
  }: { 
    label: string, 
    value: number, 
    setValue: (v: number) => void, 
    icon: any, 
    color: string,
    weight: string
  }) => (
    <div className="space-y-3 bg-white/5 p-4 rounded-xl border border-white/10 hover:bg-white/10 transition-colors group">
      <div className="flex justify-between items-center">
        <label className="text-zinc-300 font-medium flex items-center gap-2">
          <Icon className={`w-4 h-4 ${color}`} />
          {label}
        </label>
        <Badge variant="outline" className="bg-white/5 border-white/10 text-zinc-400">
          Weight: {weight}
        </Badge>
      </div>
      <div className="flex items-center gap-4">
        <input
          type="range"
          min="0"
          max="100"
          value={value}
          onChange={(e) => setValue(Number(e.target.value))}
          className={`flex-1 h-2 rounded-lg appearance-none cursor-pointer bg-white/10 accent-${color.split('-')[1]}-500`}
        />
        <div className={`w-14 text-center font-bold text-xl ${color}`}>
          {value}
        </div>
      </div>
    </div>
  );

  const getRiskColor = (risk: string) => {
    if (risk.includes("Prohibited") || risk.includes("Unacceptable")) return "bg-red-500/20 text-red-400 border-red-500/50";
    if (risk.includes("High")) return "bg-orange-500/20 text-orange-400 border-orange-500/50";
    if (risk.includes("Limited")) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50";
    return "bg-blue-500/20 text-blue-400 border-blue-500/50";
  };

  return (
    <div className="relative min-h-screen py-10 px-4">
      <AnimatedBackground />
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col items-center text-center space-y-2 mb-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center mb-2 shadow-lg shadow-purple-500/10">
            <Activity className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 tracking-tight">
            Composite Risk Calculator
          </h1>
          <p className="text-zinc-400 max-w-2xl text-lg">
            Evaluate your AI system against 5 core risk vectors. The composite score is mathematically calculated based on strict ontology weightings and persisted instantly to the Neo4j Knowledge Graph.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
            <Card className="bg-black/50 backdrop-blur-xl border-white/10 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-xl flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-blue-400" />
                  Assessment Metrics
                </CardTitle>
                <CardDescription className="text-zinc-400">
                  Adjust the scores (0-100) for each vector.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-zinc-300">Target AI System Name</label>
                  <input
                    type="text"
                    value={systemName}
                    onChange={(e) => setSystemName(e.target.value)}
                    placeholder="e.g. HiringAI"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  />
                </div>

                <div className="space-y-4 pt-4 border-t border-white/10">
                  <ScoreInput 
                    label="Ethical Impact Score" 
                    value={ethicalScore} 
                    setValue={setEthicalScore} 
                    icon={ShieldAlert} 
                    color="text-purple-400"
                    weight="25%" 
                  />
                  <ScoreInput 
                    label="Legal Compliance Score" 
                    value={legalScore} 
                    setValue={setLegalScore} 
                    icon={Scale} 
                    color="text-blue-400"
                    weight="25%" 
                  />
                  <ScoreInput 
                    label="Data Sensitivity Score" 
                    value={dataScore} 
                    setValue={setDataScore} 
                    icon={Database} 
                    color="text-emerald-400"
                    weight="20%" 
                  />
                  <ScoreInput 
                    label="Technical Robustness Score" 
                    value={technicalScore} 
                    setValue={setTechnicalScore} 
                    icon={Cpu} 
                    color="text-orange-400"
                    weight="15%" 
                  />
                  <ScoreInput 
                    label="Human Oversight Score" 
                    value={oversightScore} 
                    setValue={setOversightScore} 
                    icon={CheckCircle} 
                    color="text-pink-400"
                    weight="15%" 
                  />
                </div>

                <Button
                  onClick={handleAssess}
                  disabled={loading}
                  size="lg"
                  className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all transform hover:scale-[1.02]"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Calculating Risk & Updating Graph...
                    </>
                  ) : (
                    "Calculate Composite Risk"
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>

          {/* Results Section */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.2 }}>
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-6"
                >
                  <Card className="bg-black/60 backdrop-blur-2xl border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] overflow-hidden relative">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />
                    <CardHeader className="pb-4">
                      <CardTitle className="text-2xl text-white">Assessment Results</CardTitle>
                      <CardDescription className="text-zinc-400">
                        Graph topology successfully updated for <span className="font-bold text-white">{result.system}</span>.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-8">
                      
                      <div className="flex flex-col items-center justify-center py-6 bg-white/5 rounded-2xl border border-white/5 shadow-inner">
                        <span className="text-zinc-400 text-sm uppercase tracking-widest font-semibold mb-2">Composite Risk Score</span>
                        <div className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-zinc-500">
                          {result.composite_risk_score?.toFixed(1)}
                        </div>
                        <Badge className={`mt-4 px-4 py-1.5 text-sm uppercase tracking-wider ${getRiskColor(result.risk_level)}`}>
                          {result.risk_level}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                          <span className="text-xs text-zinc-500 uppercase font-bold block mb-1">ERC Level</span>
                          <span className="text-lg font-bold text-zinc-200">{result.erc_level} ({result.erc_score})</span>
                        </div>
                        <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                          <span className="text-xs text-zinc-500 uppercase font-bold block mb-1">Violations</span>
                          <span className="text-lg font-bold text-red-400">{result.violated_principles?.length || 0} Principles</span>
                        </div>
                      </div>

                      <div className="bg-white/5 p-4 rounded-xl border border-white/10 text-sm text-zinc-300 leading-relaxed font-serif">
                        {result.summary}
                      </div>

                      <div className="pt-4 flex justify-end gap-3">
                        <Button variant="outline" className="border-white/10 text-zinc-300 hover:text-white" onClick={() => window.open(`/trace?text=${encodeURIComponent(systemName)}`, '_blank')}>
                          View Knowledge Graph
                        </Button>
                        <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold" onClick={() => window.open(`/report?system_name=${encodeURIComponent(systemName)}`, '_blank')}>
                          Generate Audit Report
                        </Button>
                      </div>

                    </CardContent>
                  </Card>
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="h-full flex flex-col items-center justify-center text-center p-12 border-2 border-dashed border-white/10 rounded-2xl bg-white/[0.02]"
                >
                  <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
                    <AlertTriangle className="w-10 h-10 text-zinc-600" />
                  </div>
                  <h3 className="text-xl font-bold text-zinc-400 mb-2">No Assessment Data</h3>
                  <p className="text-zinc-500 max-w-sm">
                    Enter the system parameters and hit calculate to evaluate the composite risk matrix.
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>

      </div>
    </div>
  );
}

// Quick stub for Database icon since it's used
function Database(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5V19A9 3 0 0 0 21 19V5" />
      <path d="M3 12A9 3 0 0 0 21 12" />
    </svg>
  )
}
