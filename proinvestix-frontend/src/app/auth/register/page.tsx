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

const registerSchema = z.object({
  username: z.string().min(3, 'Minimaal 3 tekens'),
  email: z.string().email('Ongeldig e-mailadres'),
  password: z.string().min(8, 'Minimaal 8 tekens'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Wachtwoorden komen niet overeen',
  path: ['confirmPassword'],
})

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const { register: registerUser, isLoading } = useAuthStore()
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterForm) => {
    try {
      await registerUser(data.username, data.email, data.password)
      toast.success('Account aangemaakt! Je kunt nu inloggen.')
      router.push('/auth/login')
    } catch (err) {
      toast.error('Registratie mislukt')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-primary mb-4">
            <span className="text-3xl font-bold text-white">P</span>
          </div>
          <h1 className="text-2xl font-bold">Registreren</h1>
        </div>
        <Card>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="text-sm font-medium">Gebruikersnaam</label>
                <Input {...register('username')} error={errors.username?.message} />
              </div>
              <div>
                <label className="text-sm font-medium">E-mail</label>
                <Input type="email" {...register('email')} error={errors.email?.message} />
              </div>
              <div>
                <label className="text-sm font-medium">Wachtwoord</label>
                <Input type="password" {...register('password')} error={errors.password?.message} />
              </div>
              <div>
                <label className="text-sm font-medium">Bevestig wachtwoord</label>
                <Input type="password" {...register('confirmPassword')} error={errors.confirmPassword?.message} />
              </div>
              <Button type="submit" className="w-full" isLoading={isLoading}>Registreren</Button>
            </form>
            <p className="text-center text-sm mt-4">
              Al een account? <Link href="/auth/login" className="text-primary hover:underline">Inloggen</Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
