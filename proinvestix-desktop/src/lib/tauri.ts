// ============================================================================
// ProInvestiX Enterprise Desktop - Tauri Hooks
// ============================================================================

import { invoke } from '@tauri-apps/api/core'
import { sendNotification } from '@tauri-apps/plugin-notification'
import { open, save, message, confirm } from '@tauri-apps/plugin-dialog'
import { check } from '@tauri-apps/plugin-updater'
import { relaunch } from '@tauri-apps/plugin-process'

// =============================================================================
// APP INFO
// =============================================================================

export async function getAppVersion(): Promise<string> {
  return await invoke('get_version')
}

export async function getPlatform(): Promise<string> {
  return await invoke('get_platform')
}

export async function getAppDataDir(): Promise<string> {
  return await invoke('get_app_data_dir')
}

// =============================================================================
// NOTIFICATIONS
// =============================================================================

export async function showNotification(title: string, body: string): Promise<void> {
  await sendNotification({ title, body })
}

export async function showSuccessNotification(message: string): Promise<void> {
  await showNotification('ProInvestiX', `✅ ${message}`)
}

export async function showErrorNotification(message: string): Promise<void> {
  await showNotification('ProInvestiX', `❌ ${message}`)
}

// =============================================================================
// DIALOGS
// =============================================================================

export async function showMessage(title: string, message: string): Promise<void> {
  await message(message, { title, kind: 'info' })
}

export async function showError(title: string, message: string): Promise<void> {
  await message(message, { title, kind: 'error' })
}

export async function showConfirm(title: string, message: string): Promise<boolean> {
  return await confirm(message, { title, kind: 'warning' })
}

export async function openFileDialog(filters?: { name: string; extensions: string[] }[]): Promise<string | null> {
  const result = await open({
    multiple: false,
    filters,
  })
  return result as string | null
}

export async function saveFileDialog(defaultPath?: string, filters?: { name: string; extensions: string[] }[]): Promise<string | null> {
  const result = await save({
    defaultPath,
    filters,
  })
  return result as string | null
}

// =============================================================================
// SETTINGS
// =============================================================================

export async function storeSetting(key: string, value: string): Promise<void> {
  await invoke('store_setting', { key, value })
}

export async function getSetting(key: string): Promise<string | null> {
  return await invoke('get_setting', { key })
}

// =============================================================================
// UPDATES
// =============================================================================

export async function checkForUpdates(): Promise<{
  available: boolean
  version?: string
  notes?: string
}> {
  try {
    const update = await check()
    if (update) {
      return {
        available: true,
        version: update.version,
        notes: update.body || undefined,
      }
    }
    return { available: false }
  } catch (error) {
    console.error('Update check failed:', error)
    return { available: false }
  }
}

export async function installUpdate(): Promise<void> {
  const update = await check()
  if (update) {
    await update.downloadAndInstall()
    await relaunch()
  }
}

// =============================================================================
// UTILITY
// =============================================================================

export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI__' in window
}

export async function exitApp(): Promise<void> {
  if (isTauri()) {
    const { exit } = await import('@tauri-apps/plugin-process')
    await exit(0)
  }
}
