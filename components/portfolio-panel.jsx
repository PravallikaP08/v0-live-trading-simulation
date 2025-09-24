"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, TrendingDown, Wallet, PieChart } from "lucide-react"

export default function PortfolioPanel({ portfolio = {} }) {
  const { cash = 0, total_value = 0, total_pnl = 0, positions = [] } = portfolio

  const pnlPercentage = total_value > 0 ? (total_pnl / (total_value - total_pnl)) * 100 : 0

  return (
    <div className="space-y-4">
      {/* Portfolio Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Portfolio Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Cash</p>
              <p className="text-2xl font-bold text-foreground">${cash.toLocaleString()}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Value</p>
              <p className="text-2xl font-bold text-foreground">${total_value.toLocaleString()}</p>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">P&L</span>
              <div className="flex items-center gap-2">
                {total_pnl >= 0 ? (
                  <TrendingUp className="h-4 w-4 text-green-500" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500" />
                )}
                <span className={`font-semibold ${total_pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                  ${total_pnl.toFixed(2)} ({pnlPercentage.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Positions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="h-5 w-5" />
            Positions
          </CardTitle>
          <CardDescription>
            {positions.length} active position{positions.length !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {positions.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">No active positions</p>
          ) : (
            <div className="space-y-3">
              {positions.map((position, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                  <div>
                    <p className="font-semibold">{position.symbol}</p>
                    <p className="text-sm text-muted-foreground">
                      {position.quantity} shares @ ${position.avg_price?.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">${(position.quantity * position.current_price).toFixed(2)}</p>
                    <p className={`text-sm ${position.unrealized_pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
                      {position.unrealized_pnl >= 0 ? "+" : ""}${position.unrealized_pnl?.toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
