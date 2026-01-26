'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/store/auth'

export default function LoginPage() {
  const router = useRouter()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [formError, setFormError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    clearError()

    // Validatie
    if (!email) {
      setFormError('Email is verplicht')
      return
    }
    if (!password) {
      setFormError('Wachtwoord is verplicht')
      return
    }

    try {
      await login(email, password)
      router.push('/dashboard')
    } catch (err) {
      // Error wordt al afgehandeld in de store
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br from-green-500 to-red-500 mb-4">
              <span className="text-3xl font-bold text-white">P</span>
            </div>
          </Link>
          <h1 className="text-2xl font-bold text-white">ProInvestiX Enterprise</h1>
          <p className="text-gray-400 mt-1">Log in op je account</p>
        </div>

        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Inloggen</CardTitle>
            <CardDescription className="text-gray-400">
              Voer je gegevens in om toegang te krijgen tot het platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {(error || formError) && (
                <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-400 text-sm">
                  {error || formError}
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-300">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="john@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-gray-700 border-gray-600 text-white placeholder:text-gray-500"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-gray-300">
                  Wachtwoord
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white placeholder:text-gray-500 pr-16"
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white text-sm"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? 'Verberg' : 'Toon'}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-gray-400">
                  <input type="checkbox" className="rounded border-gray-600 bg-gray-700" />
                  Onthoud mij
                </label>
                <Link
                  href="/auth/forgot-password"
                  className="text-sm text-green-500 hover:text-green-400"
                >
                  Wachtwoord vergeten?
                </Link>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white"
                disabled={isLoading}
              >
                {isLoading ? 'Bezig met inloggen...' : 'Inloggen'}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-gray-400">Nog geen account? </span>
              <Link href="/auth/register" className="text-green-500 hover:text-green-400">
                Registreer hier
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Back to home */}
        <div className="text-center mt-6">
          <Link href="/" className="text-gray-400 hover:text-white text-sm">
            ← Terug naar home
          </Link>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-500 mt-6">
          &copy; 2024 ProInvestiX. Alle rechten voorbehouden.
        </p>
      </div>
    </div>
  )
}
