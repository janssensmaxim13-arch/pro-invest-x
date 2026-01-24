'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuthStore } from '@/store/auth'
import { toast } from 'sonner'

const loginSchema = z.object({
  username: z.string().min(1, 'Gebruikersnaam is verplicht'),
  password: z.string().min(1, 'Wachtwoord is verplicht'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data.username, data.password)
      toast.success('Succesvol ingelogd!')
      router.push('/dashboard')
    } catch (err) {
      toast.error('Inloggen mislukt. Controleer je gegevens.')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-primary mb-4">
            <span className="text-3xl font-bold text-white">P</span>
          </div>
          <h1 className="text-2xl font-bold">ProInvestiX Enterprise</h1>
          <p className="text-muted-foreground mt-1">Log in op je account</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Inloggen</CardTitle>
            <CardDescription>
              Voer je gegevens in om toegang te krijgen tot het platform
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {error && (
                <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium">
                  Gebruikersnaam
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="johndoe"
                  error={errors.username?.message}
                  {...register('username')}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Wachtwoord
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="••••••••"
                    error={errors.password?.message}
                    {...register('password')}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? 'Verberg' : 'Toon'}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" className="rounded border-gray-300" />
                  Onthoud mij
                </label>
                <Link
                  href="/auth/forgot-password"
                  className="text-sm text-primary hover:underline"
                >
                  Wachtwoord vergeten?
                </Link>
              </div>

              <Button type="submit" className="w-full" isLoading={isLoading}>
                Inloggen
              </Button>
            </form>

            <div className="mt-6 text-center text-sm">
              <span className="text-muted-foreground">Nog geen account? </span>
              <Link href="/auth/register" className="text-primary hover:underline">
                Registreer hier
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground mt-6">
          &copy; 2024 ProInvestiX. Alle rechten voorbehouden.
        </p>
      </div>
    </div>
  )
}
