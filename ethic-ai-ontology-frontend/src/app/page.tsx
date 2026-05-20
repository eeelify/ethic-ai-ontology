import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, ShieldCheck, Cpu, Scale, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="relative min-h-screen">
      <AnimatedBackground />
      
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="inline-flex items-center rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-sm text-blue-300 mb-8 backdrop-blur-md">
          <span className="flex h-2 w-2 rounded-full bg-blue-500 mr-2 animate-pulse"></span>
          GraphRAG Powered Assessment
        </div>
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-200 to-purple-400">
          Ontology-Driven AI Governance <br className="hidden md:block" />
          & Ethics Platform
        </h1>
        
        <p className="text-xl text-zinc-400 max-w-3xl mb-10 leading-relaxed">
          Analyze AI systems against EU AI Act, GDPR, KVKK, ethical principles, 
          and ontology-driven risk reasoning instantly. Full explainability. Zero black boxes.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/analyzer">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]">
              Start Assessment
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
          <Link href="/ontology">
            <Button size="lg" variant="outline" className="border-white/10 bg-white/5 hover:bg-white/10 backdrop-blur-md">
              Explore Ontology
              <Cpu className="ml-2 w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        <Card className="bg-black/40 border-white/10 backdrop-blur-md">
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center mb-4 border border-purple-500/30">
              <ShieldCheck className="w-6 h-6 text-purple-400" />
            </div>
            <CardTitle className="text-xl text-white">GraphRAG Analysis</CardTitle>
          </CardHeader>
          <CardContent className="text-zinc-400">
            Dynamically evaluate AI descriptions against a Neo4j ontology mapping risks, regulations, and principles.
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-white/10 backdrop-blur-md">
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center mb-4 border border-blue-500/30">
              <Scale className="w-6 h-6 text-blue-400" />
            </div>
            <CardTitle className="text-xl text-white">Regulatory Compliance</CardTitle>
          </CardHeader>
          <CardContent className="text-zinc-400">
            Automatically detect exposure to EU AI Act, GDPR, and KVKK articles based on system capabilities.
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-white/10 backdrop-blur-md">
          <CardHeader>
            <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center mb-4 border border-emerald-500/30">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            </div>
            <CardTitle className="text-xl text-white">Full Traceability</CardTitle>
          </CardHeader>
          <CardContent className="text-zinc-400">
            Every ethical violation and risk inference is 100% explainable through our deterministic reasoning trace.
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
