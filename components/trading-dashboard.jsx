"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Play, Pause, Square, Activity } from "lucide-react"

import PriceChart from "./price-chart"
import PortfolioPanel from "./portfolio-panel"
import TradeLog from "./trade-log"
import BacktestResults from "./backtest-results"

export default function TradingDashboard() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentSymbol, setCurrentSymbol] = useState("AAPL")
  const [marketData, setMarketData] = useState([])
  const [signals, setSignals] = useState({})
  const [portfolio, setPortfolio] = useState({ cash: 100000, total_value: 100000, total_pnl: 0 })
  const [trades, setTrades] = useState([])
  const [backtestResults, setBacktestResults] = useState(null)
  const [selectedStrategy, setSelectedStrategy] = useState("sma")
  const wsRef = useRef(null)

  useEffect(() => {
    // Load initial data
    loadHistoricalData()
    loadPortfolio()
    loadTrades()
  }, [currentSymbol])

  const loadHistoricalData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/historical/${currentSymbol}?days=30`)
      const data = await response.json()
      setMarketData(data.data || [])
    } catch (error) {
      console.error("Failed to load historical data:", error)
    }
  }

  const loadPortfolio = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/portfolio")
      const data = await response.json()
      setPortfolio(data)
    } catch (error) {
      console.error("Failed to load portfolio:", error)
    }
  }

  const loadTrades = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/trades")
      const data = await response.json()
      setTrades(data || [])
    } catch (error) {
      console.error("Failed to load trades:", error)
    }
  }

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    wsRef.current = new WebSocket("ws://localhost:8000/ws")

    wsRef.current.onopen = () => {
      console.log("[v0] WebSocket connected")
    }

    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data)

      if (message.type === "market_data") {
        setMarketData((prev) => [...prev.slice(-999), message.candle])
        setSignals(message.signals || {})
        setPortfolio(message.portfolio || portfolio)
      } else if (message.type === "trade_executed") {
        setTrades((prev) => [message.trade, ...prev])
        loadPortfolio() // Refresh portfolio
      }
    }

    wsRef.current.onclose = () => {
      console.log("[v0] WebSocket disconnected")
    }
  }

  const startStreaming = () => {
    connectWebSocket()
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "start_streaming",
          symbol: currentSymbol,
        }),
      )
      setIsStreaming(true)
    }
  }

  const stopStreaming = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "stop_streaming",
        }),
      )
    }
    setIsStreaming(false)
  }

  const runBacktest = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/backtest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: currentSymbol,
          strategy: selectedStrategy,
          days: 30,
          initial_cash: 100000,
          strategy_params: getStrategyParams(),
        }),
      })
      const data = await response.json()
      setBacktestResults(data.result)
    } catch (error) {
      console.error("Failed to run backtest:", error)
    }
  }

  const getStrategyParams = () => {
    switch (selectedStrategy) {
      case "sma":
        return { short_window: 10, long_window: 30 }
      case "rsi":
        return { period: 14, oversold: 30, overbought: 70 }
      case "bollinger":
        return { period: 20, std_dev: 2 }
      default:
        return {}
    }
  }

  const resetPortfolio = async () => {
    try {
      await fetch("http://localhost:8000/api/portfolio/reset", { method: "POST" })
      loadPortfolio()
      loadTrades()
    } catch (error) {
      console.error("Failed to reset portfolio:", error)
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Live Trading Simulation</h1>
            <p className="text-muted-foreground">Algorithmic trading system with real-time data</p>
          </div>
          <div className="flex items-center gap-4">
            <Select value={currentSymbol} onValueChange={setCurrentSymbol}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="AAPL">AAPL</SelectItem>
                <SelectItem value="GOOGL">GOOGL</SelectItem>
                <SelectItem value="MSFT">MSFT</SelectItem>
                <SelectItem value="TSLA">TSLA</SelectItem>
              </SelectContent>
            </Select>
            <Badge variant={isStreaming ? "default" : "secondary"}>{isStreaming ? "LIVE" : "PAUSED"}</Badge>
          </div>
        </div>

        {/* Control Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Trading Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Button onClick={startStreaming} disabled={isStreaming} className="flex items-center gap-2">
                <Play className="h-4 w-4" />
                Start Simulation
              </Button>
              <Button
                onClick={stopStreaming}
                disabled={!isStreaming}
                variant="outline"
                className="flex items-center gap-2 bg-transparent"
              >
                <Pause className="h-4 w-4" />
                Pause
              </Button>
              <Button onClick={resetPortfolio} variant="destructive" className="flex items-center gap-2">
                <Square className="h-4 w-4" />
                Reset Portfolio
              </Button>
              <div className="flex items-center gap-2 ml-auto">
                <Label htmlFor="strategy">Strategy:</Label>
                <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sma">SMA Crossover</SelectItem>
                    <SelectItem value="rsi">RSI Momentum</SelectItem>
                    <SelectItem value="bollinger">Bollinger Bands</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={runBacktest} variant="outline">
                  Run Backtest
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart Section */}
          <div className="lg:col-span-2">
            <PriceChart data={marketData} signals={signals} symbol={currentSymbol} />
          </div>

          {/* Portfolio Panel */}
          <div>
            <PortfolioPanel portfolio={portfolio} />
          </div>
        </div>

        {/* Bottom Section */}
        <Tabs defaultValue="trades" className="w-full">
          <TabsList>
            <TabsTrigger value="trades">Trade Log</TabsTrigger>
            <TabsTrigger value="backtest">Backtest Results</TabsTrigger>
          </TabsList>
          <TabsContent value="trades">
            <TradeLog trades={trades} />
          </TabsContent>
          <TabsContent value="backtest">
            <BacktestResults results={backtestResults} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
