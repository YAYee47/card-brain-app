import React, { useEffect, useState, useCallback } from 'react';
import {
  StyleSheet, Text, View, ScrollView, TouchableOpacity,
  TextInput, ActivityIndicator, SafeAreaView, KeyboardAvoidingView,
  Platform, Keyboard
} from 'react-native';
import { fetchChannels, fetchRecommendations, RecommendedCard, RecommendResponse } from '../../src/api/recommend';

// 格式化金額為台幣顯示
const formatNTD = (amount: number) =>
  `$${amount.toLocaleString('zh-TW', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

// 加碼使用率進度條
function CapBar({ used, cap }: { used: number; cap: number | null }) {
  if (cap === null) return <Text style={styles.capUnlimited}>無上限</Text>;
  const pct = Math.min((used / cap) * 100, 100);
  const barColor = pct >= 100 ? '#EF4444' : pct >= 80 ? '#F59E0B' : '#22C55E';
  return (
    <View style={styles.capBarWrap}>
      <View style={styles.capBarBg}>
        <View style={[styles.capBarFill, { width: `${pct}%` as any, backgroundColor: barColor }]} />
      </View>
      <Text style={[styles.capBarText, { color: barColor }]}>
        {formatNTD(used)} / {formatNTD(cap)} ({pct.toFixed(0)}%)
      </Text>
    </View>
  );
}

export default function RecommendScreen() {
  const [channels, setChannels] = useState<string[]>([]);
  const [selectedChannel, setSelectedChannel] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [result, setResult] = useState<RecommendResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingChannels, setLoadingChannels] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchChannels()
      .then((chs) => {
        setChannels(chs);
        setSelectedChannel('');
      })
      .catch(() => setError('無法載入通道清單，請確認後端已啟動。'))
      .finally(() => setLoadingChannels(false));
  }, []);

  const handleRecommend = useCallback(async () => {
    let num = parseFloat(amount.replace(/,/g, ''));
    if (isNaN(num) || num <= 0) {
      num = 1000; // Default to 1000 for rate comparison if no amount provided
    }
    if (!selectedChannel) {
      setError('請選擇支付通道。');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const resp = await fetchRecommendations(num, selectedChannel);
      setResult(resp);
    } catch {
      setError('推薦試算失敗，請確認後端 API 連線正常。');
    } finally {
      setLoading(false);
    }
  }, [amount, selectedChannel]);

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">

          {/* 金額輸入區 */}
          <View style={styles.card}>
            <Text style={styles.sectionLabel}>消費金額 (台幣)</Text>
            <View style={styles.amountRow}>
              <Text style={styles.currency}>NT$</Text>
              <TextInput
                style={styles.amountInput as any}
                value={amount}
                onChangeText={setAmount}
                keyboardType="numeric"
                placeholder="例如：3000"
                placeholderTextColor="#F472B6"
                returnKeyType="done"
              />
            </View>
          </View>

          {/* 支付通道 / 情境 */}
          <View style={styles.card}>
            <Text style={styles.sectionLabel}>支付通道 / 情境</Text>
            <View style={styles.channelInputContainer}>
              <TextInput
                style={styles.channelInput as any}
                value={selectedChannel}
                onChangeText={setSelectedChannel}
                placeholder="輸入如：國內一般、國外消費、蝦皮、淘寶"
                placeholderTextColor="#94a3b8"
              />
            </View>
            {loadingChannels ? (
              <ActivityIndicator color="#F472B6" style={{ marginTop: 8 }} />
            ) : (
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipRow}>
                {channels.filter(c => ['國內一般消費', '國外消費', '行動支付 (Apple Pay/Google Pay)', 'LINE Pay', '網購 (momo/PChome等)'].includes(c)).map((ch) => (
                  <TouchableOpacity
                    key={ch}
                    style={[styles.channelChip, selectedChannel === ch && styles.channelChipActive]}
                    onPress={() => setSelectedChannel(ch)}
                  >
                    <Text style={[styles.channelChipText, selectedChannel === ch && styles.channelChipTextActive]} numberOfLines={1}>
                      {ch}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}
          </View>

          {/* 試算按鈕 */}
          {error && <Text style={styles.errorText}>{error}</Text>}
          <View style={{ flexDirection: 'row', gap: 12, marginBottom: 12 }}>
            <TouchableOpacity
              style={[styles.calcBtn, { flex: 1, backgroundColor: '#9CA3AF', elevation: 0, shadowOpacity: 0, shadowRadius: 0 }]}
              onPress={() => {
                setAmount('');
                setSelectedChannel('');
                setResult(null);
                setError(null);
              }}
            >
              <Text style={[styles.calcBtnText, { color: '#FFFFFF' }]}>清空</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.calcBtn, { flex: 2 }, loading && { opacity: 0.6 }]}
              onPress={() => {
                Keyboard.dismiss();
                handleRecommend();
              }}
              disabled={loading}
            >
              {loading
                ? <ActivityIndicator color="#fff" />
                : <Text style={styles.calcBtnText}>秒速推薦最佳卡片</Text>
              }
            </TouchableOpacity>
          </View>

          {/* 推薦結果 */}
          {result && result.results.length === 0 && (
            <View style={styles.emptyBox}>
              <Text style={styles.emptyText}>
                尚未設定持有的信用卡，請先至「名下卡片」頁面新增。
              </Text>
            </View>
          )}

          {result && (() => {
            let currentRank = 1;
            let prevAmount = -1;
            const ranked = result.results.map((card, idx) => {
              if (prevAmount !== -1 && card.estimated_total_cashback < prevAmount) {
                currentRank = idx + 1;
              }
              prevAmount = card.estimated_total_cashback;
              return { card, rank: currentRank };
            });
            
            const rankCounts: Record<number, number> = {};
            ranked.forEach(r => {
                rankCounts[r.rank] = (rankCounts[r.rank] || 0) + 1;
            });
            
            return ranked.map(({ card, rank }, i) => (
              <CardResultRow 
                key={`${card.user_card_id}-${i}`} 
                card={card} 
                rank={rank} 
                isTied={rankCounts[rank] > 1}
                amount={result.amount} 
              />
            ));
          })()}

        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

function CardResultRow({ card, rank, amount, isTied }: { card: RecommendedCard; rank: number; amount: number; isTied?: boolean }) {
  const isTop = rank === 1 && !card.is_capped;

  return (
    <View style={[styles.resultCard, isTop && styles.resultCardTop, card.is_capped && styles.resultCardCapped]}>
      {/* 排名標籤 */}
      <View style={styles.rankRow}>
        <View style={[styles.rankBadge, isTop && styles.rankBadgeTop]}>
          <Text style={styles.rankBadgeText}>#{rank}</Text>
        </View>
        {isTop ? (
          <Text style={styles.bestLabel}>
            {isTied ? '並列第一' : '最佳推薦'}
          </Text>
        ) : isTied && !card.is_capped ? (
          <Text style={[styles.bestLabel, { backgroundColor: '#F59E0B' }]}>
            並列第{rank}
          </Text>
        ) : null}
        {card.is_capped && <Text style={styles.cappedLabel}>加碼已滿</Text>}
      </View>

      {/* 卡片基本資訊 */}
      <View style={styles.cardIdentity}>
        <View>
          <Text style={styles.cardName}>{card.card_name}</Text>
          <Text style={styles.bankName}>{card.bank_name}</Text>
          <Text style={styles.channelTag}>{card.channel_name}</Text>
        </View>
      </View>

      {/* 回饋率 */}
      <View style={styles.rateRow}>
        <View style={styles.rateBox}>
          <Text style={styles.rateLabel}>基礎回饋</Text>
          <Text style={styles.rateValue}>{card.base_rate}%</Text>
        </View>
        <Text style={styles.ratePlus}>+</Text>
        <View style={styles.rateBox}>
          <Text style={styles.rateLabel}>加碼回饋</Text>
          <Text style={[styles.rateValue, { color: '#F472B6' }]}>{card.bonus_rate}%</Text>
        </View>
      </View>

      {/* 加碼額度進度條 */}
      <Text style={styles.capLabel}>帳單週期加碼額度使用量</Text>
      <CapBar used={card.used_amount_ntd} cap={card.monthly_cap_ntd} />

      {/* 本次消費預估回饋 */}
      <View style={styles.cashbackRow}>
        <View style={styles.cashbackBox}>
          <Text style={styles.cashbackLabel}>基礎回饋</Text>
          <Text style={styles.cashbackValue}>+{formatNTD(card.estimated_base_cashback)}</Text>
        </View>
        <View style={styles.cashbackBox}>
          <Text style={styles.cashbackLabel}>加碼回饋</Text>
          <Text style={[styles.cashbackValue, { color: '#F472B6' }]}>
            +{formatNTD(card.estimated_bonus_cashback)}
          </Text>
        </View>
        <View style={[styles.cashbackBox, styles.totalBox]}>
          <Text style={styles.cashbackLabel}>總回饋</Text>
          <Text style={styles.totalValue}>+{formatNTD(card.estimated_total_cashback)}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  content: { padding: 16, paddingBottom: 48 },

  // 輸入卡片
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 20, marginBottom: 16, borderWidth: 1, borderColor: '#FCE7F3', shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  sectionLabel: { color: '#BE185D', fontSize: 13, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 12 },
  amountRow: { flexDirection: 'row', alignItems: 'center' },
  currency: { color: '#9D174D', fontSize: 24, fontWeight: 'bold', marginRight: 12 },
  amountInput: { flex: 1, color: '#831843', fontSize: 28, fontWeight: 'bold', outlineStyle: 'none' },

  // 通道選擇
  channelInput: { backgroundColor: '#FFF5F8', color: '#831843', fontSize: 16, fontWeight: 'bold', padding: 14, borderRadius: 16, borderWidth: 1, borderColor: '#FBCFE8', marginBottom: 12, outlineStyle: 'none' },
  channelList: { paddingVertical: 4, gap: 10, flexDirection: 'row' },
  channelChip: { backgroundColor: '#FFF5F8', borderRadius: 20, paddingHorizontal: 16, paddingVertical: 8, borderWidth: 1, borderColor: '#FBCFE8' },
  channelChipActive: { backgroundColor: '#EC4899', borderColor: '#EC4899', shadowColor: '#EC4899', shadowOpacity: 0.3, shadowRadius: 6, elevation: 3 },
  channelChipText: { color: '#BE185D', fontSize: 14, fontWeight: '500' },
  channelChipTextActive: { color: '#FFFFFF', fontWeight: '700' },

  // 按鈕
  calcBtn: { backgroundColor: '#DB2777', borderRadius: 16, paddingVertical: 18, alignItems: 'center', marginBottom: 24, shadowColor: '#DB2777', shadowOpacity: 0.4, shadowRadius: 14, elevation: 8 },
  calcBtnText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  errorText: { color: '#E11D48', fontSize: 14, textAlign: 'center', marginBottom: 12 },
  emptyBox: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 30, alignItems: 'center', borderWidth: 1, borderColor: '#FCE7F3' },
  emptyText: { color: '#BE185D', fontSize: 15, textAlign: 'center', lineHeight: 24 },

  // 結果卡片
  resultCard: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 20, marginBottom: 16, borderWidth: 1, borderColor: '#FCE7F3', shadowColor: '#FDA4AF', shadowOpacity: 0.15, shadowRadius: 8, elevation: 2 },
  resultCardTop: { borderColor: '#EC4899', borderWidth: 2, shadowColor: '#EC4899', shadowOpacity: 0.3, shadowRadius: 14, elevation: 6 },
  resultCardCapped: { opacity: 0.6, borderColor: '#FBCFE8' },

  rankRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  rankBadge: { backgroundColor: '#FCE7F3', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4, marginRight: 8, borderWidth: 1, borderColor: '#FBCFE8' },
  rankBadgeTop: { backgroundColor: '#EC4899', borderColor: '#EC4899' },
  rankBadgeText: { color: '#9D174D', fontSize: 13, fontWeight: '800' },
  bestLabel: { color: '#FFFFFF', fontSize: 12, fontWeight: '800', backgroundColor: '#DB2777', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8, overflow: 'hidden' },
  cappedLabel: { color: '#FFFFFF', fontSize: 12, fontWeight: '700', backgroundColor: '#E11D48', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6, overflow: 'hidden' },

  cardIdentity: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 16, gap: 12 },
  cardName: { color: '#831843', fontSize: 20, fontWeight: '900' },
  bankName: { color: '#BE185D', fontSize: 14, marginTop: 4, fontWeight: '500' },
  channelTag: { color: '#DB2777', fontSize: 14, marginTop: 6, fontWeight: '700' },

  rateRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFF5F8', borderRadius: 12, padding: 14, marginBottom: 16, borderWidth: 1, borderColor: '#FCE7F3' },
  rateBox: { flex: 1, alignItems: 'center' },
  rateLabel: { color: '#9D174D', fontSize: 12, marginBottom: 4, fontWeight: '600' },
  rateValue: { color: '#831843', fontSize: 24, fontWeight: '900' },
  ratePlus: { color: '#F472B6', fontSize: 20, marginHorizontal: 12, fontWeight: 'bold' },

  capLabel: { color: '#9D174D', fontSize: 12, marginBottom: 8, fontWeight: '600' },
  capBarWrap: { marginBottom: 20 },
  capBarBg: { height: 8, backgroundColor: '#FCE7F3', borderRadius: 4, overflow: 'hidden', marginBottom: 6 },
  capBarFill: { height: 8, borderRadius: 4 },
  capBarText: { fontSize: 12, fontWeight: '500' },
  capUnlimited: { color: '#059669', fontSize: 13, marginBottom: 16, fontWeight: '700' },

  cashbackRow: { flexDirection: 'row', gap: 10 },
  cashbackBox: { flex: 1, backgroundColor: '#FFF5F8', borderRadius: 12, padding: 12, alignItems: 'center', borderWidth: 1, borderColor: '#FCE7F3' },
  totalBox: { backgroundColor: '#FDF2F8', borderColor: '#FBCFE8', borderWidth: 2 },
  cashbackLabel: { color: '#BE185D', fontSize: 11, marginBottom: 6, fontWeight: '600' },
  cashbackValue: { color: '#831843', fontSize: 16, fontWeight: '800' },
  totalValue: { color: '#DB2777', fontSize: 18, fontWeight: '900' },
});
