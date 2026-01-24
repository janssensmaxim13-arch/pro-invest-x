'use client'

import { useEffect, useState } from 'react'
import { isTauri, checkForUpdates, installUpdate, showConfirm, getAppVersion, getPlatform } from '@/lib/tauri'

interface UpdateInfo {
  available: boolean
  version?: string
  notes?: string
}

interface AppInfo {
  version: string
  platform: string
  isTauri: boolean
}

export function useDesktopUpdates() {
  const [updateInfo, setUpdateInfo] = useState<UpdateInfo>({ available: false })
  const [checking, setChecking] = useState(false)
  const [installing, setInstalling] = useState(false)

  const checkUpdates = async () => {
    if (!isTauri()) return
    
    setChecking(true)
    try {
      const info = await checkForUpdates()
      setUpdateInfo(info)
      
      if (info.available && info.version) {
        const shouldInstall = await showConfirm(
          'Update Beschikbaar',
          `Versie ${info.version} is beschikbaar. Wil je nu updaten?\n\n${info.notes || ''}`
        )
        
        if (shouldInstall) {
          await performUpdate()
        }
      }
    } catch (error) {
      console.error('Update check failed:', error)
    } finally {
      setChecking(false)
    }
  }

  const performUpdate = async () => {
    if (!isTauri()) return
    
    setInstalling(true)
    try {
      await installUpdate()
    } catch (error) {
      console.error('Update installation failed:', error)
    } finally {
      setInstalling(false)
    }
  }

  // Check for updates on mount (desktop only)
  useEffect(() => {
    if (isTauri()) {
      // Check after 5 seconds to not block initial load
      const timer = setTimeout(checkUpdates, 5000)
      return () => clearTimeout(timer)
    }
  }, [])

  return {
    updateInfo,
    checking,
    installing,
    checkUpdates,
    performUpdate,
  }
}

export function useAppInfo() {
  const [appInfo, setAppInfo] = useState<AppInfo>({
    version: '1.0.0',
    platform: 'web',
    isTauri: false,
  })

  useEffect(() => {
    async function loadInfo() {
      if (isTauri()) {
        try {
          const [version, platform] = await Promise.all([
            getAppVersion(),
            getPlatform(),
          ])
          setAppInfo({
            version,
            platform,
            isTauri: true,
          })
        } catch (error) {
          console.error('Failed to get app info:', error)
        }
      }
    }
    loadInfo()
  }, [])

  return appInfo
}
