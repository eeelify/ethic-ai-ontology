"use client";

import { useState } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, ShieldAlert, BookOpen, AlertTriangle, FileText, GitBranch, Loader2 } from "lucide-react";
import { toast } from "sonner";
import api from "@/services/api";
import { AnalyzeTextResponse } from "@/types";
import { useRouter } from "next/navigation";

export default function AnalyzerPage() {
  const router = useRouter();
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalyzeTextResponse | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error("Please describe an AI system to analyze.");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post<AnalyzeTextResponse>("/analyze-text", { text });
      setResults(response.data);
      toast.success("Analysis complete.");
    } catch (error) {
      console.error(error);
      toast.error("Failed to analyze text. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical": return "text-red-400 border-red-500/50 bg-red-500/10";
      case "high": return "text-orange-400 border-orange-500/50 bg-orange-500/10";
      case "medium": return "text-yellow-400 border-yellow-500/50 bg-yellow-500/10";
      case "low": return "text-blue-400 border-blue-500/50 bg-blue-500/10";
      default: return "text-zinc-400 border-zinc-500/50 bg-zinc-500/10";
    }
  };

  const getRiskColor = (risk: string) => {
    if (risk.includes("Prohibited")) return "bg-red-500/20 text-red-400 border-red-500/50";
    if (risk.includes("High")) return "bg-orange-500/20 text-orange-400 border-orange-500/50";
    if (risk.includes("Limited")) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/50";
    return "bg-blue-500/20 text-blue-400 border-blue-500/50";
  };

  return (
    <div className="relative min-h-screen py-10 px-4">
      <AnimatedBackground />
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Input Section */}
        <Card className="bg-black/50 backdrop-blur-xl border-white/10 shadow-2xl">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-400" />
              AI System Analyzer
            </CardTitle>
            <CardDescription className="text-zinc-400">
              Describe the AI system&apos;s capabilities, inputs, and purpose to infer regulatory and ethical exposure.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Example: The company uses facial recognition and biometric authentication to monitor employees in public spaces..."
              className="min-h-[150px] bg-white/5 border-white/10 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500/50 text-lg"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <div className="flex flex-wrap gap-3">
              <Button 
                onClick={handleAnalyze} 
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 shadow-[0_0_15px_rgba(37,99,235,0.4)] transition-all"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Activity className="w-4 h-4 mr-2" />}
                Analyze Graph
              </Button>
              <Button 
                variant="outline" 
                className="border-white/10 bg-white/5 hover:bg-white/10 backdrop-blur-md"
                onClick={() => router.push(`/trace?text=${encodeURIComponent(text)}`)}
                disabled={!text}
              >
                <GitBranch className="w-4 h-4 mr-2" />
                Explain Reasoning
              </Button>
              <Button 
                variant="secondary" 
                className="bg-purple-600/20 text-purple-300 border border-purple-500/30 hover:bg-purple-600/30"
                onClick={() => router.push(`/report?text=${encodeURIComponent(text)}`)}
                disabled={!text}
              >
                <FileText className="w-4 h-4 mr-2" />
                Generate Full Report
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        {results && !results.message && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Overview Column */}
            <div className="space-y-6">
              <Card className="bg-black/40 backdrop-blur-md border-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-purple-400" />
                    Detected Categories
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  {results.inferred_categories.map((cat, i) => (
                    <Badge key={i} variant="outline" className="bg-purple-500/10 text-purple-300 border-purple-500/30">
                      {cat}
                    </Badge>
                  ))}
                </CardContent>
              </Card>

              <Card className="bg-black/40 backdrop-blur-md border-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-400" />
                    Risk Classification
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  {results.inferred_risks.map((risk, i) => (
                    <Badge key={i} variant="outline" className={getRiskColor(risk)}>
                      {risk}
                    </Badge>
                  ))}
                </CardContent>
              </Card>

              <Card className="bg-black/40 backdrop-blur-md border-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-blue-400" />
                    Relevant Regulations
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  {results.inferred_regulations.map((reg, i) => (
                    <Badge key={i} variant="outline" className="bg-blue-500/10 text-blue-300 border-blue-500/30">
                      {reg}
                    </Badge>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Ethical Analysis Column */}
            <div className="md:col-span-2 space-y-4">
              <h3 className="text-xl font-semibold flex items-center gap-2 text-white/90">
                <ShieldAlert className="w-5 h-5 text-emerald-400" />
                Ethical Violations & Harms
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {results.ethical_analysis.map((eth, i) => (
                  <Card key={i} className="bg-black/40 backdrop-blur-md border-white/10 overflow-hidden group hover:border-white/20 transition-colors">
                    <div className="p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <h4 className="font-bold text-lg text-white/90">{eth.principle}</h4>
                        <Badge variant="outline" className={`capitalize ${getSeverityColor(eth.severity)}`}>
                          {eth.severity}
                        </Badge>
                      </div>
                      <div className="space-y-2 text-sm">
                        <p className="text-zinc-400">
                          <span className="text-zinc-300 font-medium">Reason:</span> {eth.reason}
                        </p>
                        <p className="text-zinc-400">
                          <span className="text-zinc-300 font-medium">Impact:</span> {eth.impact}
                        </p>
                        <p className="text-zinc-400">
                          <span className="text-zinc-300 font-medium">Harm Type:</span> <span className="text-orange-300">{eth.harm_type}</span>
                        </p>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>

          </div>
        )}

        {results && results.message && (
          <Card className="bg-black/40 border-yellow-500/30">
            <CardContent className="pt-6 text-yellow-200 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              {results.message}
            </CardContent>
          </Card>
        )}

      </div>
    </div>
  );
}
