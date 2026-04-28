import React, { useState, useEffect } from "react";
import {
  Shield,
  Zap,
  TrendingUp,
  RefreshCw,
  ToggleLeft,
  ToggleRight,
  BarChart2,
  GitBranch,
  AlertTriangle,
} from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Switch } from "./ui/switch";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";

// Types
interface RouterStatus {
  enabled: boolean;
  current_intent: string;
  savings_percent: number;
  total_saved: number;
  turns_routed: number;
  fallback_count: number;
  force_full_mode: boolean;
  current_toolsets?: string[];
  top_tools?: [string, number][];
}

interface ToolRouterStatusProps {
  compact?: boolean;
}

export function ToolRouterStatus({ compact = false }: ToolRouterStatusProps) {
  const [status, setStatus] = useState<RouterStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const response = await fetch("/api/router/status");
      const data = await response.json();
      setStatus(data.enabled ? data : null);
    } catch (e) {
      // API not available - router not enabled
      setStatus(null);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const toggleRouter = async (enabled: boolean) => {
    setLoading(true);
    try {
      await fetch(`/api/router/toggle?enabled=${enabled}`, { method: "POST" });
      await fetchStatus();
    } finally {
      setLoading(false);
    }
  };

  const resetRouter = async () => {
    setLoading(true);
    try {
      await fetch("/api/router/reset", { method: "POST" });
      await fetchStatus();
    } finally {
      setLoading(false);
    }
  };

  // No router available - hide component silently
  if (!status && !compact) return null;

  if (compact) {
    return (
      <div className="flex items-center gap-2 text-xs">
        {status ? (
          <>
            <Zap className="w-3 h-3 text-emerald-500" />
            <span className="text-emerald-600 dark:text-emerald-400">
              {status.savings_percent}%
            </span>
          </>
        ) : (
          <>
            <Shield className="w-3 h-3 text-muted-foreground" />
            <span className="text-muted-foreground">Full</span>
          </>
        )}
      </div>
    );
  }

  return (
    <Card className="p-4 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20 border-emerald-200 dark:border-emerald-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-emerald-100 dark:bg-emerald-900 rounded-lg">
            <Zap className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <h3 className="font-semibold text-emerald-900 dark:text-emerald-100">
              智能工具路由
            </h3>
            <p className="text-xs text-emerald-600 dark:text-emerald-400">
              Tool Router v2.0
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">
              {status.enabled ? "已启用" : "已禁用"}
            </span>
            <Switch
              checked={status.enabled}
              onCheckedChange={toggleRouter}
              disabled={loading}
            />
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={resetRouter}
            disabled={loading}
            className="h-8 w-8 p-0"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="space-y-3">
        {/* Current Intent */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">当前意图</span>
          <Badge variant="outline" className="bg-white dark:bg-gray-900">
            <GitBranch className="w-3 h-3 mr-1" />
            {status.current_intent || "AUTO"}
          </Badge>
        </div>

        {/* Token Savings */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm text-muted-foreground flex items-center gap-1">
              <TrendingUp className="w-4 h-4" />
              Token 节省
            </span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400">
              {status.savings_percent}%
            </span>
          </div>
          <Progress value={status.savings_percent} className="h-2" />
          <p className="text-xs text-muted-foreground mt-1">
            累计节省 {status.total_saved.toLocaleString()} tokens · {status.turns_routed} 轮对话
          </p>
        </div>

        {/* Fallback Status */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            回退保护
          </span>
          <Badge
            variant={status.force_full_mode ? "destructive" : "secondary"}
            className="text-xs"
          >
            {status.force_full_mode
              ? "全工具集保护模式"
              : `${status.fallback_count} 次回退`}
          </Badge>
        </div>

        {/* Active Toolsets */}
        {status.current_toolsets && status.current_toolsets.length > 0 && (
          <div>
            <span className="text-sm text-muted-foreground">活动工具集</span>
            <div className="flex flex-wrap gap-1 mt-2">
              {status.current_toolsets.map((ts) => (
                <Badge
                  key={ts}
                  variant="outline"
                  className="text-xs bg-emerald-50 dark:bg-emerald-950"
                >
                  {ts}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Stats Summary Footer */}
      <div className="mt-4 pt-3 border-t border-emerald-200 dark:border-emerald-800">
        <div className="grid grid-cols-3 gap-2 text-center">
          <div>
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {status.turns_routed}
            </div>
            <div className="text-xs text-muted-foreground">已路由</div>
          </div>
          <div>
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {status.savings_percent}%
            </div>
            <div className="text-xs text-muted-foreground">平均节省</div>
          </div>
          <div>
            <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
              {status.fallback_count}
            </div>
            <div className="text-xs text-muted-foreground">回退次数</div>
          </div>
        </div>
      </div>
    </Card>
  );
}

// Compact version for status bar
export function ToolRouterCompact() {
  return <ToolRouterStatus compact={true} />;
}

export default ToolRouterStatus;
