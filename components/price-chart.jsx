"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { TrendingUp, TrendingDown, ArrowUp, ArrowDown } from "lucide-react"

export default function PriceChart({ data = [], signals = {}, symbol = "AAPL" }) {
  const chartData = useMemo(() => {
    return data.slice(-100).map((candle, index) => ({
      ...candle,
      timestamp: new Date(candle.timestamp).toLocaleTimeString(),
      price: candle.close,
      index,
    }))
  }, [data])

  const latestPrice = data.length > 0 ? data[data.length - 1]?.close : 0
  const previousPrice = data.length > 1 ? data[data.length - 2]?.close : latestPrice
  const priceChange = latestPrice - previousPrice
  const priceChangePercent = previousPrice ? (priceChange / previousPrice) * 100 : 0

  const getSignalColor = (signal) => {
    if (signal === 1) return "text-green-500"
    if (signal === -1) return "text-red-500"
    return "text-muted-foreground"
  }

  const getSignalIcon = (signal) => {
    if (signal === 1) return <ArrowUp className="h-4 w-4" />
    if (signal === -1) return <ArrowDown className="h-4 w-4" />
    return null
  }

  return (
    <Card className="h-[500px]">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {symbol} Price Chart
              {priceChange >= 0 ? (
                <TrendingUp className="h-5 w-5 text-green-500" />
              ) : (
                <TrendingDown className="h-5 w-5 text-red-500" />
              )}
            </CardTitle>
            <CardDescription>
              ${latestPrice?.toFixed(2)}
              <span className={priceChange >= 0 ? "text-green-500" : "text-red-500"}>
                {" "}
                ({priceChange >= 0 ? "+" : ""}
                {priceChange.toFixed(2)}, {priceChangePercent.toFixed(2)}%)
              </span>
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {Object.entries(signals).map(([strategy, signal]) => (
              <Badge
                key={strategy}
                variant={signal === 0 ? "secondary" : "default"}
                className={`flex items-center gap-1 ${getSignalColor(signal)}`}
              >
                {strategy.toUpperCase()}
                {getSignalIcon(signal)}
              </Badge>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="timestamp" className="text-xs" tick={{ fontSize: 10 }} />
            <YAxis domain={["dataMin - 1", "dataMax + 1"]} className="text-xs" tick={{ fontSize: 10 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "6px",
              }}
              formatter={(value) => [`$${value?.toFixed(2)}`, "Price"]}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "hsl(var(--primary))" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
