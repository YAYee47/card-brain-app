import React, { useEffect, useState, useCallback, useRef } from 'react';
import {
  StyleSheet, Text, View, ScrollView, RefreshControl,
  TouchableOpacity, ActivityIndicator, Animated, SafeAreaView, Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { fetchDashboard, DashboardSummary, CardDashboard, BenefitUsage } from '../../src/api/dashboard';
import { checkBackendHealth } from '../../src/api/client';
import { getCached, setCached, clearAllCache, CACHE_KEYS } from '../../src/services/cache';
import TutorialOverlay from '../../src/components/TutorialOverlay';
import { useRouter, Tabs } from 'expo-router';

// ── 格式化工具 ──────────────────────────────────────────────────
const fmt = (n: number) =>
  `$${n.toLocaleString('zh-TW', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

const fmtPct = (n: number) => `${n.toFixed(0)}%`;

function barColor(pct: number): string {
  if (pct >= 100) return '#EF4444';
  if (pct >= 80) return '#F59E0B';
  return '#22C55E';
}

// ── 動態進度條元件 ──────────────────────────────────────────────
function AnimatedBar({ pct, color }: { pct: number; color: string }) {
  const anim = useRef(new Animated.Value(0)).current;
  useEffect(() => {
    Animated.timing(anim, {
      toValue: Math.min(pct, 100),
      duration: 700,
      useNativeDriver: false,
    }).start();
  }, [pct]);
  const width = anim.interpolate({ inputRange: [0, 100], outputRange: ['0%', '100%'] });
  return (
    <View style={styles.barBg}>
      <Animated.View style={[styles.barFill, { width, backgroundColor: color }]} />
    </View>
  );
}

// ── 單通道額度行 ──────────────────────────────────────────────
function BenefitRow({ b }: { b: BenefitUsage }) {
  if (b.monthly_cap_ntd === null) return null;  // 無上限的通道不顯示進度條
  const color = barColor(b.used_pct);
  return (
    <View style={styles.benefitRow}>
      <View style={styles.benefitHeader}>
        <Text style={styles.benefitName} numberOfLines={1}>{b.channel_name}</Text>
        <View style={styles.benefitRates}>
          <Text style={styles.rateBase}>{b.base_rate}%</Text>
          {b.bonus_rate > 0 && <Text style={styles.rateBonus}>+{b.bonus_rate}%</Text>}
        </View>
      </View>
      <AnimatedBar pct={b.used_pct} color={color} />
      <View style={styles.benefitMeta}>
        <Text style={[styles.metaPct, { color }]}>{fmtPct(b.used_pct)}</Text>
        <Text style={styles.metaValues}>
          {fmt(b.used_amount_ntd)} / {fmt(b.monthly_cap_ntd)}
          {b.remaining_cap_ntd !== null && b.remaining_cap_ntd > 0
            ? ` · 剩 ${fmt(b.remaining_cap_ntd)}`
            : b.is_capped ? ' · 已封頂' : ''}
        </Text>
      </View>
      {b.is_warning && !b.is_capped && (
        <View style={styles.warningBadge}>
          <Text style={styles.warningText}>⚠ 額度即將達上限，建議換卡消費</Text>
        </View>
      )}
      {b.is_capped && (
        <View style={styles.cappedBadge}>
          <Text style={styles.cappedText}>🔴 加碼額度已滿，改用基礎回饋 {b.base_rate}%</Text>
        </View>
      )}
    </View>
  );
}

// ── 卡片區塊 ──────────────────────────────────────────────────
function CardBlock({ card }: { card: CardDashboard }) {
  const [expanded, setExpanded] = useState(true);
  const cappedChannels = card.benefits.filter(b => b.is_capped).length;
  const warningChannels = card.benefits.filter(b => b.is_warning && !b.is_capped).length;

  return (
    <View style={[
      styles.cardBlock,
      cappedChannels > 0 && styles.cardBlockCapped,
      warningChannels > 0 && !cappedChannels && styles.cardBlockWarning,
    ]}>
      <TouchableOpacity style={styles.cardBlockHeader} onPress={() => setExpanded(e => !e)}>
        
        <View style={{ flex: 1 }}>
          <View style={styles.cardTitleRow}>
            <Text style={styles.cardName}>{card.card_name}</Text>
            {cappedChannels > 0 && <View style={styles.pillRed}><Text style={styles.pillText}>封頂</Text></View>}
            {warningChannels > 0 && !cappedChannels && <View style={styles.pillAmber}><Text style={styles.pillText}>警示</Text></View>}
          </View>
          <Text style={styles.cardBank}>{card.bank_name} · 結帳日每月 {card.billing_cycle_date} 號</Text>
          <Text style={styles.cardCycle}>週期 {card.cycle_start_date} ~ {card.cycle_end_date}</Text>
        </View>
        <Text style={styles.chevron}>{expanded ? '▾' : '▸'}</Text>
      </TouchableOpacity>

      {/* 卡片摘要數字 */}
      <View style={styles.cardSummaryRow}>
        <View style={styles.summaryBox}>
          <Text style={styles.summaryLabel}>本期消費</Text>
          <Text style={styles.summaryValue}>{fmt(card.total_used_ntd)}</Text>
        </View>
        <View style={[styles.summaryBox, styles.summaryBoxHighlight]}>
          <Text style={styles.summaryLabel}>已賺回饋</Text>
          <Text style={[styles.summaryValue, styles.summaryHighlight]}>+{fmt(card.total_cashback_ntd)}</Text>
        </View>
      </View>

      {/* 展開：各通道進度條 */}
      {expanded && (
        <View style={styles.benefitList}>
          {card.benefits.filter(b => b.monthly_cap_ntd !== null && !b.channel_name.includes('新戶') && !b.channel_name.includes('舊戶') && !b.channel_name.includes('新申辦')).map((b, i) => (
            <BenefitRow key={i} b={b} />
          ))}
          {card.benefits.every(b => b.monthly_cap_ntd === null) && (
            <Text style={styles.noCapText}>此卡所有通道均無加碼上限</Text>
          )}
        </View>
      )}
    </View>
  );
}

// ── 主頁面 ──────────────────────────────────────────────────────
export default function DashboardScreen() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [cacheTime, setCacheTime] = useState<string | null>(null);
  const router = useRouter();

  const load = useCallback(async (forceRefresh = false) => {
    // 嘗試從快取讀取（離線優先）
    if (!forceRefresh) {
      const cached = await getCached<DashboardSummary>(CACHE_KEYS.DASHBOARD, 10 * 60 * 1000);
      if (cached) {
        setData(cached);
        setCacheTime(new Date(cached.last_updated).toLocaleTimeString('zh-TW'));
        setLoading(false);
        setIsOffline(false);
        // 背景靜默更新
        fetchDashboard()
          .then(async fresh => {
            setData(fresh);
            setCacheTime(new Date(fresh.last_updated).toLocaleTimeString('zh-TW'));
            await setCached(CACHE_KEYS.DASHBOARD, fresh);
            setIsOffline(false);
          })
          .catch(() => setIsOffline(true));
        return;
      }
    }

    // 無快取時：直接連線
    try {
      const fresh = await fetchDashboard();
      setData(fresh);
      setCacheTime(new Date(fresh.last_updated).toLocaleTimeString('zh-TW'));
      await setCached(CACHE_KEYS.DASHBOARD, fresh);
      setIsOffline(false);
    } catch {
      // 連線失敗：再嘗試讀舊快取（不限 TTL）
      const stale = await getCached<DashboardSummary>(CACHE_KEYS.DASHBOARD, Infinity);
      if (stale) {
        setData(stale);
        setCacheTime(new Date(stale.last_updated).toLocaleTimeString('zh-TW'));
      }
      setIsOffline(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await clearAllCache();
    await load(true);
    setRefreshing(false);
  }, [load]);

  useEffect(() => { load(); }, [load]);

  return (
    <SafeAreaView style={styles.container}>
      <Tabs.Screen
        options={{
          headerLeft: () => (
            <TouchableOpacity onPress={onRefresh} style={{ marginLeft: 16, padding: 4 }}>
              <Ionicons name="refresh" size={24} color="#DB2777" />
            </TouchableOpacity>
          ),
          headerRight: () => {
            const handleLogout = async () => {
              Alert.alert('確認', '確定要登出並切換身分嗎？如果是試用模式，資料將會永久刪除！', [
                { text: '取消', style: 'cancel' },
                { 
                  text: '確定登出', 
                  style: 'destructive',
                  onPress: async () => {
                    try {
                      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
                      const { apiClient } = require('../../src/api/client');
                      const isGuest = await AsyncStorage.getItem('is_guest');
                      if (isGuest === 'true') {
                        await apiClient.delete('/users/me');
                      }
                      await AsyncStorage.clear();
                      router.replace('/welcome');
                    } catch (e) {
                      console.error('登出失敗:', e);
                      const AsyncStorage = require('@react-native-async-storage/async-storage').default;
                      await AsyncStorage.clear();
                      router.replace('/welcome');
                    }
                  }
                }
              ]);
            };
            return (
              <TouchableOpacity onPress={handleLogout} style={{ marginRight: 16, padding: 4 }}>
                <Ionicons name="log-out-outline" size={24} color="#DB2777" />
              </TouchableOpacity>
            );
          }
        }}
      />
      {/* 新手教學遮罩 - 首次打開自動顯示 */}
      <TutorialOverlay show={!loading && !!data && data.cards_count > 0} />

      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#DB2777" />}
        showsVerticalScrollIndicator={false}
      >
        {/* 離線 Banner */}
        {isOffline && (
          <View style={styles.offlineBanner}>
            <Text style={styles.offlineText}>📡 離線模式 — 顯示最後同步資料</Text>
            <TouchableOpacity onPress={onRefresh}>
              <Text style={styles.offlineRetry}>重試</Text>
            </TouchableOpacity>
          </View>
        )}

        {loading && !data ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="large" color="#DB2777" />
            <Text style={styles.loadingText}>同步最新資料中...</Text>
          </View>
        ) : !data || data.cards_count === 0 ? (
          <EmptyState />
        ) : (
          <>
            {/* 全域狀態區與標題 */}
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <Text style={[styles.sectionTitle, { marginBottom: 0, fontSize: 13, fontWeight: '700', color: '#BE185D' }]}>各卡片加碼額度水位</Text>
              <Text style={{ fontSize: 10, color: '#9CA3AF' }}>資料更新時間: {cacheTime ?? '--'}</Text>
            </View>

            {/* 卡片列表 */}
            {data.cards.map(card => (
              <CardBlock key={card.user_card_id} card={card} />
            ))}

            <Text style={styles.tip}>↑ 下拉可強制重新同步最新數據</Text>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function EmptyState() {
  return (
    <View style={styles.emptyBox}>
      <Text style={styles.emptyIcon}>💳</Text>
      <Text style={styles.emptyTitle}>尚未設定持有卡片</Text>
      <Text style={styles.emptyHint}>請前往底部「名下卡片」頁面，完成初始信用卡設定後即可開始追蹤回饋！</Text>
    </View>
  );
}

// ── Styles ────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  content: { padding: 16, paddingBottom: 40 },

  offlineBanner: {
    backgroundColor: '#FEF3C7', borderRadius: 10, padding: 10,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12,
  },
  offlineText: { color: '#B45309', fontSize: 13 },
  offlineRetry: { color: '#D97706', fontSize: 13, fontWeight: '700' },

  loadingBox: { paddingTop: 80, alignItems: 'center' },
  loadingText: { color: '#9D174D', marginTop: 14, fontSize: 14 },

  // Hero 卡片
  heroCard: {
    borderRadius: 20, padding: 24, marginBottom: 20,
    backgroundColor: '#831843', // 深粉紅/酒紅
    borderWidth: 1, borderColor: '#BE185D',
    shadowColor: '#BE185D', shadowOpacity: 0.25, shadowRadius: 16, elevation: 8,
  },
  heroLabel: { color: '#FBCFE8', fontSize: 13, marginBottom: 4 },
  heroAmount: { color: '#FFFFFF', fontSize: 42, fontWeight: '800', letterSpacing: -1, marginBottom: 2 },
  heroSub: { color: '#F9A8D4', fontSize: 13, marginBottom: 16, opacity: 0.8 },
  heroStats: { flexDirection: 'row', backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 12, padding: 12 },
  heroStat: { flex: 1, alignItems: 'center' },
  heroStatLabel: { color: '#FBCFE8', fontSize: 11, marginBottom: 4 },
  heroStatValue: { color: '#FFFFFF', fontSize: 14, fontWeight: '700' },
  heroStatDivider: { width: 1, backgroundColor: '#BE185D', marginHorizontal: 8 },

  // 快捷操作
  quickActions: { flexDirection: 'row', gap: 12, marginBottom: 20 },
  actionBtn: { 
    flex: 1, backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, 
    flexDirection: 'row', alignItems: 'center', gap: 12,
    borderWidth: 1, borderColor: '#FBCFE8',
    shadowColor: '#F9A8D4', shadowOpacity: 0.15, shadowRadius: 8, elevation: 3
  },
  actionIconBg: { backgroundColor: '#FCE7F3', width: 40, height: 40, borderRadius: 20, alignItems: 'center', justifyContent: 'center' },
  actionIcon: { fontSize: 20 },
  actionText: { color: '#831843', fontSize: 15, fontWeight: '700' },

  sectionTitle: {
    color: '#9D174D', fontSize: 11, fontWeight: '700',
    textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 10,
  },

  // 卡片區塊
  cardBlock: {
    backgroundColor: '#FFFFFF', borderRadius: 16, marginBottom: 14,
    borderWidth: 1, borderColor: '#FBCFE8', overflow: 'hidden',
    shadowColor: '#F9A8D4', shadowOpacity: 0.15, shadowRadius: 8, elevation: 3
  },
  cardBlockWarning: { borderColor: '#FBBF24', borderWidth: 2 },
  cardBlockCapped: { borderColor: '#F87171', borderWidth: 2 },

  cardBlockHeader: { flexDirection: 'row', alignItems: 'center', padding: 14, gap: 10 },
  cardIcon: { fontSize: 28 },
  cardTitleRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 2 },
  cardName: { color: '#831843', fontSize: 16, fontWeight: 'bold' },
  cardBank: { color: '#9D174D', fontSize: 12 },
  cardCycle: { color: '#BE185D', fontSize: 11, marginTop: 2 },
  chevron: { color: '#9D174D', fontSize: 18 },

  pillRed: { backgroundColor: '#FEF2F2', borderRadius: 4, paddingHorizontal: 6, paddingVertical: 2, borderWidth: 1, borderColor: '#FECACA' },
  pillAmber: { backgroundColor: '#FFFBEB', borderRadius: 4, paddingHorizontal: 6, paddingVertical: 2, borderWidth: 1, borderColor: '#FDE68A' },
  pillText: { color: '#DC2626', fontSize: 10, fontWeight: '700' },

  cardSummaryRow: { flexDirection: 'row', paddingHorizontal: 14, paddingBottom: 12, gap: 8 },
  summaryBox: { flex: 1, backgroundColor: '#FFF0F5', borderRadius: 10, padding: 10, alignItems: 'center', borderWidth: 1, borderColor: '#FCE7F3' },
  summaryBoxHighlight: { backgroundColor: '#FCE7F3', borderColor: '#FBCFE8' },
  summaryLabel: { color: '#9D174D', fontSize: 11, marginBottom: 3 },
  summaryValue: { color: '#831843', fontSize: 16, fontWeight: '800' },
  summaryHighlight: { color: '#DB2777' },

  benefitList: { paddingHorizontal: 14, paddingBottom: 14 },

  // 通道進度條
  benefitRow: { marginBottom: 14 },
  benefitHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  benefitName: { color: '#831843', fontSize: 12, flex: 1, marginRight: 8, fontWeight: '600' },
  benefitRates: { flexDirection: 'row', gap: 4 },
  rateBase: { color: '#9D174D', fontSize: 11 },
  rateBonus: { color: '#DB2777', fontSize: 11, fontWeight: '800' },

  barBg: { height: 7, backgroundColor: '#FCE7F3', borderRadius: 4, overflow: 'hidden', marginBottom: 4 },
  barFill: { height: 7, borderRadius: 4 },

  benefitMeta: { flexDirection: 'row', justifyContent: 'space-between' },
  metaPct: { fontSize: 11, fontWeight: '800' },
  metaValues: { fontSize: 11, color: '#9D174D', fontWeight: '500' },

  warningBadge: { backgroundColor: '#FFFBEB', borderRadius: 6, padding: 6, marginTop: 4, borderWidth: 1, borderColor: '#FEF3C7' },
  warningText: { color: '#D97706', fontSize: 11, fontWeight: '600' },
  cappedBadge: { backgroundColor: '#FEF2F2', borderRadius: 6, padding: 6, marginTop: 4, borderWidth: 1, borderColor: '#FEE2E2' },
  cappedText: { color: '#DC2626', fontSize: 11, fontWeight: '600' },

  noCapText: { color: '#059669', fontSize: 12, textAlign: 'center', paddingVertical: 8, fontWeight: '600' },

  tip: { color: '#9D174D', fontSize: 12, textAlign: 'center', marginTop: 8 },

  // 空狀態
  emptyBox: { paddingTop: 80, alignItems: 'center', paddingHorizontal: 24 },
  emptyIcon: { fontSize: 64, marginBottom: 16 },
  emptyTitle: { color: '#831843', fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  emptyHint: { color: '#9D174D', fontSize: 14, textAlign: 'center', lineHeight: 22 },
});
