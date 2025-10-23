import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, X, FileText, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface SummaryHistoryProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SummaryHistory = ({ isOpen, onClose }: SummaryHistoryProps) => {
  // Mock data for now - will be replaced with real data
  const summaries = [
    {
      id: 1,
      fileName: "Q4 Financial Report.pdf",
      contextType: "Executive",
      timestamp: "2 hours ago",
    },
    {
      id: 2,
      fileName: "Research Paper.pdf",
      contextType: "Student",
      timestamp: "1 day ago",
    },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed lg:sticky top-16 left-0 h-[calc(100vh-4rem)] w-72 bg-sidebar border-r border-sidebar-border z-50 transition-transform duration-300 lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
            <h2 className="font-semibold text-sidebar-foreground">History</h2>
            <div className="flex items-center gap-2">
              <Button size="icon" variant="ghost" className="h-8 w-8">
                <Plus className="h-4 w-4" />
              </Button>
              <Button
                size="icon"
                variant="ghost"
                className="h-8 w-8 lg:hidden"
                onClick={onClose}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Summary List */}
          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              {summaries.map((summary) => (
                <button
                  key={summary.id}
                  className="w-full text-left p-3 rounded-lg hover:bg-sidebar-accent transition-colors duration-200 group"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded bg-sidebar-accent flex items-center justify-center flex-shrink-0 group-hover:bg-primary/10">
                      <FileText className="w-4 h-4 text-sidebar-foreground group-hover:text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-sidebar-foreground truncate">
                        {summary.fileName}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {summary.contextType}
                      </p>
                      <div className="flex items-center gap-1 mt-1">
                        <Clock className="w-3 h-3 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">
                          {summary.timestamp}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </ScrollArea>
        </div>
      </aside>
    </>
  );
};
