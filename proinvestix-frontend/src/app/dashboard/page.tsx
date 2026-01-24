'use client'

import { useEffect, useState } from 'react'
import { DashboardLayout } from '@/components/layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Users, Trophy, ArrowLeftRight, Ticket, Wallet, TrendingUp, 
  TrendingDown, Calendar, Activity 
} from 'lucide-react'
import { formatCurrency, formatNumber, formatRelativeTime } from '@/lib/utils'
import { dashboardApi } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  icon: React.ComponentType<{ className?: string }>
  trend?: 'up' | 'down' | 'neutral'
}

function StatCard({ title, value, change, icon: Icon, trend }: StatCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {change !== undefined && (
              <div className="flex items-center mt-1">
                {trend === 'up' ? (
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                ) : trend === 'down' ? (
                  <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                ) : null}
                <span className={`text-sm ${
                  trend === 'up' ? 'text-green-500' : 
                  trend === 'down' ? 'text-red-500' : 'text-muted-foreground'
                }`}>
                  {change > 0 ? '+' : ''}{change}%
                </span>
              </div>
            )}
          </div>
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface ActivityItem {
  id: string
  type: string
  message: string
  timestamp: string
}

function ActivityFeed({ activities }: { activities: ActivityItem[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Recente Activiteit
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3">
              <div className="h-2 w-2 rounded-full bg-primary mt-2" />
              <div className="flex-1">
                <p className="text-sm">{activity.message}</p>
                <p className="text-xs text-muted-foreground">
                  {formatRelativeTime(activity.timestamp)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function WKCountdown() {
  const [countdown, setCountdown] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  })

  useEffect(() => {
    // WK 2030 start datum (geschat)
    const wkDate = new Date('2030-06-13T00:00:00')
    
    const updateCountdown = () => {
      const now = new Date()
      const diff = wkDate.getTime() - now.getTime()
      
      setCountdown({
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((diff % (1000 * 60)) / 1000),
      })
    }
    
    updateCountdown()
    const interval = setInterval(updateCountdown, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <Card className="gradient-morocco text-white">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold">WK 2030</h3>
            <p className="text-sm opacity-80">Marokko • Spanje • Portugal</p>
          </div>
          <Trophy className="h-8 w-8 opacity-80" />
        </div>
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-3xl font-bold">{countdown.days}</p>
            <p className="text-xs opacity-80">Dagen</p>
          </div>
          <div>
            <p className="text-3xl font-bold">{countdown.hours}</p>
            <p className="text-xs opacity-80">Uren</p>
          </div>
          <div>
            <p className="text-3xl font-bold">{countdown.minutes}</p>
            <p className="text-xs opacity-80">Min</p>
          </div>
          <div>
            <p className="text-3xl font-bold">{countdown.seconds}</p>
            <p className="text-xs opacity-80">Sec</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  // Mock data - in productie vervangen door API calls
  const stats = {
    totalTalents: 1247,
    totalTransfers: 89,
    transferVolume: 45000000,
    ticketsSold: 15420,
    activeWallets: 8932,
    academies: 47,
  }

  const activities: ActivityItem[] = [
    { id: '1', type: 'transfer', message: 'Nieuwe transfer: Youssef B. → Ajax Amsterdam', timestamp: new Date().toISOString() },
    { id: '2', type: 'talent', message: 'Talent geregistreerd: Mohamed K. (U17)', timestamp: new Date(Date.now() - 3600000).toISOString() },
    { id: '3', type: 'ticket', message: '250 tickets verkocht voor WAC vs RSB', timestamp: new Date(Date.now() - 7200000).toISOString() },
    { id: '4', type: 'donation', message: 'Donatie ontvangen: €500 voor Academy Support', timestamp: new Date(Date.now() - 10800000).toISOString() },
    { id: '5', type: 'event', message: 'Nieuw evenement: FRMF Scheidsrechtersexamen', timestamp: new Date(Date.now() - 14400000).toISOString() },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="page-header">
          <h1 className="page-title">Dashboard</h1>
          <p className="page-description">
            Welkom terug! Hier is een overzicht van het platform.
          </p>
        </div>

        {/* WK Countdown */}
        <WKCountdown />

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <StatCard
            title="Talenten"
            value={formatNumber(stats.totalTalents)}
            change={12}
            trend="up"
            icon={Users}
          />
          <StatCard
            title="Transfers"
            value={stats.totalTransfers}
            change={8}
            trend="up"
            icon={ArrowLeftRight}
          />
          <StatCard
            title="Transfer Volume"
            value={formatCurrency(stats.transferVolume)}
            change={-3}
            trend="down"
            icon={TrendingUp}
          />
          <StatCard
            title="Tickets Verkocht"
            value={formatNumber(stats.ticketsSold)}
            change={24}
            trend="up"
            icon={Ticket}
          />
          <StatCard
            title="Actieve Wallets"
            value={formatNumber(stats.activeWallets)}
            change={15}
            trend="up"
            icon={Wallet}
          />
          <StatCard
            title="Academies"
            value={stats.academies}
            change={2}
            trend="up"
            icon={Trophy}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Activity Feed */}
          <div className="lg:col-span-2">
            <ActivityFeed activities={activities} />
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Snelle Acties</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <a
                href="/talents/new"
                className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted transition-colors"
              >
                <Users className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Talent Registreren</span>
              </a>
              <a
                href="/transfers/new"
                className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted transition-colors"
              >
                <ArrowLeftRight className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Transfer Aanmaken</span>
              </a>
              <a
                href="/events/new"
                className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted transition-colors"
              >
                <Calendar className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Evenement Plannen</span>
              </a>
              <a
                href="/foundation/donate"
                className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted transition-colors"
              >
                <Wallet className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Doneren</span>
              </a>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
