/**
 * Dashboard - FIXED: Auto-refreshes history on new summaries
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

const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const API_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
};

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentSummary, setCurrentSummary] = useState<any>(null);
  const [apiHealthy, setApiHealthy] = useState(true);
  const [healthCheckAttempts, setHealthCheckAttempts] = useState(0);
  const [historyRefreshTrigger, setHistoryRefreshTrigger] = useState(0); // NEW: Trigger history refresh

  // Check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          navigate("/login");
          return;
        }
        setUser(session.user);
      } catch (error) {
        console.error("Auth error:", error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT") {
        navigate("/login");
      } else if (session) {
        setUser(session.user);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  // Check API health
  useEffect(() => {
    let isMounted = true;
    
    const checkHealth = async () => {
      const healthy = await checkBackendHealth();
      
      if (isMounted) {
        setApiHealthy(healthy);
        setHealthCheckAttempts(prev => prev + 1);
        
        if (!healthy && healthCheckAttempts < 2) {
          setTimeout(() => {
            if (isMounted) checkHealth();
          }, 2000);
        } else if (!healthy) {
          toast({
            title: "Backend Connection Issue",
            description: "Cannot connect to backend. Some features may not work.",
            variant: "destructive",
          });
        }
      }
    };

    const timeoutId = setTimeout(checkHealth, 500);
    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
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
    console.log('🎉 New summary generated:', summary.summaryId);
    setCurrentSummary(summary);
    setApiHealthy(true);
    
    // Trigger history refresh
    setHistoryRefreshTrigger(prev => prev + 1);
    
    // Auto-open sidebar to show new summary in history
    setSidebarOpen(true);
    
    toast({
      title: "Success!",
      description: "Your PDF summary has been generated",
    });
  };

  const handleSelectSummary = (summary: any) => {
    console.log('📖 Selected summary:', summary.summaryId);
    setCurrentSummary(summary);
  };

  const handleNewSummary = () => {
    console.log('📝 Creating new summary');
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
      <DashboardHeader
        user={user}
        onLogout={handleLogout}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      {!apiHealthy && healthCheckAttempts >= 2 && (
        <div className="bg-yellow-50 border-b border-yellow-200 px-4 py-2 text-center">
          <p className="text-sm text-yellow-800">
            ⚠️ Backend connection issues detected. 
            <button 
              onClick={() => window.location.reload()} 
              className="ml-2 underline hover:no-underline"
            >
              Click to retry
            </button>
          </p>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <SummaryHistory
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onSelectSummary={handleSelectSummary}
          onNewSummary={handleNewSummary}
          refreshTrigger={historyRefreshTrigger} // Pass trigger to force refresh
        />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-5xl">
            {!currentSummary ? (
              <div>
                <div className="mb-6">
                  <h1 className="text-3xl font-bold mb-2">
                    Context-Aware PDF Summarizer
                  </h1>
                  <p className="text-muted-foreground">
                    Upload your PDF documents and get AI-powered summaries powered by Gemini
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