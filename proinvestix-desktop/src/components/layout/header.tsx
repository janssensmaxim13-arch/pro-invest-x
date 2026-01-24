'use client'

import { Bell, Search, Menu, LogOut, User, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'
import { getInitials } from '@/lib/utils'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuthStore()
  const router = useRouter()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    logout()
    router.push('/auth/login')
  }

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6">
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Search */}
      <div className="flex-1">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Zoeken..."
            className="pl-9"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-white">
            3
          </span>
        </Button>

        {/* User menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 rounded-lg p-2 hover:bg-muted"
          >
            <Avatar className="h-8 w-8">
              <AvatarImage src="" />
              <AvatarFallback className="bg-primary text-white">
                {user ? getInitials(user.username) : 'U'}
              </AvatarFallback>
            </Avatar>
            <div className="hidden text-left md:block">
              <p className="text-sm font-medium">{user?.username || 'Gebruiker'}</p>
              <p className="text-xs text-muted-foreground">{user?.role || 'User'}</p>
            </div>
          </button>

          {/* Dropdown menu */}
          {showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-56 rounded-lg border bg-card p-2 shadow-lg">
              <div className="border-b pb-2 mb-2">
                <p className="px-3 py-1 text-sm font-medium">{user?.email}</p>
              </div>
              <button
                onClick={() => {
                  router.push('/profile')
                  setShowUserMenu(false)
                }}
                className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-muted"
              >
                <User className="h-4 w-4" />
                Profiel
              </button>
              <button
                onClick={() => {
                  router.push('/settings')
                  setShowUserMenu(false)
                }}
                className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm hover:bg-muted"
              >
                <Settings className="h-4 w-4" />
                Instellingen
              </button>
              <div className="border-t mt-2 pt-2">
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  Uitloggen
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
