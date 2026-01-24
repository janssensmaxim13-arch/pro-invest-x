'use client'

import { DashboardLayout } from '@/components/layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Construction } from 'lucide-react'

export default function AcademiesPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="page-header">
          <h1 className="page-title">Academies</h1>
          <p className="page-description">Deze pagina is in ontwikkeling</p>
        </div>
        <Card>
          <CardContent className="p-12 text-center">
            <Construction className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">Binnenkort beschikbaar</h2>
            <p className="text-muted-foreground">
              We werken hard aan deze functionaliteit. Kom snel terug!
            </p>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
