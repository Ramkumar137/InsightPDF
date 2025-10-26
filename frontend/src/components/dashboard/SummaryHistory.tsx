/**
 * SummaryHistory Component
 * FIXED: Display times in IST timezone
 */

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { X, Plus, FileText, Loader2, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { getSummaryHistory, getSummary } from "@/lib/api-client";

interface SummaryHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSummary: (summary: any) => void;
  onNewSummary: () => void;
  refreshTrigger?: number;
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
  refreshTrigger = 0,
}: SummaryHistoryProps) {
  const [summaries, setSummaries] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      console.log('📚 SummaryHistory: Loading summaries...');
      loadSummaries();
    }
  }, [isOpen, refreshTrigger]);

  const loadSummaries = async () => {
    setIsLoading(true);
    try {
      console.log('📡 Fetching summary history...');
      const data = await getSummaryHistory(50, 0);
      console.log('✅ History loaded:', data);
      console.log('📊 Summaries count:', data.summaries?.length);
      
      setSummaries(data.summaries || []);
      
      if (data.summaries?.length === 0) {
        console.log('ℹ️ No summaries found');
      }
    } catch (error: any) {
      console.error('❌ History load error:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to load summary history",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSummary = async (id: string) => {
    setSelectedId(id);
    console.log('📖 Loading summary:', id);
    try {
      const summary = await getSummary(id);
      console.log('✅ Summary loaded:', summary);
      onSelectSummary(summary);
      
      if (window.innerWidth < 768) {
        onClose();
      }
    } catch (error: any) {
      console.error('❌ Summary load error:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to load summary",
        variant: "destructive",
      });
      setSelectedId(null);
    }
  };

  const handleNewSummary = () => {
    setSelectedId(null);
    onNewSummary();
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  // FIXED: Convert UTC to IST and format
  const formatDate = (timestamp: string) => {
    // Parse the UTC timestamp
    const date = new Date(timestamp);
    
    // Convert to IST (UTC + 5:30)
    const istDate = new Date(date.getTime() + (5.5 * 60 * 60 * 1000));
    
    const now = new Date();
    const istNow = new Date(now.getTime() + (5.5 * 60 * 60 * 1000));
    
    const diffInHours = (istNow.getTime() - istDate.getTime()) / (1000 * 60 * 60);

    // Format based on how recent it is
    if (diffInHours < 1) {
      const minutes = Math.floor(diffInHours * 60);
      return minutes <= 0 ? 'Just now' : `${minutes}m ago`;
    } else if (diffInHours < 24) {
      const hours = Math.floor(diffInHours);
      return `${hours}h ago`;
    } else if (diffInHours < 168) { // Less than 7 days
      const days = Math.floor(diffInHours / 24);
      return `${days}d ago`;
    } else {
      // For older items, show full date in IST
      return istDate.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: istDate.getFullYear() !== istNow.getFullYear() ? 'numeric' : undefined
      });
    }
  };

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:sticky top-0 left-0 h-screen w-80 bg-background border-r z-50 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b p-4">
            <h2 className="text-lg font-semibold">Summary History</h2>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={loadSummaries}
                title="Refresh history"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="md:hidden"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* New Summary Button */}
          <div className="p-4">
            <Button
              onClick={handleNewSummary}
              className="w-full"
              variant="default"
            >
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
                  No summaries yet.<br />Create your first one!
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
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between">
                        <h3 className="font-medium text-sm line-clamp-1">
                          {summary.fileName}
                        </h3>
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
              {summaries.length} {summaries.length === 1 ? 'summary' : 'summaries'} total
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}