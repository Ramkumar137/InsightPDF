import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Upload, X, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const contextTypes = [
  {
    value: "executive",
    label: "Executive",
    description: "High-level overview and key decisions",
  },
  {
    value: "student",
    label: "Student",
    description: "Detailed explanations and learning focus",
  },
  {
    value: "analyst",
    label: "Analyst",
    description: "Data-driven insights and trends",
  },
  {
    value: "general",
    label: "General Summary",
    description: "Balanced, concise overview",
  },
];

export const UploadSection = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [contextType, setContextType] = useState<string>("");
  const [isDragging, setIsDragging] = useState(false);
  const { toast } = useToast();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "application/pdf"
    );
    
    if (droppedFiles.length === 0) {
      toast({
        title: "Invalid file type",
        description: "Please upload PDF files only.",
        variant: "destructive",
      });
      return;
    }
    
    setFiles((prev) => [...prev, ...droppedFiles]);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (files.length === 0) {
      toast({
        title: "No files selected",
        description: "Please upload at least one PDF file.",
        variant: "destructive",
      });
      return;
    }
    
    if (!contextType) {
      toast({
        title: "Context type required",
        description: "Please select a context type for summarization.",
        variant: "destructive",
      });
      return;
    }
    
    // Will be implemented with backend
    toast({
      title: "Processing...",
      description: "Your PDFs are being summarized.",
    });
  };

  return (
    <Card className="shadow-elegant">
      <CardHeader>
        <CardTitle>Upload PDFs</CardTitle>
        <CardDescription>
          Upload one or more PDF files and select the context type for summarization
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* File Upload Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 ${
            isDragging ? "border-primary bg-primary/5" : "border-border"
          }`}
        >
          <Upload className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-sm text-muted-foreground mb-2">
            Drag and drop PDF files here, or
          </p>
          <Label htmlFor="file-upload">
            <Button variant="outline" asChild>
              <span className="cursor-pointer">Browse Files</span>
            </Button>
          </Label>
          <Input
            id="file-upload"
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileInput}
            className="hidden"
          />
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="space-y-2">
            <Label>Uploaded Files ({files.length})</Label>
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-secondary rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-primary" />
                    <span className="text-sm font-medium">{file.name}</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(index)}
                    className="h-8 w-8"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Context Type Selector */}
        <div className="space-y-2">
          <Label>Context Type</Label>
          <Select value={contextType} onValueChange={setContextType}>
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="Select context type" />
            </SelectTrigger>
            <SelectContent className="bg-popover">
              {contextTypes.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  <div>
                    <div className="font-medium">{type.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {type.description}
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Generate Button */}
        <Button
          onClick={handleSubmit}
          className="w-full bg-gradient-primary hover:shadow-glow transition-all duration-300"
        >
          Generate Summary
        </Button>
      </CardContent>
    </Card>
  );
};
