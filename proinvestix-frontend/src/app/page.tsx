'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Trophy, 
  Users, 
  Ticket, 
  Wallet, 
  Heart, 
  Shield,
  ArrowRight,
  Star,
  Globe,
  Zap
} from 'lucide-react'

// WK 2030 datum (13 juni 2030 - verwachte start)
const WK_2030_DATE = new Date('2030-06-13T00:00:00')

interface TimeLeft {
  days: number
  hours: number
  minutes: number
  seconds: number
}

function calculateTimeLeft(): TimeLeft {
  const difference = WK_2030_DATE.getTime() - new Date().getTime()
  
  return {
    days: Math.floor(difference / (1000 * 60 * 60 * 24)),
    hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
    minutes: Math.floor((difference / 1000 / 60) % 60),
    seconds: Math.floor((difference / 1000) % 60),
  }
}

function CountdownBox({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col items-center">
      <div className="bg-gradient-to-br from-green-600 to-red-600 text-white text-3xl md:text-5xl font-bold rounded-xl w-20 h-20 md:w-28 md:h-28 flex items-center justify-center shadow-lg">
        {value.toString().padStart(2, '0')}
      </div>
      <span className="text-gray-300 mt-2 text-sm md:text-base uppercase tracking-wider">{label}</span>
    </div>
  )
}

const features = [
  {
    icon: Trophy,
    title: 'NTSP',
    description: 'National Talent Scouting Platform - Ontdek de sterren van morgen',
    color: 'from-yellow-500 to-orange-500',
  },
  {
    icon: Users,
    title: 'Transfers',
    description: 'Transparante transfer management en compensatie berekening',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Ticket,
    title: 'TicketChain',
    description: 'Blockchain-beveiligde tickets - Geen fraude, geen zwarte markt',
    color: 'from-purple-500 to-pink-500',
  },
  {
    icon: Wallet,
    title: 'Diaspora Wallet',
    description: 'Digitale wallet voor de Marokkaanse diaspora wereldwijd',
    color: 'from-green-500 to-emerald-500',
  },
  {
    icon: Heart,
    title: 'Foundation Bank',
    description: 'Sadaka Jaaria - Investeer in de toekomst van Marokkaans voetbal',
    color: 'from-red-500 to-rose-500',
  },
  {
    icon: Shield,
    title: 'Identity Shield',
    description: 'Bescherm je identiteit met geavanceerde verificatie',
    color: 'from-indigo-500 to-violet-500',
  },
]

const stats = [
  { value: '200+', label: 'API Endpoints' },
  { value: '52', label: 'Paginas' },
  { value: '20', label: 'Modules' },
  { value: '2030', label: 'WK Gereed' },
]

export default function Home() {
  const [timeLeft, setTimeLeft] = useState<TimeLeft>(calculateTimeLeft())
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900">
      {/* Hero Section */}
      <header className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <nav className="relative z-10 flex items-center justify-between px-6 py-4 md:px-12">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-red-500">
              <span className="text-xl font-bold text-white">P</span>
            </div>
            <span className="text-xl font-bold text-white">ProInvestiX</span>
          </div>
          <div className="flex items-center gap-4">
            <Link 
              href="/auth/login"
              className="text-gray-300 hover:text-white transition-colors"
            >
              Login
            </Link>
            <Link 
              href="/auth/register"
              className="bg-gradient-to-r from-green-600 to-red-600 text-white px-6 py-2 rounded-lg font-medium hover:opacity-90 transition-opacity"
            >
              Registreer
            </Link>
          </div>
        </nav>

        <div className="relative z-10 flex flex-col items-center justify-center px-6 py-20 text-center">
          {/* Moroccan Flag Colors Accent */}
          <div className="flex gap-2 mb-6">
            <div className="w-12 h-1 bg-green-500 rounded-full" />
            <div className="w-12 h-1 bg-red-500 rounded-full" />
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-4">
            ProInvestiX
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-2">
            National Investment Platform for Football Development
          </p>
          <p className="text-lg text-gray-400 mb-12 max-w-2xl">
            Het complete ecosysteem voor Marokkaans voetbal - Van talent scouting tot WK 2030
          </p>

          {/* WK 2030 Countdown */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 mb-12 border border-gray-700">
            <div className="flex items-center justify-center gap-2 mb-6">
              <Globe className="w-6 h-6 text-green-500" />
              <h2 className="text-xl md:text-2xl font-bold text-white">
                🇲🇦 WK 2030 Countdown 🇪🇸 🇵🇹
              </h2>
            </div>
            <div className="flex gap-4 md:gap-8 justify-center">
              <CountdownBox value={timeLeft.days} label="Dagen" />
              <CountdownBox value={timeLeft.hours} label="Uren" />
              <CountdownBox value={timeLeft.minutes} label="Minuten" />
              <CountdownBox value={timeLeft.seconds} label="Seconden" />
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Link 
              href="/auth/register"
              className="flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-green-500 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:opacity-90 transition-opacity shadow-lg"
            >
              Start Nu <ArrowRight className="w-5 h-5" />
            </Link>
            <Link 
              href="/dashboard"
              className="flex items-center justify-center gap-2 bg-gray-700 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-600 transition-colors"
            >
              Bekijk Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Stats Section */}
      <section className="py-16 px-6 bg-gray-800/50">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-white mb-2">
                {stat.value}
              </div>
              <div className="text-gray-400">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Alles-in-één Platform
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Van talent scouting tot blockchain tickets - ProInvestiX biedt alle tools voor de toekomst van Marokkaans voetbal
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-colors group"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-green-600/20 to-red-600/20 rounded-2xl p-12 border border-gray-700">
            <Zap className="w-12 h-12 text-yellow-500 mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Klaar om te beginnen?
            </h2>
            <p className="text-gray-300 text-lg mb-8">
              Sluit je aan bij duizenden gebruikers die al profiteren van ProInvestiX
            </p>
            <Link 
              href="/auth/register"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-green-600 to-red-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:opacity-90 transition-opacity"
            >
              Maak Gratis Account <Star className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-gray-800">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-green-500 to-red-500">
              <span className="text-sm font-bold text-white">P</span>
            </div>
            <span className="text-white font-semibold">ProInvestiX</span>
          </div>
          <div className="text-gray-400 text-sm">
            © 2024 ProInvestiX. National Investment Platform for Football Development.
          </div>
          <div className="flex gap-6">
            <Link href="/auth/login" className="text-gray-400 hover:text-white transition-colors">
              Login
            </Link>
            <Link href="/auth/register" className="text-gray-400 hover:text-white transition-colors">
              Registreer
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
