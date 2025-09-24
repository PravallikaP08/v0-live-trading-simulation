"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { TrendingUp, TrendingDown, Target, Activity, DollarSign } from "lucide-react"

export default function BacktestResults({ results = null }) {
  if (!results) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Backtest Results
          </CardTitle>
          <CardDescription>Run a backtest to see performance metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No backtest results available. Click "Run Backtest" to analyze strategy performance.
          </p>
        </CardContent>
      </Card>
    )
  }

  const equityData =
    results.equity_curve?.map((point, index) => ({
      index,
      equity: point.equity,
      timestamp: new Date(point.timestamp).toLocaleDateString(),
    })) || []

  const winRate = results.total_trades > 0 ? ((results.winning_trades / results.total_trades) * 100).toFixed(1) : 0

  return (
    <div className="space-y-6">
      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Backtest Performance
          </CardTitle>
          <CardDescription>Strategy performance metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Return</p>
              <div className="flex items-center gap-2">
                {results.total_return >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-lg font-bold ${results.total_return >= 0 ? "text-green-500" : "text-red-500"}`}>
                  {results.total_return.toFixed(2)}%
                </span>
              </div>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Max Drawdown</p>
              <p className="text-lg font-bold text-red-500">{results.max_drawdown.toFixed(2)}%</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
              <p className="text-lg font-bold text-foreground">{results.sharpe_ratio.toFixed(2)}</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <p className="text-lg font-bold text-foreground">{winRate}%</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Equity Curve */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Equity Curve
          </CardTitle>
          <CardDescription>Portfolio value over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="index" className="text-xs" tick={{ fontSize: 10 }} />
                <YAxis
                  className="text-xs"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "6px",
                  }}
                  formatter={(value) => [`$${value?.toLocaleString()}`, "Equity"]}
                />
                <Line type="monotone" dataKey="equity" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Trade Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Trade Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">{results.total_trades}</p>
              <p className="text-sm text-muted-foreground">Total Trades</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-500">{results.winning_trades}</p>
              <p className="text-sm text-muted-foreground">Winning</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-500">{results.losing_trades}</p>
              <p className="text-sm text-muted-foreground">Losing</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
