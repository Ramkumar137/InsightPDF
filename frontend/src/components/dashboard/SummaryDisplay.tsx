/**
 * SummaryDisplay Component - Updated with Backend Integration
 * Replace your existing SummaryDisplay.tsx with this code
 */

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  FileText,
  Download,
  Sparkles,
  RefreshCw,
  Minimize2,
  Loader2,
  FileUp,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { refineSummary, downloadSummary } from "@/lib/api-client";

interface SummaryDisplayProps {
  summary: {
    summaryId: string;
    content: {
      overview: string;
      keyInsights: string;
      risks: string;
      recommendations: string;
    };
    metadata: {
      fileName: string;
      contextType: string;
      createdAt: string;
    };
  } | null;
  onNewSummary?: () => void;
}

export function SummaryDisplay({ summary, onNewSummary }: SummaryDisplayProps) {
  const { toast } = useToast();
  const [isRefining, setIsRefining] = useState(false);
  const [currentSummary, setCurrentSummary] = useState(summary);

  // Update when new summary prop is received
  if (summary && summary.summaryId !== currentSummary?.summaryId) {
    setCurrentSummary(summary);
  }

  if (!currentSummary) {
    return (
      <Card className="flex h-[600px] flex-col items-center justify-center p-12">
        <div className="rounded-full bg-primary/10 p-6 mb-6">
          <FileUp className="h-12 w-12 text-primary" />
        </div>
        <h2 className="text-2xl font-semibold mb-3">No Summary Yet</h2>
        <p className="text-center text-muted-foreground max-w-md mb-6">
          Upload PDF files and select a context type to generate an AI-powered summary
        </p>
      </Card>
    );
  }

  const handleRefine = async (action: "shorten" | "refine" | "regenerate") => {
    setIsRefining(true);

    try {
      const result = await refineSummary(currentSummary.summaryId, action);
      
      setCurrentSummary({
        ...currentSummary,
        content: result.content,
      });

      toast({
        title: "Summary refined!",
        description: `Successfully ${action === "shorten" ? "shortened" : action === "refine" ? "refined" : "regenerated"} the summary`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || `Failed to ${action} summary`,
        variant: "destructive",
      });
    } finally {
      setIsRefining(false);
    }
  };

  const handleDownload = async (format: "txt" | "pdf" | "docx") => {
    try {
      await downloadSummary(currentSummary.summaryId, format);
      
      toast({
        title: "Download started",
        description: `Downloading summary as ${format.toUpperCase()}`,
      });
    } catch (error: any) {
      toast({
        title: "Download failed",
        description: error.message || "Failed to download summary",
        variant: "destructive",
      });
    }
  };

  const { content, metadata } = currentSummary;

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{metadata.fileName}</h2>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Context: <span className="capitalize">{metadata.contextType}</span> • 
              Generated: {new Date(metadata.createdAt).toLocaleString()}
            </p>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRefine("shorten")}
              disabled={isRefining}
            >
              {isRefining ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Minimize2 className="h-4 w-4" />
              )}
              <span className="ml-2">Shorten</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRefine("refine")}
              disabled={isRefining}
            >
              {isRefining ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              <span className="ml-2">Refine</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRefine("regenerate")}
              disabled={isRefining}
            >
              {isRefining ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              <span className="ml-2">Regenerate</span>
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="default" size="sm">
                  <Download className="h-4 w-4" />
                  <span className="ml-2">Download</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleDownload("txt")}>
                  Text (.txt)
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDownload("pdf")}>
                  PDF (.pdf)
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleDownload("docx")}>
                  Word (.docx)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            {onNewSummary && (
              <Button variant="outline" size="sm" onClick={onNewSummary}>
                New Summary
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Overview */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <div className="rounded-md bg-blue-100 p-2">
            <FileText className="h-5 w-5 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold">Overview</h3>
        </div>
        <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
          {content.overview}
        </p>
      </Card>

      {/* Key Insights */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <div className="rounded-md bg-green-100 p-2">
            <Sparkles className="h-5 w-5 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold">Key Insights</h3>
        </div>
        <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
          {content.keyInsights}
        </p>
      </Card>

      {/* Risks (if available) */}
      {content.risks && (
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <div className="rounded-md bg-orange-100 p-2">
              <span className="text-xl">⚠️</span>
            </div>
            <h3 className="text-lg font-semibold">Risks & Challenges</h3>
          </div>
          <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
            {content.risks}
          </p>
        </Card>
      )}

      {/* Recommendations (if available) */}
      {content.recommendations && (
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <div className="rounded-md bg-purple-100 p-2">
              <span className="text-xl">✅</span>
            </div>
            <h3 className="text-lg font-semibold">Recommendations</h3>
          </div>
          <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
            {content.recommendations}
          </p>
        </Card>
      )}
    </div>
  );
}