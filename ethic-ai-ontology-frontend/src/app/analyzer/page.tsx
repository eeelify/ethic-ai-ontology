"use client";

import { useState, useRef } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, ShieldAlert, BookOpen, AlertTriangle, FileText, GitBranch, Loader2, Upload, FileUp, X } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import api from "@/services/api";
import { AnalyzeTextResponse } from "@/types";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function AnalyzerPage() {
  const router = useRouter();
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AnalyzeTextResponse | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    const validFiles: File[] = [];
    for (const file of files) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (extension !== "pdf" && extension !== "docx" && extension !== "doc") {
        toast.error(`Invalid file type: ${file.name}`);
        continue;
      }
      if (file.size > 20 * 1024 * 1024) {
        toast.error(`File too large: ${file.name}`);
        continue;
      }
      validFiles.push(file);
    }

    if (validFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...validFiles]);
      toast.success(`${validFiles.length} file(s) added.`);
    }
  };

  const handleRemoveFile = (indexToRemove: number) => {
    setUploadedFiles(prev => prev.filter((_, idx) => idx !== indexToRemove));
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleAnalyze = async () => {
    if (!text.trim() && uploadedFiles.length === 0) {
      toast.error("Please describe an AI system or upload a file.");
      return;
    }
    setLoading(true);
    try {
      let response;

      if (uploadedFiles.length > 0) {
        const formData = new FormData();
        if (text.trim()) {
          formData.append("text", text);
        }
        uploadedFiles.forEach(file => {
          formData.append("file", file);
        });

        response = await axios.post<AnalyzeTextResponse>(
          `${API_BASE_URL}/analyze-text`,
          formData
        );
      } else {
        response = await api.post<AnalyzeTextResponse>("/analyze-text", { text });
      }

      setResults(response.data);
      toast.success("Analysis complete.");
    } catch (error: any) {
      console.error(error);
      const detail = error?.response?.data?.detail;
      toast.error(detail || "Failed to analyze. Ensure backend is running.");
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
              Describe the AI system&apos;s capabilities, inputs, and purpose — or upload a PDF/Word document for analysis.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Example: The company uses facial recognition and biometric authentication to monitor employees in public spaces..."
              className="min-h-[150px] bg-white/5 border-white/10 text-white placeholder:text-zinc-600 focus-visible:ring-blue-500/50 text-lg"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />

            {/* PDF/Word Upload Area */}
            <div className="space-y-3">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.docx,.doc"
                className="hidden"
                onChange={handleFileChange}
              />

              {uploadedFiles.length === 0 ? (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full group relative flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-white/15 bg-white/[0.03] py-6 px-4 transition-all duration-300 hover:border-blue-400/50 hover:bg-blue-500/[0.06] cursor-pointer"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 ring-1 ring-white/10 group-hover:ring-blue-400/30 transition-all duration-300 group-hover:scale-110">
                    <Upload className="w-5 h-5 text-blue-400 group-hover:text-blue-300 transition-colors" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-semibold text-zinc-300 group-hover:text-white transition-colors">
                      Upload Files (PDF, Word)
                    </p>
                    <p className="text-xs text-zinc-500 mt-1">
                      You can select multiple files
                    </p>
                  </div>
                </button>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-between px-2">
                    <span className="text-sm font-medium text-zinc-300">Uploaded Files ({uploadedFiles.length})</span>
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    >
                      <FileUp className="w-3 h-3" /> Add more
                    </button>
                  </div>
                  <div className="grid gap-2 max-h-[160px] overflow-y-auto pr-1">
                    {uploadedFiles.map((file, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-blue-500/30 bg-blue-500/10 transition-all hover:bg-blue-500/20 group">
                        <div className="flex items-center gap-3 overflow-hidden">
                          <FileUp className="w-5 h-5 text-blue-400 shrink-0" />
                          <div className="flex flex-col truncate">
                            <span className="text-sm font-medium text-blue-100 truncate">{file.name}</span>
                            <span className="text-xs text-blue-400/60">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                          </div>
                        </div>
                        <button
                          onClick={() => handleRemoveFile(idx)}
                          className="p-1.5 rounded-md hover:bg-red-500/20 text-red-400/70 hover:text-red-400 transition-colors shrink-0"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

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
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Composite Score Card */}
            {results.composite_score !== undefined && (
              <div className="mb-6 p-6 rounded-2xl bg-black/60 border border-white/10 flex flex-col md:flex-row items-center gap-8 shadow-2xl backdrop-blur-xl">
                <div className="relative w-32 h-32 flex-shrink-0">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" className="text-white/10" strokeWidth="10" />
                    <circle 
                      cx="50" cy="50" r="45" fill="none" 
                      stroke="currentColor" 
                      strokeWidth="10" 
                      strokeDasharray="283" 
                      strokeDashoffset={283 - (283 * results.composite_score) / 100}
                      className={`transition-all duration-1000 ease-out ${
                        results.composite_score >= 75 ? "text-emerald-500" : 
                        results.composite_score >= 50 ? "text-yellow-500" : 
                        results.composite_score >= 25 ? "text-red-500" : "text-rose-700"
                      }`} 
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold text-white">{results.composite_score}</span>
                    <span className="text-[10px] text-zinc-500 uppercase tracking-widest mt-1">Score</span>
                  </div>
                </div>
                <div className="flex-1 text-center md:text-left">
                  <h3 className="text-2xl font-semibold text-white mb-2">Ethical Reliability Score</h3>
                  <p className="text-zinc-400 text-sm">
                    This score (0-100) evaluates the overall ethical risk and compliance of your AI system. It begins with the Base Risk of your system's domain, applies penalties for specific risk triggers, and grants bonuses for robust safeguards like human oversight and anonymization.
                  </p>
                  <div className="mt-4 flex flex-wrap justify-center md:justify-start gap-2">
                    <Badge variant="outline" className="bg-white/5 border-white/10 text-zinc-300">Initial Risk: {results.initial_risk_level}</Badge>
                    <Badge variant="outline" className="bg-white/5 border-white/10 text-zinc-300">Final Risk: {results.final_risk_level}</Badge>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
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
                    Context-Aware Risk
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-zinc-400 mb-1">Initial Risk (Triggers Only)</p>
                    <Badge variant="outline" className={`text-base py-1 ${getRiskColor(results.initial_risk_level)}`}>
                      {results.initial_risk_level}
                    </Badge>
                  </div>
                  {results.final_risk_level !== results.initial_risk_level ? (
                    <div>
                      <p className="text-sm text-zinc-400 mb-1">Final Risk (After Safeguards)</p>
                      <Badge variant="outline" className={`text-base py-1 ${getRiskColor(results.final_risk_level)}`}>
                        {results.final_risk_level}
                      </Badge>
                      <p className="text-xs text-emerald-400 mt-2">Risk successfully mitigated</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm text-zinc-400 mb-1">Final Risk</p>
                      <Badge variant="outline" className={`text-base py-1 ${getRiskColor(results.final_risk_level)}`}>
                        {results.final_risk_level}
                      </Badge>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="bg-black/40 backdrop-blur-md border-white/10">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-emerald-400" />
                    Detected Safeguards
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-wrap gap-2">
                  {results.detected_safeguards?.length > 0 ? (
                    results.detected_safeguards.map((sg, i) => (
                      <Badge key={i} variant="outline" className="bg-emerald-500/10 text-emerald-300 border-emerald-500/30">
                        {sg}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-sm text-zinc-500">No sufficient safeguards detected.</span>
                  )}
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
