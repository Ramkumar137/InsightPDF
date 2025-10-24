/**
 * SummaryHistory Component - Updated with Backend Integration
 * Replace your existing SummaryHistory.tsx with this code
 */

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X, Plus, FileText, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { getSummaryHistory, getSummary } from "@/lib/api-client";

interface SummaryHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSummary: (summary: any) => void;
  onNewSummary: () => void;
}

interface HistoryItem {
  id: string;
  fileName: string;
  contextType: string;
  timestamp: string;
  previewText: string;
}

export function SummaryHistory({
  isOpen,
  onClose,
  onSelectSummary,
  onNewSummary,
}: SummaryHistoryProps) {
  const [summaries, setSummaries] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { toast } = useToast();

  // Fetch summaries when sidebar opens
  useEffect(() => {
    if (isOpen) {
      loadSummaries();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const loadSummaries = async () => {
    setIsLoading(true);
    try {
      // adapt these params if your backend expects different pagination
      const data = await getSummaryHistory(50, 0);
      // handle both { summaries: [...] } and plain array return shapes
      if (Array.isArray(data)) {
        setSummaries(data as HistoryItem[]);
      } else if (data && Array.isArray((data as any).summaries)) {
        setSummaries((data as any).summaries);
      } else {
        setSummaries([]);
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error?.message || "Failed to load summary history.",
        variant: "destructive",
      });
      setSummaries([]);
      setSelectedId(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSummary = () => {
    setSelectedId(null);
    onNewSummary();
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  const handleSelectSummary = async (id: string) => {
    setSelectedId(id);
    try {
      const summary = await getSummary(id);
      onSelectSummary(summary);
      // Close sidebar on mobile after selection
      if (window.innerWidth < 768) {
        onClose();
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error?.message || "Failed to load selected summary.",
        variant: "destructive",
      });
      setSelectedId(null);
    }
  };

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

      if (diffInHours < 24) {
        return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      } else if (diffInHours < 168) {
        return date.toLocaleDateString([], { weekday: "short", hour: "2-digit", minute: "2-digit" });
      } else {
        return date.toLocaleDateString([], { month: "short", day: "numeric" });
      }
    } catch {
      return timestamp;
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 h-screen w-80 bg-background border-r z-50 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        aria-hidden={!isOpen}
        aria-label="Summary history sidebar"
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b p-4">
            <h2 className="text-lg font-semibold">Summary History</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="md:hidden"
              aria-label="Close summary history"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* New Summary Button */}
          <div className="p-4">
            <Button onClick={handleNewSummary} className="w-full" variant="default">
              <Plus className="mr-2 h-4 w-4" />
              New Summary
            </Button>
          </div>

          {/* Summary List */}
          <ScrollArea className="flex-1 px-4">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
                <p className="text-sm text-muted-foreground">Loading summaries...</p>
              </div>
            ) : summaries.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="rounded-full bg-muted p-4 mb-4">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                </div>
                <p className="text-sm text-muted-foreground text-center">
                  No summaries yet.
                  <br />
                  Create your first one!
                </p>
              </div>
            ) : (
              <div className="space-y-2 pb-4">
                {summaries.map((summary) => (
                  <Card
                    key={summary.id}
                    className={`p-4 cursor-pointer transition-colors hover:bg-accent ${
                      selectedId === summary.id ? "bg-accent border-primary" : ""
                    }`}
                    onClick={() => handleSelectSummary(summary.id)}
                    role="button"
                    tabIndex={0}
                    aria-pressed={selectedId === summary.id}
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between">
                        <h3 className="font-medium text-sm line-clamp-1">{summary.fileName}</h3>
                        <span className="text-xs text-muted-foreground whitespace-nowrap ml-2">
                          {formatDate(summary.timestamp)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-1 text-xs font-medium text-primary capitalize">
                          {summary.contextType}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {summary.previewText}
                      </p>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>

          {/* Footer */}
          <div className="border-t p-4">
            <p className="text-xs text-muted-foreground text-center">
              {summaries.length} {summaries.length === 1 ? "summary" : "summaries"} total
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
