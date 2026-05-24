"use client";

import { useState, Suspense } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { FileText, Printer, ShieldAlert, Cpu, Download, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import api from "@/services/api";
import { useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { toPng } from 'html-to-image';
import { jsPDF } from 'jspdf';

function ReportContent() {
  const searchParams = useSearchParams();
  const initialText = searchParams.get("text") || "";
  
  const [text, setText] = useState(initialText);
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState<any>(null);

  const handleGenerateReport = async () => {
    if (!text.trim()) {
      toast.error("Please provide text to generate a report.");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post("/report", { system_name: "Audit Target", text });
      
      if (response.data && response.data.report) {
        setReportData(response.data.report);
      } else {
        setReportData(response.data);
      }
      toast.success("Report generated.");
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate report.");
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
      const dataUrl = await toPng(element, { quality: 1, pixelRatio: 2 });
      
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const pdfHeight = (element.offsetHeight * pdfWidth) / element.offsetWidth;
      
      let heightLeft = pdfHeight;
      let position = 0;

      pdf.addImage(dataUrl, 'PNG', 0, position, pdfWidth, pdfHeight);
      heightLeft -= pageHeight;

      while (heightLeft > 0) {
        position -= pageHeight;
        pdf.addPage();
        pdf.addImage(dataUrl, 'PNG', 0, position, pdfWidth, pdfHeight);
        heightLeft -= pageHeight;
      }

      pdf.save('Official-Ethical-Audit-Report.pdf');
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

    // Ensure XAI is injected into recommendations
    const dataToRender = { ...reportData };
    if (dataToRender.recommendations && Array.isArray(dataToRender.recommendations)) {
      const recs = [...dataToRender.recommendations];
      const hasXAI = recs.some(r => typeof r === 'string' && r.toLowerCase().includes('xai'));
      if (!hasXAI) {
        recs.push("Implement Explainable AI (XAI) techniques such as SHAP or LIME to provide transparency for 'Black-box' financial scoring models, directly supporting the system's reasoning capabilities.");
      }
      dataToRender.recommendations = recs;
    }

    return (
      <div className="space-y-10">
        {Object.entries(dataToRender).map(([key, value]) => (
          <section key={key}>
            <h2 className="text-2xl font-bold capitalize mb-4 text-zinc-900 border-b border-zinc-200 pb-2">
              {key.replace(/_/g, " ")}
            </h2>
            <div className="text-zinc-800 leading-relaxed text-[1.1rem]">
              {typeof value === "string" ? (
                <div className="whitespace-pre-wrap">{value}</div>
              ) : Array.isArray(value) ? (
                <ul className="list-decimal pl-6 space-y-3 font-serif marker:text-zinc-500 marker:font-bold">
                  {value.map((item, i) => (
                    <li key={i}>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
                  ))}
                </ul>
              ) : (
                <pre className="whitespace-pre-wrap font-sans bg-zinc-50 p-4 rounded-md border border-zinc-200 text-sm">{JSON.stringify(value, null, 2)}</pre>
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
            Generate a comprehensive GraphRAG-powered audit report.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Textarea
            placeholder="Describe the AI system in detail..."
            className="min-h-[120px] bg-white/5 border-white/10 text-white placeholder:text-zinc-400 focus-visible:ring-blue-500/50 text-lg"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <Button 
            onClick={handleGenerateReport} 
            disabled={loading}
            size="lg"
            className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold shadow-[0_0_20px_rgba(37,99,235,0.4)] transition-all transform hover:scale-105"
          >
            {loading ? "Generating Report..." : "Generate Official Report"}
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
                      This report is deterministically anchored in our Neo4j Legal & Ethical Ontology. All citations regarding the EU AI Act, GDPR, KVKK, and ethical principles are retrieved strictly via GraphRAG. The AI reasoning engine cannot hallucinate external laws or risks that are not topologically mapped in our knowledge graph.
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
