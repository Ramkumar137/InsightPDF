/**
 * UploadSection Component - Updated with Backend Integration
 * Replace your existing UploadSection.tsx with this code
 */

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { uploadAndSummarize } from "@/lib/api-client";

interface UploadSectionProps {
  onSummaryGenerated: (summary: any) => void;
}

export function UploadSection({ onSummaryGenerated }: UploadSectionProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [contextType, setContextType] = useState("executive");
  const [userRole, setUserRole] = useState("professional");
  const [isPrivate, setIsPrivate] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
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

    const droppedFiles = Array.from(e.dataTransfer.files);
    const pdfFiles = droppedFiles.filter((file) => file.type === "application/pdf");

    if (pdfFiles.length !== droppedFiles.length) {
      toast({
        title: "Invalid files",
        description: "Only PDF files are allowed",
        variant: "destructive",
      });
    }

    setFiles((prev) => [...prev, ...pdfFiles]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (files.length === 0) {
      toast({
        title: "No files selected",
        description: "Please select at least one PDF file",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);

    try {
      const result = await uploadAndSummarize(files, contextType, userRole, isPrivate);
      
      toast({
        title: "Summary generated!",
        description: `Successfully processed ${files.length} file(s)`,
      });

      // Pass the result to parent component
      onSummaryGenerated(result);

      // Clear files after successful upload
      setFiles([]);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to generate summary",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card
        className={`border-2 border-dashed p-8 transition-colors ${
          isDragging ? "border-primary bg-primary/5" : "border-gray-300"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="rounded-full bg-primary/10 p-4">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <div className="text-center">
            <p className="text-lg font-medium">Drop your PDF files here</p>
            <p className="text-sm text-muted-foreground">
              or click to browse your computer
            </p>
          </div>
          <input
            type="file"
            accept=".pdf"
            multiple
            className="hidden"
            id="file-upload"
            onChange={handleFileSelect}
            disabled={isUploading}
          />
          <label htmlFor="file-upload">
            <Button variant="outline" disabled={isUploading} asChild>
              <span className="cursor-pointer">Browse Files</span>
            </Button>
          </label>
        </div>
      </Card>

      {/* Selected Files */}
      {files.length > 0 && (
        <Card className="p-4">
          <h3 className="mb-3 font-medium">Selected Files ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-md border p-2"
              >
                <div className="flex items-center space-x-2">
                  <FileText className="h-4 w-4 text-blue-600" />
                  <span className="text-sm">{file.name}</span>
                  <span className="text-xs text-muted-foreground">
                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Context Selection */}
      <Card className="p-6">
        <h3 className="mb-4 font-medium">Summary Context</h3>
        <RadioGroup value={contextType} onValueChange={setContextType} disabled={isUploading}>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="executive" id="executive" />
              <Label htmlFor="executive" className="cursor-pointer">
                <div>
                  <p className="font-medium">Executive</p>
                  <p className="text-sm text-muted-foreground">
                    High-level insights and strategic decisions
                  </p>
                </div>
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="student" id="student" />
              <Label htmlFor="student" className="cursor-pointer">
                <div>
                  <p className="font-medium">Student</p>
                  <p className="text-sm text-muted-foreground">
                    Clear explanations and learning insights
                  </p>
                </div>
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="analyst" id="analyst" />
              <Label htmlFor="analyst" className="cursor-pointer">
                <div>
                  <p className="font-medium">Analyst</p>
                  <p className="text-sm text-muted-foreground">
                    Trends, data points, and analysis
                  </p>
                </div>
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="general" id="general" />
              <Label htmlFor="general" className="cursor-pointer">
                <div>
                  <p className="font-medium">General</p>
                  <p className="text-sm text-muted-foreground">
                    Brief and clear summary
                  </p>
                </div>
              </Label>
            </div>
          </div>
        </RadioGroup>
      </Card>

      {/* User Role Selection */}
      <Card className="p-6">
        <h3 className="mb-4 font-medium">Your Role</h3>
        <RadioGroup value={userRole} onValueChange={setUserRole} disabled={isUploading}>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="student" id="role-student" />
              <Label htmlFor="role-student" className="cursor-pointer">
                <div>
                  <p className="font-medium">Student</p>
                  <p className="text-sm text-muted-foreground">
                    Focus on learning and understanding concepts
                  </p>
                </div>
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="researcher" id="role-researcher" />
              <Label htmlFor="role-researcher" className="cursor-pointer">
                <div>
                  <p className="font-medium">Researcher</p>
                  <p className="text-sm text-muted-foreground">
                    Methodology, findings, and academic rigor
                  </p>
                </div>
              </Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="professional" id="role-professional" />
              <Label htmlFor="role-professional" className="cursor-pointer">
                <div>
                  <p className="font-medium">Professional</p>
                  <p className="text-sm text-muted-foreground">
                    Business value and practical applications
                  </p>
                </div>
              </Label>
            </div>
          </div>
        </RadioGroup>
      </Card>

      {/* Privacy Settings */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium">Privacy Settings</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Private documents use short-term memory only
            </p>
          </div>
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isPrivate}
              onChange={(e) => setIsPrivate(e.target.checked)}
              disabled={isUploading}
              className="w-4 h-4 text-primary bg-gray-100 border-gray-300 rounded focus:ring-primary"
            />
            <span className="text-sm font-medium">
              {isPrivate ? "Private (Short-term)" : "Shared (Long-term)"}
            </span>
          </label>
        </div>
      </Card>

      {/* Submit Button */}
      <Button
        onClick={handleSubmit}
        disabled={files.length === 0 || isUploading}
        className="w-full"
        size="lg"
      >
        {isUploading ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Generating Summary...
          </>
        ) : (
          "Generate Summary"
        )}
      </Button>
    </div>
  );
}