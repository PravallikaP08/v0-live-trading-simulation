"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ArrowUpCircle, ArrowDownCircle, Clock } from "lucide-react"

export default function TradeLog({ trades = [] }) {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString()
  }

  const getTradeIcon = (action) => {
    return action === "BUY" ? (
      <ArrowUpCircle className="h-4 w-4 text-green-500" />
    ) : (
      <ArrowDownCircle className="h-4 w-4 text-red-500" />
    )
  }

  const getTradeColor = (action) => {
    return action === "BUY" ? "text-green-500" : "text-red-500"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Trade Log
        </CardTitle>
        <CardDescription>
          {trades.length} trade{trades.length !== 1 ? "s" : ""} executed
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px]">
          {trades.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">No trades executed yet</p>
          ) : (
            <div className="space-y-3">
              {trades.map((trade, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-3">
                    {getTradeIcon(trade.action)}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{trade.symbol}</span>
                        <Badge
                          variant={trade.action === "BUY" ? "default" : "secondary"}
                          className={getTradeColor(trade.action)}
                        >
                          {trade.action}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{formatTimestamp(trade.timestamp)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">
                      {trade.quantity} @ ${trade.price?.toFixed(2)}
                    </p>
                    <p className="text-sm text-muted-foreground">${(trade.quantity * trade.price).toFixed(2)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
