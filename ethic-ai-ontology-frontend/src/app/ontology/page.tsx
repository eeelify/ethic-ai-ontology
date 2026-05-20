"use client";

import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Database, Filter, Layers, Network } from "lucide-react";
import { ReactFlow, Background, Controls, MiniMap, Node, Edge, MarkerType } from "@xyflow/react";
import '@xyflow/react/dist/style.css';
import { useState } from "react";

// Initial Demo Ontology Data
const initialNodes: Node[] = [
  // Categories
  { id: "c1", position: { x: 400, y: 300 }, data: { label: "BiometricAI" }, style: { background: "#a855f7", color: "#fff", padding: 10, borderRadius: 8 } },
  { id: "c2", position: { x: 400, y: 500 }, data: { label: "HiringAI" }, style: { background: "#a855f7", color: "#fff", padding: 10, borderRadius: 8 } },
  
  // Risks
  { id: "r1", position: { x: 700, y: 250 }, data: { label: "ProhibitedRisk" }, style: { background: "#ef4444", color: "#fff", padding: 10, borderRadius: 8 } },
  { id: "r2", position: { x: 700, y: 550 }, data: { label: "HighRisk" }, style: { background: "#f97316", color: "#fff", padding: 10, borderRadius: 8 } },

  // Regulations
  { id: "reg1", position: { x: 100, y: 200 }, data: { label: "EU AI Act Art. 5" }, style: { background: "#3b82f6", color: "#fff", padding: 10, borderRadius: 8 } },
  { id: "reg2", position: { x: 100, y: 400 }, data: { label: "GDPR Art. 9" }, style: { background: "#3b82f6", color: "#fff", padding: 10, borderRadius: 8 } },
  { id: "reg3", position: { x: 100, y: 600 }, data: { label: "GDPR Art. 22" }, style: { background: "#3b82f6", color: "#fff", padding: 10, borderRadius: 8 } },

  // Principles
  { id: "p1", position: { x: 700, y: 350 }, data: { label: "Privacy" }, style: { background: "#10b981", color: "#fff", padding: 10, borderRadius: 8 } },
  { id: "p2", position: { x: 700, y: 450 }, data: { label: "Fairness" }, style: { background: "#10b981", color: "#fff", padding: 10, borderRadius: 8 } },
];

const initialEdges: Edge[] = [
  // Risks
  { id: "e-c1-r1", source: "c1", target: "r1", label: "HAS_RISK", animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#ef4444" }, style: { stroke: "#ef4444" } },
  { id: "e-c2-r2", source: "c2", target: "r2", label: "HAS_RISK", animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" }, style: { stroke: "#f97316" } },
  
  // Regulations
  { id: "e-c1-reg1", source: "c1", target: "reg1", label: "RELATED_TO_REGULATION", markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" }, style: { stroke: "#3b82f6" } },
  { id: "e-c1-reg2", source: "c1", target: "reg2", label: "RELATED_TO_REGULATION", markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" }, style: { stroke: "#3b82f6" } },
  { id: "e-c2-reg3", source: "c2", target: "reg3", label: "RELATED_TO_REGULATION", markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" }, style: { stroke: "#3b82f6" } },

  // Principles
  { id: "e-c1-p1", source: "c1", target: "p1", label: "IMPACTS_PRINCIPLE", animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" }, style: { stroke: "#10b981" } },
  { id: "e-c2-p2", source: "c2", target: "p2", label: "IMPACTS_PRINCIPLE", animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" }, style: { stroke: "#10b981" } },
];

export default function OntologyExplorerPage() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  // In a real application, you would fetch the full graph from the backend:
  // useEffect(() => { api.get("/ontology-graph").then(...) }, [])

  return (
    <div className="relative min-h-screen py-10 px-4">
      <AnimatedBackground />
      <div className="max-w-[1600px] mx-auto space-y-6">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-2">
              <Network className="w-8 h-8 text-purple-400" />
              Ontology Explorer
            </h1>
            <p className="text-zinc-400 mt-1">Interactive visualization of the underlying Neo4j knowledge graph.</p>
          </div>
          <div className="flex gap-2">
            <Badge variant="outline" className="bg-purple-500/10 text-purple-300 border-purple-500/30">AI Categories</Badge>
            <Badge variant="outline" className="bg-red-500/10 text-red-300 border-red-500/30">Risks</Badge>
            <Badge variant="outline" className="bg-blue-500/10 text-blue-300 border-blue-500/30">Regulations</Badge>
            <Badge variant="outline" className="bg-emerald-500/10 text-emerald-300 border-emerald-500/30">Principles</Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 h-[700px]">
          {/* React Flow Map */}
          <Card className="lg:col-span-4 bg-black/40 border-white/10 overflow-hidden relative">
            <ReactFlow 
              nodes={nodes} 
              edges={edges}
              fitView
              className="dark"
              minZoom={0.2}
            >
              <Background color="#333" gap={20} />
              <Controls />
              <MiniMap style={{ backgroundColor: "#111", border: "1px solid #333" }} />
            </ReactFlow>
          </Card>

          {/* Sidebar Stats */}
          <Card className="bg-black/40 border-white/10 overflow-hidden flex flex-col">
            <CardHeader className="border-b border-white/10 bg-white/5">
              <CardTitle className="text-lg flex items-center gap-2">
                <Database className="w-5 h-5 text-blue-400" />
                Graph Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-4">
              <div className="space-y-1">
                <span className="text-xs text-zinc-500 uppercase font-bold">Total Nodes</span>
                <p className="text-2xl font-bold text-white">{nodes.length}</p>
              </div>
              <div className="space-y-1">
                <span className="text-xs text-zinc-500 uppercase font-bold">Total Relationships</span>
                <p className="text-2xl font-bold text-white">{edges.length}</p>
              </div>
              <div className="space-y-1">
                <span className="text-xs text-zinc-500 uppercase font-bold">AI Categories</span>
                <p className="text-2xl font-bold text-purple-400">2</p>
              </div>
              <div className="space-y-1">
                <span className="text-xs text-zinc-500 uppercase font-bold">Regulations</span>
                <p className="text-2xl font-bold text-blue-400">3</p>
              </div>
              
              <div className="mt-8 pt-4 border-t border-white/10">
                <CardDescription className="text-xs text-zinc-400">
                  This explorer is currently rendering a demo subset of the ontology graph. 
                  Connect to the `GET /ontology-graph` backend endpoint to stream the live Neo4j topology.
                </CardDescription>
              </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
