/**
 * Dashboard Component - Updated with Complete Backend Integration
 * Replace your existing Dashboard.tsx with this code
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { User } from "@supabase/supabase-js";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { UploadSection } from "@/components/dashboard/UploadSection";
import { SummaryDisplay } from "@/components/dashboard/SummaryDisplay";
import { SummaryHistory } from "@/components/dashboard/SummaryHistory";
import { useToast } from "@/hooks/use-toast";
import { checkApiHealth } from "@/lib/api-client";

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentSummary, setCurrentSummary] = useState<any>(null);
  const [apiHealthy, setApiHealthy] = useState(true);

  // Check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession();

        if (!session) {
          navigate("/login");
          return;
        }

        setUser(session.user);
      } catch (error) {
        console.error("Auth check error:", error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    // Subscribe to auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT") {
        navigate("/login");
      } else if (session) {
        setUser(session.user);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [navigate]);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await checkApiHealth();
      setApiHealthy(healthy);
      
      if (!healthy) {
        toast({
          title: "Backend Offline",
          description: "The API server is not responding. Please ensure the backend is running.",
          variant: "destructive",
        });
      }
    };

    checkHealth();
  }, [toast]);

  const handleLogout = async () => {
    try {
      await supabase.auth.signOut();
      navigate("/login");
    } catch (error) {
      console.error("Logout error:", error);
      toast({
        title: "Error",
        description: "Failed to logout",
        variant: "destructive",
      });
    }
  };

  const handleSummaryGenerated = (summary: any) => {
    setCurrentSummary(summary);
    toast({
      title: "Success!",
      description: "Your PDF summary has been generated",
    });
  };

  const handleSelectSummary = (summary: any) => {
    setCurrentSummary(summary);
  };

  const handleNewSummary = () => {
    setCurrentSummary(null);
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <DashboardHeader
        user={user}
        onLogout={handleLogout}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* API Health Warning */}
      {!apiHealthy && (
        <div className="bg-destructive/10 border-b border-destructive/20 px-4 py-2 text-center">
          <p className="text-sm text-destructive">
            ⚠️ Backend API is offline. Please start the backend server: <code className="bg-muted px-2 py-1 rounded">uvicorn main:app --reload</code>
          </p>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <SummaryHistory
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onSelectSummary={handleSelectSummary}
          onNewSummary={handleNewSummary}
        />

        {/* Main Area */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-5xl">
            {!currentSummary ? (
              <div>
                <div className="mb-6">
                  <h1 className="text-3xl font-bold mb-2">
                    Context-Aware PDF Summarizer
                  </h1>
                  <p className="text-muted-foreground">
                    Upload your PDF documents and get AI-powered summaries tailored to your needs
                  </p>
                </div>
                <UploadSection onSummaryGenerated={handleSummaryGenerated} />
              </div>
            ) : (
              <SummaryDisplay
                summary={currentSummary}
                onNewSummary={handleNewSummary}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}