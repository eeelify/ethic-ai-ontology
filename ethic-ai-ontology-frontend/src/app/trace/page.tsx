"use client";

import { useState, useEffect, Suspense } from "react";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { GitBranch, Loader2, Play } from "lucide-react";
import { toast } from "sonner";
import api from "@/services/api";
import { GraphTraceResponse } from "@/types";
import { useSearchParams } from "next/navigation";
import { ReactFlow, Background, Controls, MiniMap, Node, Edge, MarkerType } from "@xyflow/react";
import '@xyflow/react/dist/style.css';

const NODE_COLORS: Record<string, string> = {
  keyword_match: "#06b6d4",       // cyan
  mapped_category: "#a855f7",     // purple
  risk_inference: "#ef4444",      // red
  regulation_inference: "#3b82f6",// blue
  ethical_principle: "#10b981",   // green
  harm_type: "#f97316"            // orange
};

function TraceContent() {
  const searchParams = useSearchParams();
  const initialText = searchParams.get("text") || "";
  
  const [text, setText] = useState(initialText);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<GraphTraceResponse | null>(null);

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  useEffect(() => {
    if (initialText) {
      handleTrace(initialText);
    }
  }, [initialText]);

  const handleTrace = async (txtToAnalyze = text) => {
    if (!txtToAnalyze.trim()) {
      toast.error("Please provide text to trace.");
      return;
    }
    setLoading(true);
    try {
      const response = await api.post<GraphTraceResponse>("/graph-trace", { text: txtToAnalyze });
      setResults(response.data);
      buildGraph(response.data.trace);
      toast.success("Graph trace complete.");
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate trace.");
    } finally {
      setLoading(false);
    }
  };

  const buildGraph = (trace: { step: string; value: string }[]) => {
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];

    // Grouping by step types to layout them horizontally
    // 0: keyword, 1: category, 2: risk, 3: reg, 4: principle, 5: harm
    const levels: Record<string, number> = {
      keyword_match: 0,
      mapped_category: 1,
      risk_inference: 2,
      regulation_inference: 3,
      ethical_principle: 4,
      harm_type: 5
    };

    const levelCounts = [0,0,0,0,0,0];
    let prevNodeId: string | null = null;

    trace.forEach((t, i) => {
      const level = levels[t.step] !== undefined ? levels[t.step] : 0;
      const x = level * 250 + 50;
      const y = levelCounts[level] * 100 + 50;
      levelCounts[level]++;

      const nodeId = `node-${i}`;

      newNodes.push({
        id: nodeId,
        position: { x, y },
        data: { 
          label: (
            <div className="flex flex-col items-center">
              <span className="text-[10px] uppercase font-bold opacity-70 mb-1">{t.step.replace('_', ' ')}</span>
              <span className="font-semibold text-sm">{t.value}</span>
            </div>
          ) 
        },
        style: {
          background: "rgba(0,0,0,0.8)",
          color: "#fff",
          border: `2px solid ${NODE_COLORS[t.step] || "#fff"}`,
          borderRadius: "8px",
          padding: "10px",
          minWidth: "150px",
          boxShadow: `0 0 15px ${NODE_COLORS[t.step]}40`
        }
      });

      if (prevNodeId) {
        newEdges.push({
          id: `e-${prevNodeId}-${nodeId}`,
          source: prevNodeId,
          target: nodeId,
          animated: true,
          style: { stroke: "#4b5563", strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#4b5563" },
        });
      }
      prevNodeId = nodeId;
    });

    setNodes(newNodes);
    setEdges(newEdges);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <Card className="bg-black/50 backdrop-blur-xl border-white/10">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <GitBranch className="w-6 h-6 text-purple-400" />
            Explainable Graph Trace
          </CardTitle>
          <CardDescription className="text-zinc-400">
            See the deterministic reasoning chain that powers the AI evaluation.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Textarea
              placeholder="System description..."
              className="flex-1 min-h-[60px] bg-white/5 border-white/10 text-white placeholder:text-zinc-600 focus-visible:ring-purple-500/50"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
            <Button 
              onClick={() => handleTrace()} 
              disabled={loading}
              className="h-auto bg-purple-600 hover:bg-purple-700 shadow-[0_0_15px_rgba(147,51,234,0.4)] transition-all px-8"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 mr-2" />}
              Trace
            </Button>
          </div>
        </CardContent>
      </Card>

      {nodes.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-in fade-in duration-500 h-[600px]">
          {/* React Flow Map */}
          <Card className="lg:col-span-3 bg-black/40 border-white/10 overflow-hidden relative">
            <ReactFlow 
              nodes={nodes} 
              edges={edges}
              fitView
              className="dark"
            >
              <Background color="#333" gap={16} />
              <Controls />
              <MiniMap style={{ backgroundColor: "#111", border: "1px solid #333" }} nodeColor={(n) => n.style?.borderColor as string || "#fff"} />
            </ReactFlow>
          </Card>

          {/* Reasoning Timeline Sidebar */}
          <Card className="bg-black/40 border-white/10 overflow-hidden flex flex-col">
            <CardHeader className="border-b border-white/10 bg-white/5">
              <CardTitle className="text-lg">Reasoning Timeline</CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-y-auto flex-1">
              <div className="p-4 space-y-4 relative">
                <div className="absolute left-[27px] top-4 bottom-4 w-[2px] bg-white/10" />
                {results?.trace.map((step, idx) => (
                  <div key={idx} className="relative flex items-start gap-4">
                    <div 
                      className="w-4 h-4 rounded-full mt-1 shrink-0 z-10"
                      style={{ backgroundColor: NODE_COLORS[step.step] || "#fff" }}
                    />
                    <div>
                      <p className="text-xs text-zinc-500 uppercase font-semibold">{step.step.replace('_', ' ')}</p>
                      <p className="text-sm text-white/90 font-medium">{step.value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export default function TracePage() {
  return (
    <div className="relative min-h-screen py-10 px-4">
      <AnimatedBackground />
      <Suspense fallback={<div>Loading trace...</div>}>
        <TraceContent />
      </Suspense>
    </div>
  );
}
