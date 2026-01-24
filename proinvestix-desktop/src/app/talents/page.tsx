'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { 
  Plus, Search, Filter, Download, ChevronLeft, ChevronRight,
  MapPin, Calendar, Star, TrendingUp, Users
} from 'lucide-react'
import { talentsApi } from '@/lib/api'
import { formatDate, getInitials, calculateAge, getStatusColor } from '@/lib/utils'
import type { Talent } from '@/types'

function TalentCard({ talent }: { talent: Talent }) {
  return (
    <Link href={`/talents/${talent.id}`}>
      <Card className="card-hover cursor-pointer">
        <CardContent className="p-4">
          <div className="flex items-start gap-4">
            <Avatar className="h-12 w-12">
              <AvatarFallback className="bg-primary text-white">
                {getInitials(`${talent.first_name} ${talent.last_name}`)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold truncate">
                  {talent.first_name} {talent.last_name}
                </h3>
                <Badge variant={talent.status === 'Active' ? 'success' : 'muted'}>
                  {talent.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{talent.position}</p>
              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {calculateAge(talent.date_of_birth)} jaar
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {talent.nationality}
                </span>
                {talent.scout_rating && (
                  <span className="flex items-center gap-1">
                    <Star className="h-3 w-3 text-yellow-500" />
                    {talent.scout_rating}/10
                  </span>
                )}
              </div>
              {talent.current_club && (
                <p className="text-sm mt-1">{talent.current_club}</p>
              )}
              {talent.is_diaspora && (
                <Badge variant="info" className="mt-2">
                  Diaspora • {talent.diaspora_country}
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}

function TalentStats() {
  const { data: stats } = useQuery({
    queryKey: ['talent-stats'],
    queryFn: () => talentsApi.getStats().then(res => res.data),
  })

  return (
    <div className="grid gap-4 md:grid-cols-4">
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <Users className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.total_talents || 0}</p>
              <p className="text-sm text-muted-foreground">Totaal Talenten</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.high_potential || 0}</p>
              <p className="text-sm text-muted-foreground">Hoog Potentieel</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
              <MapPin className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.diaspora_count || 0}</p>
              <p className="text-sm text-muted-foreground">Diaspora Talenten</p>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-yellow-100 flex items-center justify-center">
              <Star className="h-5 w-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.avg_rating?.toFixed(1) || '-'}</p>
              <p className="text-sm text-muted-foreground">Gem. Rating</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function TalentsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({
    nationality: '',
    position: '',
    is_diaspora: undefined as boolean | undefined,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['talents', page, search, filters],
    queryFn: () => talentsApi.list({ 
      page, 
      per_page: 12,
      search: search || undefined,
      ...filters,
    }).then(res => res.data),
  })

  const talents = data?.data || []
  const meta = data?.meta || { total: 0, page: 1, per_page: 12, total_pages: 1 }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="page-title">Talenten</h1>
            <p className="page-description">
              Beheer en ontdek voetbaltalenten uit Marokko en de diaspora
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Exporteren
            </Button>
            <Link href="/talents/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Talent Toevoegen
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats */}
        <TalentStats />

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col gap-4 md:flex-row md:items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Zoek op naam, club of nationaliteit..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
              <div className="flex gap-2">
                <select
                  className="rounded-md border px-3 py-2 text-sm"
                  value={filters.position}
                  onChange={(e) => setFilters({ ...filters, position: e.target.value })}
                >
                  <option value="">Alle posities</option>
                  <option value="Goalkeeper">Keeper</option>
                  <option value="Defender">Verdediger</option>
                  <option value="Midfielder">Middenvelder</option>
                  <option value="Forward">Aanvaller</option>
                </select>
                <select
                  className="rounded-md border px-3 py-2 text-sm"
                  value={filters.is_diaspora?.toString() || ''}
                  onChange={(e) => setFilters({ 
                    ...filters, 
                    is_diaspora: e.target.value === '' ? undefined : e.target.value === 'true'
                  })}
                >
                  <option value="">Alle</option>
                  <option value="true">Diaspora</option>
                  <option value="false">Lokaal</option>
                </select>
                <Button variant="outline" size="icon">
                  <Filter className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Talent Grid */}
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-4">
                  <div className="flex gap-4">
                    <div className="h-12 w-12 rounded-full bg-muted" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-muted rounded w-3/4" />
                      <div className="h-3 bg-muted rounded w-1/2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : talents.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {talents.map((talent: Talent) => (
              <TalentCard key={talent.id} talent={talent} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="p-12 text-center">
              <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="font-semibold mb-2">Geen talenten gevonden</h3>
              <p className="text-muted-foreground mb-4">
                Pas je zoekcriteria aan of voeg een nieuw talent toe
              </p>
              <Link href="/talents/new">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Talent Toevoegen
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Pagination */}
        {meta.total_pages > 1 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Toont {(meta.page - 1) * meta.per_page + 1} - {Math.min(meta.page * meta.per_page, meta.total)} van {meta.total}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
                Vorige
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page === meta.total_pages}
                onClick={() => setPage(page + 1)}
              >
                Volgende
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
