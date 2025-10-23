import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Minimize2, RefreshCw, Sparkles, Download, FileText, File } from "lucide-react";

export const SummaryDisplay = () => {
  // Mock summary data - will be replaced with real data
  const hasSummary = false;

  if (!hasSummary) {
    return (
      <Card className="shadow-elegant">
        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-16 h-16 bg-gradient-primary/10 rounded-full flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No Summary Yet</h3>
          <p className="text-muted-foreground max-w-md">
            Upload your PDF files and select a context type to generate an AI-powered summary.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-elegant">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>Financial Report Summary</CardTitle>
            <CardDescription>Executive Context • Generated 5 minutes ago</CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                Download
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-popover">
              <DropdownMenuItem className="gap-2 cursor-pointer">
                <FileText className="w-4 h-4" />
                Download as .txt
              </DropdownMenuItem>
              <DropdownMenuItem className="gap-2 cursor-pointer">
                <File className="w-4 h-4" />
                Download as .pdf
              </DropdownMenuItem>
              <DropdownMenuItem className="gap-2 cursor-pointer">
                <File className="w-4 h-4" />
                Download as .docx
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary Sections */}
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold mb-2 text-primary">Overview</h4>
            <p className="text-sm text-foreground leading-relaxed">
              This is where the overview section of the summary would appear...
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2 text-primary">Key Insights</h4>
            <p className="text-sm text-foreground leading-relaxed">
              This is where the key insights would appear...
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2 text-primary">Risks</h4>
            <p className="text-sm text-foreground leading-relaxed">
              This is where identified risks would appear...
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-2 text-primary">Recommendations</h4>
            <p className="text-sm text-foreground leading-relaxed">
              This is where recommendations would appear...
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 pt-4 border-t">
          <Button variant="outline" className="gap-2">
            <Minimize2 className="w-4 h-4" />
            Shorten Summary
          </Button>
          <Button variant="outline" className="gap-2">
            <Sparkles className="w-4 h-4" />
            Refine Summary
          </Button>
          <Button variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            Regenerate Summary
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
