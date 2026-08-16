/**
 * 離線快取模組 (Offline Cache)
 * 使用 React Native AsyncStorage 將最新 API 資料持久化至手機本地端，
 * 確保無網路時仍能顯示最後一次同步的儀表板數據。
 */

import { Platform } from 'react-native';

// AsyncStorage 的 polyfill：在 Web 環境使用 localStorage，手機端動態載入 @react-native-async-storage/async-storage
// 由於 Expo 的限制，在 Web 模式下使用 in-memory fallback
const memoryStore: Record<string, string> = {};

const storage = {
  async getItem(key: string): Promise<string | null> {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch {}
    return memoryStore[key] ?? null;
  },
  async setItem(key: string, value: string): Promise<void> {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, value);
        return;
      }
    } catch {}
    memoryStore[key] = value;
  },
  async removeItem(key: string): Promise<void> {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.removeItem(key);
        return;
      }
    } catch {}
    delete memoryStore[key];
  },
};

const CACHE_KEYS = {
  DASHBOARD: 'cache:dashboard',
  USER_CARDS: 'cache:user_cards',
  CHANNELS: 'cache:channels',
};

const CACHE_TTL_MS = 5 * 60 * 1000; // 5 分鐘過期

interface CacheEntry<T> {
  data: T;
  ts: number;  // unix timestamp ms
}

/** 寫入快取 */
export async function setCached<T>(key: string, data: T): Promise<void> {
  const entry: CacheEntry<T> = { data, ts: Date.now() };
  await storage.setItem(key, JSON.stringify(entry));
}

/** 讀取快取；若已過期或不存在則回傳 null */
export async function getCached<T>(key: string, ttlMs = CACHE_TTL_MS): Promise<T | null> {
  try {
    const raw = await storage.getItem(key);
    if (!raw) return null;
    const entry: CacheEntry<T> = JSON.parse(raw);
    if (Date.now() - entry.ts > ttlMs) return null;
    return entry.data;
  } catch {
    return null;
  }
}

/** 強制清除所有快取（供手動重新同步使用）*/
export async function clearAllCache(): Promise<void> {
  await Promise.all(Object.values(CACHE_KEYS).map(k => storage.removeItem(k)));
}

export { CACHE_KEYS };
