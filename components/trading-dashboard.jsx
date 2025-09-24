"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Play, Pause, Square, Activity, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

import PriceChart from "./price-chart"
import PortfolioPanel from "./portfolio-panel"
import TradeLog from "./trade-log"
import BacktestResults from "./backtest-results"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Mock data for when backend is not available
const MOCK_HISTORICAL_DATA = [
  { timestamp: "2024-01-01T09:30:00Z", open: 150, high: 155, low: 148, close: 152, volume: 1000000 },
  { timestamp: "2024-01-01T09:31:00Z", open: 152, high: 154, low: 151, close: 153, volume: 950000 },
  { timestamp: "2024-01-01T09:32:00Z", open: 153, high: 156, low: 152, close: 155, volume: 1100000 },
  { timestamp: "2024-01-01T09:33:00Z", open: 155, high: 157, low: 154, close: 156, volume: 980000 },
  { timestamp: "2024-01-01T09:34:00Z", open: 156, high: 158, low: 155, close: 157, volume: 1050000 },
]

export default function TradingDashboard() {
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentSymbol, setCurrentSymbol] = useState("AAPL")
  const [marketData, setMarketData] = useState(MOCK_HISTORICAL_DATA)
  const [signals, setSignals] = useState({})
  const [portfolio, setPortfolio] = useState({ cash: 100000, total_value: 100000, total_pnl: 0 })
  const [trades, setTrades] = useState([])
  const [backtestResults, setBacktestResults] = useState(null)
  const [selectedStrategy, setSelectedStrategy] = useState("sma")
  const [backendConnected, setBackendConnected] = useState(false)
  const [connectionError, setConnectionError] = useState("")
  const wsRef = useRef(null)

  useEffect(() => {
    // Check backend connection first
    checkBackendConnection()
    // Load initial data
    loadHistoricalData()
    loadPortfolio()
    loadTrades()
  }, [currentSymbol])

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`, {
        method: "GET",
        signal: AbortSignal.timeout(5000), // 5 second timeout
      })
      if (response.ok) {
        setBackendConnected(true)
        setConnectionError("")
        console.log("[v0] Backend connected successfully")
      } else {
        throw new Error(`Backend returned ${response.status}`)
      }
    } catch (error) {
      setBackendConnected(false)
      setConnectionError(error.message)
      console.log("[v0] Backend not available, using mock data")
    }
  }

  const loadHistoricalData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/historical/${currentSymbol}?days=30`, {
        signal: AbortSignal.timeout(10000),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      setMarketData(data.data || MOCK_HISTORICAL_DATA)
      console.log("[v0] Loaded historical data from backend")
    } catch (error) {
      console.log("[v0] Using mock historical data:", error.message)
      // Use mock data when backend is not available
      setMarketData(MOCK_HISTORICAL_DATA)
    }
  }

  const loadPortfolio = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/portfolio`, {
        signal: AbortSignal.timeout(5000),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      setPortfolio(data)
      console.log("[v0] Loaded portfolio from backend")
    } catch (error) {
      console.log("[v0] Using mock portfolio data:", error.message)
      // Keep default portfolio when backend is not available
    }
  }

  const loadTrades = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/trades`, {
        signal: AbortSignal.timeout(5000),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      setTrades(data || [])
      console.log("[v0] Loaded trades from backend")
    } catch (error) {
      console.log("[v0] Using mock trades data:", error.message)
      // Keep empty trades when backend is not available
    }
  }

  const connectWebSocket = () => {
    if (!backendConnected) {
      console.log("[v0] Cannot connect WebSocket - backend not available")
      return
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      wsRef.current = new WebSocket(`ws://localhost:8000/ws`)

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

      wsRef.current.onerror = (error) => {
        console.log("[v0] WebSocket error:", error)
      }
    } catch (error) {
      console.log("[v0] WebSocket connection failed:", error)
    }
  }

  const startStreaming = () => {
    if (!backendConnected) {
      console.log("[v0] Starting mock streaming simulation")
      setIsStreaming(true)
      simulateMockStreaming()
      return
    }

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

  const simulateMockStreaming = () => {
    const interval = setInterval(() => {
      if (!isStreaming) {
        clearInterval(interval)
        return
      }

      // Generate mock price movement
      const lastPrice = marketData[marketData.length - 1]?.close || 150
      const change = (Math.random() - 0.5) * 2 // Random change between -1 and 1
      const newPrice = Math.max(lastPrice + change, 1)

      const newCandle = {
        timestamp: new Date().toISOString(),
        open: lastPrice,
        high: Math.max(lastPrice, newPrice),
        low: Math.min(lastPrice, newPrice),
        close: newPrice,
        volume: Math.floor(Math.random() * 1000000) + 500000,
      }

      setMarketData((prev) => [...prev.slice(-999), newCandle])

      // Mock signals occasionally
      if (Math.random() < 0.1) {
        // 10% chance of signal
        setSignals({
          sma: Math.random() > 0.5 ? "buy" : "sell",
          timestamp: new Date().toISOString(),
        })
      }
    }, 2000) // Update every 2 seconds
  }

  const stopStreaming = () => {
    if (backendConnected && wsRef.current?.readyState === WebSocket.OPEN) {
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
      const response = await fetch(`${API_BASE_URL}/api/backtest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: currentSymbol,
          strategy: selectedStrategy,
          days: 30,
          initial_cash: 100000,
          strategy_params: getStrategyParams(),
        }),
        signal: AbortSignal.timeout(30000),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      setBacktestResults(data.result)
    } catch (error) {
      console.log("[v0] Backtest failed, using mock results:", error.message)
      setBacktestResults({
        total_return: 15.5,
        total_trades: 24,
        winning_trades: 15,
        losing_trades: 9,
        max_drawdown: -5.2,
        sharpe_ratio: 1.8,
        equity_curve: [100000, 102000, 101500, 103000, 105000, 108000, 115500],
        trades: [
          { timestamp: "2024-01-01T10:00:00Z", action: "buy", quantity: 100, price: 150, pnl: 0 },
          { timestamp: "2024-01-01T11:00:00Z", action: "sell", quantity: 100, price: 155, pnl: 500 },
        ],
      })
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
      await fetch(`${API_BASE_URL}/api/portfolio/reset`, {
        method: "POST",
        signal: AbortSignal.timeout(5000),
      })
      loadPortfolio()
      loadTrades()
    } catch (error) {
      console.log("[v0] Portfolio reset failed, resetting locally:", error.message)
      setPortfolio({ cash: 100000, total_value: 100000, total_pnl: 0 })
      setTrades([])
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
            <Badge variant={backendConnected ? "default" : "destructive"}>
              {backendConnected ? "API Connected" : "Mock Mode"}
            </Badge>
          </div>
        </div>

        {!backendConnected && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Backend API not available ({connectionError}). Running in mock mode with sample data. To connect to real
              backend, ensure FastAPI server is running on port 8000.
            </AlertDescription>
          </Alert>
        )}

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
