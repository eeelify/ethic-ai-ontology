"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldAlert, Activity, GitBranch, FileText, Database } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Home", path: "/", icon: <ShieldAlert className="w-4 h-4 mr-2" /> },
    { name: "Analyzer", path: "/analyzer", icon: <Activity className="w-4 h-4 mr-2" /> },
    { name: "Graph Trace", path: "/trace", icon: <GitBranch className="w-4 h-4 mr-2" /> },
    { name: "Report", path: "/report", icon: <FileText className="w-4 h-4 mr-2" /> },
    { name: "Ontology", path: "/ontology", icon: <Database className="w-4 h-4 mr-2" /> },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-black/50 backdrop-blur-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/50 flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-blue-400" />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
            AuraGovernance
          </span>
        </Link>
        <div className="flex items-center space-x-6">
          {navItems.map((item) => (
            <Link
              key={item.path}
              href={item.path}
              className={`flex items-center text-sm font-medium transition-colors hover:text-blue-400 ${
                pathname === item.path ? "text-blue-400" : "text-zinc-400"
              }`}
            >
              {item.icon}
              {item.name}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
