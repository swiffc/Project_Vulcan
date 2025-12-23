/**
 * Validation Dashboard Widget
 * 
 * Shows recent validation results with pass rates and issues.
 */

"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle, AlertTriangle, FileText, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { ValidationReport, ValidationResponse, getValidationStatus } from "@/lib/cad/validation-client";

interface ValidationWidgetProps {
  maxItems?: number;
  showChart?: boolean;
}

export function ValidationWidget({ maxItems = 5, showChart = true }: ValidationWidgetProps) {
  const [recentValidations, setRecentValidations] = useState<ValidationReport[]>([]);
  const [systemStatus, setSystemStatus] = useState<{ available: boolean; message: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadValidations();
    checkSystemStatus();
  }, []);

  async function loadValidations() {
    try {
      setLoading(true);
      const response = await fetch("/api/cad/validations/recent");
      if (!response.ok) throw new Error("Failed to fetch validations");
      const data = await response.json();
      setRecentValidations(data || []);
    } catch (error) {
      console.error("Failed to load validations:", error);
      setRecentValidations([]);
    } finally {
      setLoading(false);
    }
  }

  async function checkSystemStatus() {
    try {
      const status = await getValidationStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error("Failed to check system status:", error);
      setSystemStatus({ available: false, message: "System unavailable" });
    }
  }

  function getStatusIcon(passRate: number) {
    if (passRate >= 95) {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    } else if (passRate >= 80) {
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    } else {
      return <XCircle className="w-5 h-5 text-red-500" />;
    }
  }

  function formatDuration(ms: number): string {
    if (ms < 1000) {
      return `${ms}ms`;
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(1)}s`;
    } else {
      return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader title="Recent Validations" icon={<CheckCircle2 className="w-5 h-5" />} />
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader 
        title="Recent Validations" 
        icon={<CheckCircle2 className="w-5 h-5" />}
      />
      <CardContent>
        {/* System Status */}
        {systemStatus && (
          <div className="mb-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center gap-2">
              {systemStatus.available ? (
                <CheckCircle2 className="w-4 h-4 text-green-500" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500" />
              )}
              <span className="text-sm font-medium">
                {systemStatus.message}
              </span>
            </div>
          </div>
        )}

        {/* Validation List */}
        {recentValidations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No validations yet</p>
            <p className="text-xs mt-1">Upload a drawing to get started</p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentValidations.slice(0, maxItems).map((validation) => (
              <ValidationItem key={validation.id} validation={validation} />
            ))}
          </div>
        )}

        {/* Weekly Summary */}
        {showChart && recentValidations.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <h4 className="text-sm font-semibold">This Week</h4>
            </div>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {recentValidations.length}
                </div>
                <div className="text-xs text-gray-500">Total</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {Math.round(
                    recentValidations.reduce((sum, v) => sum + v.passRate, 0) / 
                    recentValidations.length
                  )}%
                </div>
                <div className="text-xs text-gray-500">Avg Pass Rate</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {recentValidations.reduce((sum, v) => sum + v.criticalFailures, 0)}
                </div>
                <div className="text-xs text-gray-500">Critical Issues</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface ValidationItemProps {
  validation: ValidationReport;
}

function ValidationItem({ validation }: ValidationItemProps) {
  const getStatusColor = (passRate: number) => {
    if (passRate >= 95) return "text-green-600 bg-green-50 dark:bg-green-900/20";
    if (passRate >= 80) return "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20";
    return "text-red-600 bg-red-50 dark:bg-red-900/20";
  };

  const getStatusIcon = (passRate: number) => {
    if (passRate >= 95) return <CheckCircle2 className="w-4 h-4" />;
    if (passRate >= 80) return <AlertTriangle className="w-4 h-4" />;
    return <XCircle className="w-4 h-4" />;
  };

  function formatTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return `${Math.floor(diffMins / 1440)}d ago`;
  }

  return (
    <div
      className="p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 cursor-pointer transition-colors"
      onClick={() => {
        // TODO: Show validation detail modal
        console.log("Show validation:", validation.id);
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className={`p-1 rounded ${getStatusColor(validation.passRate)}`}>
            {getStatusIcon(validation.passRate)}
          </div>
          <div>
            <div className="text-sm font-medium truncate max-w-[200px]">
              {validation.inputFile.split("/").pop() || "Unknown file"}
            </div>
            <div className="text-xs text-gray-500">
              {formatTime(validation.timestamp)}
            </div>
          </div>
        </div>
        
        <div className="text-right">
          <div className={`text-lg font-bold ${getStatusColor(validation.passRate)}`}>
            {validation.passRate.toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500">
            {validation.durationMs < 1000 
              ? `${validation.durationMs}ms` 
              : `${(validation.durationMs / 1000).toFixed(1)}s`}
          </div>
        </div>
      </div>
      
      <div className="flex gap-4 text-xs text-gray-600 dark:text-gray-400">
        <span>✓ {validation.passed}</span>
        {validation.warnings > 0 && <span className="text-yellow-600">⚠ {validation.warnings}</span>}
        {validation.errors > 0 && <span className="text-red-600">✗ {validation.errors}</span>}
        {validation.criticalFailures > 0 && (
          <span className="text-red-700 font-semibold">❌ {validation.criticalFailures}</span>
        )}
      </div>
    </div>
  );
}
