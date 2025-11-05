/**
 * Enhanced SummaryDisplay with Keyword Highlighting and Interactive Features
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
  Maximize2,
  Focus,
  Tag,
  BookOpen,
  Shield,
  Clock,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { refineSummary, downloadSummary } from "@/lib/api-client";

interface EnhancedSummaryDisplayProps {
  summary: {
    summaryId: string;
    content: {
      overview: string;
      keyInsights: string;
      risks: string;
      recommendations: string;
      extractiveSummary?: string;
      abstractiveSummary?: string;
    };
    keywords?: string[];
    sections?: {
      abstract?: string;
      introduction?: string;
      methodology?: string;
      results?: string;
      conclusion?: string;
    };
    metadata: {
      fileName: string;
      contextType: string;
      userRole?: string;
      memoryType?: string;
      isPrivate?: boolean;
      createdAt: string;
    };
  } | null;
  onNewSummary?: () => void;
}

export function EnhancedSummaryDisplay({ summary, onNewSummary }: EnhancedSummaryDisplayProps) {
  const { toast } = useToast();

  const [loadingStates, setLoadingStates] = useState({
    shorten: false,
    refine: false,
    regenerate: false,
    shorter: false,
    detailed: false,
    focus_methods: false,
    focus_results: false,
  });

  const [currentSummary, setCurrentSummary] = useState(summary);
  const [showSections, setShowSections] = useState(false);
  const [highlightKeywords, setHighlightKeywords] = useState(true);

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
          Upload PDF files and configure your preferences to generate an AI-powered hybrid summary
        </p>
      </Card>
    );
  }

  const handleRefine = async (action: any) => {
    setLoadingStates((prev) => ({ ...prev, [action]: true }));

    try {
      const result = await refineSummary(currentSummary.summaryId, action);

      setCurrentSummary({
        ...currentSummary,
        content: result.content,
      });

      toast({
        title: "Summary updated!",
        description: `Successfully applied ${action} refinement`,
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || `Failed to ${action} summary`,
        variant: "destructive",
      });
    } finally {
      setLoadingStates((prev) => ({ ...prev, [action]: false }));
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

  const formatDateIST = (timestamp: string) => {
    const date = new Date(timestamp);
    const istDate = new Date(date.getTime() + 5.5 * 60 * 60 * 1000);

    return istDate.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  };

  const highlightText = (text: string, keywords: string[]) => {
    if (!highlightKeywords || !keywords || keywords.length === 0) {
      return text;
    }

    let highlightedText = text;
    keywords.forEach((keyword) => {
      const regex = new RegExp(`\\b(${keyword})\\b`, "gi");
      highlightedText = highlightedText.replace(
        regex,
        '<mark class="bg-yellow-200 px-1 rounded">$1</mark>'
      );
    });

    return highlightedText;
  };

  const { content, metadata, keywords, sections } = currentSummary;
  const isAnyLoading = Object.values(loadingStates).some((state) => state);

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">{metadata.fileName}</h2>
            </div>
            <div className="flex flex-wrap gap-2 mt-2 text-sm text-muted-foreground">
              <span className="capitalize">{metadata.contextType}</span>
              {metadata.userRole && (
                <>
                  <span>•</span>
                  <span className="capitalize">{metadata.userRole}</span>
                </>
              )}
              {metadata.memoryType && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    {metadata.isPrivate ? (
                      <>
                        <Shield className="h-3 w-3" />
                        Short-term
                      </>
                    ) : (
                      <>
                        <Clock className="h-3 w-3" />
                        Long-term
                      </>
                    )}
                  </span>
                </>
              )}
              <span>•</span>
              <span>{formatDateIST(metadata.createdAt)} IST</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {/* Interactive Refinement */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" disabled={isAnyLoading}>
                  <Focus className="h-4 w-4" />
                  <span className="ml-2">Refine</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => handleRefine("shorter")}>
                  Make Shorter
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleRefine("detailed")}>
                  More Detailed
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleRefine("focus_methods")}>
                  Focus on Methods
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleRefine("focus_results")}>
                  Focus on Results
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRefine("shorten")}
              disabled={isAnyLoading}
            >
              <Minimize2 className="h-4 w-4" />
              <span className="ml-2">Shorten</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => handleRefine("regenerate")}
              disabled={isAnyLoading}
            >
              {loadingStates.regenerate ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              <span className="ml-2">Regenerate</span>
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="default" size="sm" disabled={isAnyLoading}>
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
              <Button variant="outline" size="sm" onClick={onNewSummary} disabled={isAnyLoading}>
                New Summary
              </Button>
            )}
          </div>
        </div>

        {/* Keywords Display */}
        {keywords && keywords.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Tag className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Key Terms</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setHighlightKeywords(!highlightKeywords)}
              >
                {highlightKeywords ? "Hide Highlights" : "Show Highlights"}
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {keywords.slice(0, 10).map((keyword, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Section Toggle */}
      {sections && Object.keys(sections).length > 0 && (
        <Card className="p-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowSections(!showSections)}
            className="w-full"
          >
            <BookOpen className="h-4 w-4 mr-2" />
            {showSections ? "Hide" : "Show"} Document Sections
          </Button>
        </Card>
      )}

      {/* Document Sections */}
      {showSections && sections && (
        <>
          {sections.abstract && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3">Abstract</h3>
              <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {sections.abstract}
              </p>
            </Card>
          )}
          {sections.methodology && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3">Methodology</h3>
              <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {sections.methodology}
              </p>
            </Card>
          )}
          {sections.results && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3">Results</h3>
              <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {sections.results}
              </p>
            </Card>
          )}
          {sections.conclusion && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-3">Conclusion</h3>
              <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {sections.conclusion}
              </p>
            </Card>
          )}
        </>
      )}

      {/* Hybrid Summary View */}
      {content.extractiveSummary && (
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <div className="rounded-md bg-green-100 p-2">
              <Sparkles className="h-5 w-5 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold">Extractive Summary</h3>
            <span className="text-xs text-muted-foreground">(Key Sentences)</span>
          </div>
          <p
            className="text-muted-foreground leading-relaxed"
            dangerouslySetInnerHTML={{
              __html: highlightText(content.extractiveSummary, keywords || []),
            }}
          />
        </Card>
      )}

      {/* Overview */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <div className="rounded-md bg-blue-100 p-2">
            <FileText className="h-5 w-5 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold">Overview</h3>
          <span className="text-xs text-muted-foreground">(Abstractive)</span>
        </div>
        <p
          className="text-muted-foreground leading-relaxed whitespace-pre-wrap"
          dangerouslySetInnerHTML={{
            __html: highlightText(content.overview, keywords || []),
          }}
        />
      </Card>

      {/* Key Insights */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <div className="rounded-md bg-green-100 p-2">
            <Sparkles className="h-5 w-5 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold">Key Insights</h3>
        </div>
        <p
          className="text-muted-foreground leading-relaxed whitespace-pre-wrap"
          dangerouslySetInnerHTML={{
            __html: highlightText(content.keyInsights, keywords || []),
          }}
        />
      </Card>

      {/* Risks */}
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

      {/* Recommendations */}
      {content.recommendations && (
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <div className="rounded-md bg-blue-100 p-2">
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
