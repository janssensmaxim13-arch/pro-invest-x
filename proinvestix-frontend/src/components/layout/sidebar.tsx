'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Users,
  UserSearch,
  ArrowLeftRight,
  Ticket,
  Calendar,
  Wallet,
  Heart,
  GraduationCap,
  CreditCard,
  Flag,
  Shield,
  Fingerprint,
  IdCard,
  Brain,
  Ban,
  Newspaper,
  Building,
  Settings,
  ChevronDown,
  Trophy,
} from 'lucide-react'
import { useState } from 'react'

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  children?: { title: string; href: string }[]
}

const navigation: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'NTSP',
    href: '/talents',
    icon: Trophy,
    children: [
      { title: 'Talenten', href: '/talents' },
      { title: 'Scouts', href: '/scouts' },
    ],
  },
  {
    title: 'Transfers',
    href: '/transfers',
    icon: ArrowLeftRight,
    children: [
      { title: 'Overzicht', href: '/transfers' },
      { title: 'Calculator', href: '/transfers/calculator' },
    ],
  },
  {
    title: 'TicketChain',
    href: '/events',
    icon: Ticket,
    children: [
      { title: 'Evenementen', href: '/events' },
      { title: 'Mijn Tickets', href: '/tickets' },
    ],
  },
  {
    title: 'Wallet',
    href: '/wallets',
    icon: Wallet,
  },
  {
    title: 'Foundation',
    href: '/foundation',
    icon: Heart,
    children: [
      { title: 'Doneren', href: '/foundation/donate' },
      { title: 'Projecten', href: '/foundation/projects' },
    ],
  },
  {
    title: 'Academy',
    href: '/academies',
    icon: GraduationCap,
  },
  {
    title: 'Abonnementen',
    href: '/subscriptions',
    icon: CreditCard,
  },
  {
    title: 'FanDorpen',
    href: '/fandorpen',
    icon: Flag,
  },
  {
    title: 'FRMF',
    href: '/frmf',
    icon: Shield,
    children: [
      { title: 'Scheidsrechters', href: '/frmf/referees' },
      { title: 'VAR Beslissingen', href: '/frmf/var-decisions' },
      { title: 'Spelers', href: '/frmf/players' },
    ],
  },
  {
    title: 'Identity Shield',
    href: '/identities',
    icon: Fingerprint,
  },
  {
    title: 'Maroc ID',
    href: '/maroc-id',
    icon: IdCard,
    children: [
      { title: 'Mijn ID', href: '/maroc-id' },
      { title: 'Certificaten', href: '/maroc-id/certificates' },
    ],
  },
  {
    title: 'Hayat',
    href: '/hayat',
    icon: Brain,
    children: [
      { title: 'Sessies', href: '/hayat/sessions' },
      { title: 'Crisis', href: '/hayat/crisis' },
    ],
  },
  {
    title: 'Anti-Hate',
    href: '/antihate',
    icon: Ban,
    children: [
      { title: 'Incidenten', href: '/antihate/incidents' },
      { title: 'Juridisch', href: '/antihate/legal' },
    ],
  },
  {
    title: 'NIL',
    href: '/nil',
    icon: Newspaper,
    children: [
      { title: 'Signalen', href: '/nil/signals' },
      { title: 'Factcards', href: '/nil/factcards' },
    ],
  },
  {
    title: 'Consulaat',
    href: '/consulate',
    icon: Building,
    children: [
      { title: 'Documenten', href: '/consulate/documents' },
      { title: 'Afspraken', href: '/consulate/appointments' },
    ],
  },
]

const adminNavigation: NavItem[] = [
  {
    title: 'Admin',
    href: '/admin',
    icon: Settings,
    children: [
      { title: 'Gebruikers', href: '/admin/users' },
      { title: 'Sessies', href: '/admin/sessions' },
      { title: 'Audit Log', href: '/admin/audit' },
      { title: 'Instellingen', href: '/admin/settings' },
    ],
  },
]

function NavItemComponent({ item }: { item: NavItem }) {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)
  const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
  const hasChildren = item.children && item.children.length > 0

  if (hasChildren) {
    return (
      <div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors',
            isActive
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          )}
        >
          <div className="flex items-center gap-3">
            <item.icon className="h-4 w-4" />
            <span>{item.title}</span>
          </div>
          <ChevronDown
            className={cn('h-4 w-4 transition-transform', isOpen && 'rotate-180')}
          />
        </button>
        {isOpen && (
          <div className="ml-7 mt-1 space-y-1">
            {item.children.map((child) => (
              <Link
                key={child.href}
                href={child.href}
                className={cn(
                  'block rounded-lg px-3 py-2 text-sm transition-colors',
                  pathname === child.href
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                {child.title}
              </Link>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <Link
      href={item.href}
      className={cn(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
        isActive
          ? 'bg-primary/10 text-primary'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
    >
      <item.icon className="h-4 w-4" />
      <span>{item.title}</span>
    </Link>
  )
}

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <span className="text-lg font-bold text-white">P</span>
          </div>
          <span className="text-lg font-bold">ProInvestiX</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="h-[calc(100vh-4rem)] overflow-y-auto p-4 scrollbar-thin">
        <div className="space-y-1">
          {navigation.map((item) => (
            <NavItemComponent key={item.href} item={item} />
          ))}
        </div>

        {/* Admin Section */}
        <div className="mt-6 border-t pt-4">
          <p className="mb-2 px-3 text-xs font-semibold uppercase text-muted-foreground">
            Beheer
          </p>
          {adminNavigation.map((item) => (
            <NavItemComponent key={item.href} item={item} />
          ))}
        </div>
      </nav>
    </aside>
  )
}
