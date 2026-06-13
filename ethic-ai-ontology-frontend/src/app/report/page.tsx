"use client";

import { useState, useRef, Suspense } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { FileText, Printer, ShieldAlert, Cpu, Download, CheckCircle, Upload, X, FileUp, Loader2, Scale } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function ReportContent() {
  const searchParams = useSearchParams();
  const initialText = searchParams.get("text") || "";
  const initialSystemName = searchParams.get("system_name") || "";

  const [text, setText] = useState(initialText);
  const [systemName, setSystemName] = useState(initialSystemName);
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<any>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const extension = file.name.split('.').pop()?.toLowerCase();
    if (extension !== "pdf" && extension !== "docx" && extension !== "doc") {
      toast.error("Only PDF and Word (.docx, .doc) files can be uploaded.");
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      toast.error("File size must be less than 20MB.");
      return;
    }

    setUploadedFile(file);
    toast.success(`"${file.name}" uploaded.`);
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleGenerateReport = async () => {
    if (!text.trim() && !uploadedFile && !systemName.trim()) {
      toast.error("Please enter a system name, description text, or upload a file.");
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("system_name", systemName.trim() || "Audit Target");
      if (text.trim()) {
        formData.append("text", text);
      }
      if (uploadedFile) {
        formData.append("file", uploadedFile);
      }

      const response = await axios.post(`${API_BASE_URL}/report`, formData);

      if (response.data && response.data.report) {
        setReportData(response.data.report);
      } else {
        setReportData(response.data);
      }
      toast.success("Report generated.");
    } catch (error: any) {
      console.error(error);
      const detail = error?.response?.data?.detail;
      toast.error(detail || "Failed to generate report.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    const element = document.getElementById('report-container');
    if (!element) return;

    const actionContainer = document.getElementById('report-actions');
    if (actionContainer) actionContainer.style.display = 'none';

    try {
      const html2pdf = (await import('html2pdf.js')).default;
      
      const opt = {
        margin:       15, // 15mm margins
        filename:     'Official-Ethical-Audit-Report.pdf',
        image:        { type: 'jpeg', quality: 1 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
      };

      await html2pdf().set(opt).from(element).save();
    } catch (err) {
      console.error("PDF generation failed", err);
      toast.error("Failed to generate PDF. Falling back to print.");
      window.print();
    } finally {
      if (actionContainer) actionContainer.style.display = 'flex';
    }
  };

  const renderReportContent = () => {
    if (!reportData) return null;

    if (typeof reportData === "string") {
      return <div className="whitespace-pre-wrap leading-relaxed text-zinc-800">{reportData}</div>;
    }

    const {
      executive_summary,
      risk_assessment,
      composite_risk_score,
      risk_level,
      score_components,
      risk_threshold_explanation,
      ethical_analysis,
      ethical_tensions,
      legal_compliance,
      recommendations,
      citation_sources,
      ...otherFields
    } = reportData;

    const getRiskColorClass = (risk: string) => {
      const r = (risk || "").toLowerCase();
      if (r.includes("unacceptable") || r.includes("prohibited")) return { text: "text-red-600", bg: "bg-red-50", border: "border-red-200", fill: "fill-red-600", accent: "accent-red-600" };
      if (r.includes("high")) return { text: "text-orange-600", bg: "bg-orange-50", border: "border-orange-200", fill: "fill-orange-600", accent: "accent-orange-600" };
      if (r.includes("limited") || r.includes("medium")) return { text: "text-yellow-600", bg: "bg-yellow-50", border: "border-yellow-200", fill: "fill-yellow-600", accent: "accent-yellow-600" };
      return { text: "text-blue-600", bg: "bg-blue-50", border: "border-blue-200", fill: "fill-blue-600", accent: "accent-blue-600" };
    };

    const riskColors = getRiskColorClass(risk_level);

    // Make sure recommendations exist & contain explainability details if missing
    let finalRecommendations = recommendations;
    if (finalRecommendations && Array.isArray(finalRecommendations)) {
      const recs = [...finalRecommendations];
      const hasXAI = recs.some(r => typeof r === 'string' && r.toLowerCase().includes('xai'));
      if (!hasXAI) {
        recs.push("Implement Explainable AI (XAI) techniques such as SHAP or LIME to provide transparency for 'Black-box' financial scoring models, directly supporting the system's reasoning capabilities.");
      }
      finalRecommendations = recs;
    }

    return (
      <div className="space-y-8 font-sans">
        {/* Composite Score and Risk Level Overview */}
        {composite_risk_score !== undefined && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 print:block">
            {/* Big Score Card */}
            <div className={`p-6 rounded-2xl border ${riskColors.border} ${riskColors.bg} flex flex-col items-center justify-center text-center shadow-sm`}>
              <span className="text-zinc-500 text-xs font-bold uppercase tracking-wider mb-2">Composite Risk Score</span>
              <div className={`text-6xl font-black ${riskColors.text}`}>
                {typeof composite_risk_score === 'number' ? composite_risk_score.toFixed(1) : composite_risk_score}
              </div>
              <div className={`mt-3 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${riskColors.border} bg-white shadow-sm inline-block`}>
                {risk_level || "Assessed Risk"}
              </div>
            </div>

            {/* Score Components Progress Bars */}
            <div className="md:col-span-2 p-6 rounded-2xl border border-zinc-200 bg-zinc-50/50 space-y-4">
              <h3 className="text-zinc-800 font-bold text-sm uppercase tracking-wider mb-3">Assessment Vector Scores</h3>
              {score_components ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
                  {Object.entries(score_components).map(([compName, compVal]: [string, any]) => {
                    const formattedName = compName.replace(/_(score|val)/g, "").replace(/_/g, " ");
                    const valNum = Number(compVal) || 0;
                    return (
                      <div key={compName} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium text-zinc-600">
                          <span className="capitalize">{formattedName}</span>
                          <span className="font-bold text-zinc-800">{valNum}%</span>
                        </div>
                        <div className="h-1.5 w-full bg-zinc-200 rounded-full overflow-hidden">
                          <div className={`h-full bg-zinc-700 rounded-full`} style={{ width: `${valNum}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-zinc-400 text-sm">No component score breakdown available.</div>
              )}
            </div>
          </div>
        )}

        {/* Risk Threshold Explanation */}
        {risk_threshold_explanation && (
          <div className="p-5 bg-zinc-50 border border-zinc-200 rounded-xl">
            <h4 className="text-xs uppercase font-bold text-zinc-500 tracking-wider mb-1">Risk Classification Logic</h4>
            <p className="text-zinc-700 text-sm leading-relaxed m-0 font-serif">{risk_threshold_explanation}</p>
          </div>
        )}

        {/* Executive Summary */}
        {executive_summary && (
          <section className="space-y-3">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 flex items-center gap-2">
              <FileText className="w-5 h-5 text-zinc-600" />
              Executive Summary
            </h3>
            <p className="text-zinc-800 leading-relaxed font-serif text-[1.05rem]">{executive_summary}</p>
          </section>
        )}

        {/* Risk Assessment */}
        {risk_assessment && (
          <section className="space-y-3">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-zinc-600" />
              Risk Assessment &amp; Justification
            </h3>
            <p className="text-zinc-800 leading-relaxed font-serif text-[1.05rem]">{risk_assessment}</p>
          </section>
        )}

        {/* Ethical Analysis */}
        {ethical_analysis && (
          <section className="space-y-3">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-zinc-600" />
              Ethical Analysis &amp; Principle Tensions
            </h3>
            <p className="text-zinc-800 leading-relaxed font-serif text-[1.05rem]">{ethical_analysis}</p>
          </section>
        )}

        {/* Ethical Tensions */}
        {ethical_tensions && Array.isArray(ethical_tensions) && ethical_tensions.length > 0 && (
          <section className="space-y-3">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 flex items-center gap-2">
              <Scale className="w-5 h-5 text-zinc-600" />
              Identified Ethical Tensions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
              {ethical_tensions.map((tensionItem: any, idx: number) => (
                <div key={idx} className="p-4 rounded-xl border border-zinc-200 bg-white shadow-sm flex flex-col gap-2">
                  <div className="text-sm font-bold text-zinc-800 uppercase tracking-wide flex items-center gap-2">
                    <Scale className="w-4 h-4 text-orange-500" />
                    {tensionItem.tension || tensionItem.name || "Unknown Tension"}
                  </div>
                  <p className="text-zinc-600 text-sm leading-relaxed m-0">
                    {tensionItem.description || tensionItem}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Legal Compliance */}
        {legal_compliance && (
          <section className="space-y-3">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-zinc-600" />
              Legal Compliance &amp; Regulatory Context
            </h3>
            <p className="text-zinc-800 leading-relaxed font-serif text-[1.05rem]">{legal_compliance}</p>
          </section>
        )}

        {/* Recommendations */}
        {finalRecommendations && Array.isArray(finalRecommendations) && (
          <section className="space-y-3">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-zinc-600" />
              Strategic Recommendations
            </h3>
            <ul className="list-decimal pl-6 space-y-2.5 font-serif marker:text-zinc-500 marker:font-bold">
              {finalRecommendations.map((rec, i) => (
                <li key={i} className="text-zinc-800 leading-relaxed text-[1.05rem]">
                  {typeof rec === 'string' ? rec : JSON.stringify(rec)}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Citation Sources */}
        {citation_sources && Array.isArray(citation_sources) && (
          <section className="space-y-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-500 border-b border-zinc-200 pb-1.5">
              Citations &amp; Legal References
            </h3>
            <div className="flex flex-wrap gap-2 pt-1">
              {citation_sources.map((src, i) => (
                <span key={i} className="bg-zinc-100 border border-zinc-200 text-zinc-700 px-2.5 py-1 rounded-md text-xs font-mono">
                  {src}
                </span>
              ))}
            </div>
          </section>
        )}

        {/* Other properties that might be returned */}
        {Object.entries(otherFields).map(([key, value]) => (
          <section key={key} className="space-y-2">
            <h3 className="text-xl font-bold text-zinc-900 border-b border-zinc-200 pb-2 capitalize">
              {key.replace(/_/g, " ")}
            </h3>
            <div className="text-zinc-800 leading-relaxed text-[1.05rem]">
              {typeof value === "string" ? (
                <div className="whitespace-pre-wrap">{value}</div>
              ) : Array.isArray(value) ? (
                <ul className="list-decimal pl-6 space-y-2 font-serif">
                  {value.map((item, i) => (
                    <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                  ))}
                </ul>
              ) : (
                <pre className="whitespace-pre-wrap font-sans bg-zinc-50 p-4 rounded-md border border-zinc-200 text-sm">
                  {JSON.stringify(value, null, 2)}
                </pre>
              )}
            </div>
          </section>
        ))}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-4xl mx-auto space-y-6 print:m-0 print:p-0"
    >
      {/* Configuration Section - hidden during print */}
      <Card className="bg-black/40 backdrop-blur-xl border-white/10 print:hidden shadow-2xl">
        <CardHeader>
          <CardTitle className="text-3xl font-extrabold flex items-center gap-3 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            <FileText className="w-8 h-8 text-blue-400" />
            AI Ethics Audit Report Generator
          </CardTitle>
          <CardDescription className="text-zinc-400 text-lg">
            Generate a comprehensive GraphRAG-powered audit report from text, PDF, or Word documents.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-300">Target AI System Name (Optional)</label>
            <input
              type="text"
              value={systemName}
              onChange={(e) => setSystemName(e.target.value)}
              placeholder="e.g. HiringAI (to load its graph topology and risk scores)"
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all text-lg"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-300">System Description (Optional)</label>
            <Textarea
              placeholder="Describe the AI system's functionality and context..."
              className="min-h-[100px] bg-white/5 border-white/10 text-white placeholder:text-zinc-400 focus-visible:ring-blue-500/50 text-lg"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          {/* Upload Area */}
          <div className="space-y-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.doc"
              className="hidden"
              onChange={handleFileChange}
            />

            {!uploadedFile ? (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full group relative flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-white/15 bg-white/[0.03] py-8 px-4 transition-all duration-300 hover:border-blue-400/50 hover:bg-blue-500/[0.06] cursor-pointer"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 ring-1 ring-white/10 group-hover:ring-blue-400/30 transition-all duration-300 group-hover:scale-110">
                  <Upload className="w-6 h-6 text-blue-400 group-hover:text-blue-300 transition-colors" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-semibold text-zinc-300 group-hover:text-white transition-colors">
                    Upload File (PDF, Word)
                  </p>
                  <p className="text-xs text-zinc-500 mt-1">
                    Drag-and-drop or click · Max 20MB
                  </p>
                </div>
              </button>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center justify-between rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-4"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/20 shrink-0">
                    <FileUp className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-emerald-300 truncate">
                      {uploadedFile.name}
                    </p>
                    <p className="text-xs text-emerald-500/80">
                      {(uploadedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-red-500/20 transition-colors group"
                >
                  <X className="w-4 h-4 text-zinc-400 group-hover:text-red-400 transition-colors" />
                </button>
              </motion.div>
            )}
          </div>

          {!uploadedFile && text.trim() === "" && (
            <div className="flex items-center gap-4">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-xs text-zinc-500 uppercase tracking-wider font-medium">or use together</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>
          )}

          <Button
            onClick={handleGenerateReport}
            disabled={loading}
            size="lg"
            className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all transform hover:scale-105"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generating Report...
              </>
            ) : (
              "Generate Official Report"
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Report View */}
      <AnimatePresence>
        {reportData && (
          <motion.div
            initial={{ opacity: 0, height: 0, scale: 0.95 }}
            animate={{ opacity: 1, height: "auto", scale: 1 }}
            transition={{ duration: 0.6, type: "spring", bounce: 0.4 }}
          >
            <Card id="report-container" className="bg-white text-black border-zinc-200 print:shadow-none print:border-none print:bg-transparent overflow-hidden shadow-2xl">
              <CardHeader className="border-b border-zinc-200 bg-zinc-50/80 print:bg-transparent flex flex-row justify-between items-center py-6">
                <div>
                  <CardTitle className="text-3xl font-serif text-zinc-900 flex items-center gap-3">
                    <ShieldAlert className="w-8 h-8 text-red-600" />
                    Official Ethical Audit Report
                  </CardTitle>
                  <CardDescription className="text-zinc-500 mt-2 text-sm font-serif">
                    Generated by AuraGovernance GraphRAG Engine
                  </CardDescription>
                </div>
                <div id="report-actions" className="flex gap-2 print:hidden">
                  <Button onClick={handleDownload} className="bg-blue-600 text-white hover:bg-blue-700 font-bold shadow-[0_0_15px_rgba(37,99,235,0.4)] transition-all transform hover:scale-105">
                    <Download className="w-5 h-5 mr-2" />
                    Download PDF
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="p-10 print:p-0 space-y-8">
                {/* Anti-Hallucination Disclaimer */}
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6 flex items-start gap-4">
                  <div className="bg-emerald-100 p-2 rounded-full shrink-0">
                    <CheckCircle className="w-6 h-6 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="text-emerald-800 font-bold text-lg m-0">Zero-Hallucination Guarantee</h3>
                    <p className="text-emerald-700 text-sm mt-2 mb-0 leading-relaxed font-serif">
                      This report is deterministically anchored in our Neo4j Legal &amp; Ethical Ontology. All citations regarding the EU AI Act, GDPR, KVKK, and ethical principles are retrieved strictly via GraphRAG. The AI reasoning engine cannot hallucinate external laws or risks that are not topologically mapped in our knowledge graph.
                    </p>
                  </div>
                </div>

                <div className="prose prose-zinc prose-lg max-w-none font-serif">
                  {renderReportContent()}
                </div>

                {/* Footer for print */}
                <div className="hidden print:block mt-20 pt-8 border-t border-zinc-300 text-center text-sm text-zinc-500 font-serif">
                  AuraGovernance - Official Generated Record - {new Date().toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ReportPage() {
  return (
    <div className="relative min-h-screen py-10 px-4 print:py-0 print:bg-white print:text-black">
      <div className="print:hidden">
        <AnimatedBackground />
      </div>
      <Suspense fallback={<div className="text-zinc-400 text-center mt-20">Loading report interface...</div>}>
        <ReportContent />
      </Suspense>
    </div>
  );
}
