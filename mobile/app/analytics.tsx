import React, { useState, useEffect, useMemo } from 'react';
import {
  StyleSheet, Text, View, SafeAreaView, TouchableOpacity,
  ScrollView, ActivityIndicator, Dimensions, LayoutAnimation, UIManager, Platform, Modal
} from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { PieChart } from 'react-native-chart-kit';
import { fetchTransactions, TransactionOut } from '../src/api/transactions';
import { Ionicons } from '@expo/vector-icons';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const screenWidth = Dimensions.get('window').width;

const CATEGORY_COLORS: Record<string, string> = {
  '餐飲': '#F472B6', // Pink
  '購物': '#38BDF8', // Sky
  '交通': '#34D399', // Emerald
  '數位網購': '#A78BFA', // Purple
  '娛樂': '#FBBF24', // Amber
  '固定支出': '#F87171', // Red
  '其他': '#9CA3AF', // Gray
};

export default function AnalyticsScreen() {
  const router = useRouter();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [txns, setTxns] = useState<TransactionOut[]>([]);
  const [expandedCat, setExpandedCat] = useState<string | null>(null);

  const loadData = async (date: Date) => {
    setLoading(true);
    try {
      const year = date.getFullYear();
      const month = date.getMonth();
      const startDate = new Date(year, month, 1, 0, 0, 0).toISOString();
      const endDate = new Date(year, month + 1, 0, 23, 59, 59).toISOString();
      
      const res = await fetchTransactions(undefined, startDate, endDate);
      setTxns(res);
    } catch (error) {
      console.error('Failed to fetch analytics txns', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(currentDate);
  }, [currentDate]);

  const handlePrevMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
    setExpandedCat(null);
  };

  const handleNextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
    setExpandedCat(null);
  };

  const toggleCategory = (cat: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedCat(prev => prev === cat ? null : cat);
  };

  const [showMonthPicker, setShowMonthPicker] = useState(false);
  const [pickerYear, setPickerYear] = useState(currentDate.getFullYear());

  const stats = useMemo(() => {
    const grouped: Record<string, { total: number; count: number; txns: TransactionOut[] }> = {};
    let totalSpent = 0;
    let totalCashback = 0;

    txns.forEach(t => {
      const cat = t.category || '其他';
      if (!grouped[cat]) grouped[cat] = { total: 0, count: 0, txns: [] };
      grouped[cat].total += t.ntd_amount;
      grouped[cat].count += 1;
      grouped[cat].txns.push(t);
      totalSpent += t.ntd_amount;
      totalCashback += t.earned_cashback_ntd;
    });

    const chartData = Object.keys(grouped).map(cat => ({
      name: cat,
      population: grouped[cat].total,
      color: CATEGORY_COLORS[cat] || CATEGORY_COLORS['其他'],
      legendFontColor: '#4B5563',
      legendFontSize: 13,
    })).sort((a, b) => b.population - a.population);

    const listData = Object.keys(grouped).map(cat => ({
      name: cat,
      ...grouped[cat],
      percent: totalSpent > 0 ? (grouped[cat].total / totalSpent) * 100 : 0
    })).sort((a, b) => b.total - a.total);

    return { totalSpent, totalCashback, chartData, listData };
  }, [txns]);

  const monthLabel = `${currentDate.getFullYear()}年${currentDate.getMonth() + 1}月`;

  return (
    <SafeAreaView style={styles.container}>
      <Stack.Screen options={{ title: '消費分析', headerBackTitle: '返回', headerStyle: { backgroundColor: '#FFF0F5' }, headerTintColor: '#831843' }} />
      
      {/* Month Navigator */}
      <View style={styles.navHeader}>
        <TouchableOpacity style={styles.navBtn} onPress={handlePrevMonth}>
          <Ionicons name="chevron-back" size={24} color="#BE185D" />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => { setPickerYear(currentDate.getFullYear()); setShowMonthPicker(true); }}>
          <View style={styles.monthPill}>
            <Text style={styles.navTitle}>{monthLabel}</Text>
            <Ionicons name="caret-down" size={16} color="#BE185D" style={{ marginLeft: 4 }} />
          </View>
        </TouchableOpacity>
        <TouchableOpacity style={styles.navBtn} onPress={handleNextMonth}>
          <Ionicons name="chevron-forward" size={24} color="#BE185D" />
        </TouchableOpacity>
      </View>

      <Modal visible={showMonthPicker} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.monthPickerBox}>
            <View style={styles.pickerYearRow}>
              <TouchableOpacity onPress={() => setPickerYear(y => y - 1)} style={{ padding: 10 }}>
                <Ionicons name="chevron-back" size={24} color="#BE185D" />
              </TouchableOpacity>
              <Text style={styles.pickerYearText}>{pickerYear} 年</Text>
              <TouchableOpacity onPress={() => setPickerYear(y => y + 1)} style={{ padding: 10 }}>
                <Ionicons name="chevron-forward" size={24} color="#BE185D" />
              </TouchableOpacity>
            </View>
            <View style={styles.monthsGrid}>
              {[...Array(12)].map((_, i) => {
                const isActive = currentDate.getFullYear() === pickerYear && currentDate.getMonth() === i;
                return (
                  <TouchableOpacity 
                    key={i} 
                    style={[styles.monthCell, isActive && styles.monthCellActive]}
                    onPress={() => {
                      setCurrentDate(new Date(pickerYear, i, 1));
                      setShowMonthPicker(false);
                      setExpandedCat(null);
                    }}
                  >
                    <Text style={[styles.monthCellText, isActive && styles.monthCellTextActive]}>
                      {i + 1}月
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
            <TouchableOpacity style={styles.modalCloseBtn} onPress={() => setShowMonthPicker(false)}>
              <Text style={styles.modalCloseBtnText}>取消</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#EC4899" />
          <Text style={{ marginTop: 10, color: '#9D174D' }}>載入資料中...</Text>
        </View>
      ) : (
        <ScrollView style={styles.content} contentContainerStyle={{ paddingBottom: 40 }}>
          {/* Summary Box */}
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>本月總支出</Text>
            <Text style={styles.summaryAmount}>${stats.totalSpent.toLocaleString()}</Text>
            <Text style={styles.summarySub}>預估獲得回饋: +${Math.round(stats.totalCashback).toLocaleString()}</Text>
          </View>

          {/* Chart */}
          {stats.chartData.length > 0 ? (
            <View style={styles.chartContainer}>
              <PieChart
                data={stats.chartData}
                width={screenWidth - 32}
                height={220}
                chartConfig={{
                  color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                }}
                accessor={"population"}
                backgroundColor={"transparent"}
                paddingLeft={"15"}
                center={[10, 0]}
                absolute
              />
            </View>
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>這個月還沒有記帳紀錄喔！</Text>
            </View>
          )}

          {/* Category List */}
          <View style={styles.listContainer}>
            {stats.listData.map((cat, idx) => {
              const isExpanded = expandedCat === cat.name;
              return (
                <View key={idx} style={styles.catCard}>
                  <TouchableOpacity style={styles.catHeader} onPress={() => toggleCategory(cat.name)}>
                    <View style={styles.catIconRow}>
                      <View style={[styles.colorDot, { backgroundColor: CATEGORY_COLORS[cat.name] || '#9CA3AF' }]} />
                      <View>
                        <Text style={styles.catName}>{cat.name}</Text>
                        <Text style={styles.catCount}>{cat.count} 筆消費</Text>
                      </View>
                    </View>
                    <View style={styles.catStatsRow}>
                      <View style={{ alignItems: 'flex-end' }}>
                        <Text style={styles.catAmount}>${cat.total.toLocaleString()}</Text>
                        <Text style={styles.catPercent}>{cat.percent.toFixed(1)}%</Text>
                      </View>
                      <Ionicons name={isExpanded ? "chevron-up" : "chevron-down"} size={20} color="#9CA3AF" style={{ marginLeft: 8 }} />
                    </View>
                  </TouchableOpacity>

                  {/* Expanded Txns */}
                  {isExpanded && (
                    <View style={styles.txnList}>
                      {cat.txns.map(t => (
                        <View key={t.id} style={styles.txnRow}>
                          <View style={styles.txnLeft}>
                            <Text style={styles.txnDate}>{new Date(t.transacted_at).getDate()}日</Text>
                            <View>
                              <Text style={styles.txnMerchant}>{t.merchant_name || t.channel_name}</Text>
                              <Text style={styles.txnChannel}>{t.channel_name}</Text>
                            </View>
                          </View>
                          <View style={styles.txnRight}>
                            <Text style={styles.txnAmt}>${t.ntd_amount.toLocaleString()}</Text>
                            {t.earned_cashback_ntd > 0 && (
                              <Text style={styles.txnCb}>+${Math.round(t.earned_cashback_ntd).toLocaleString()}</Text>
                            )}
                          </View>
                        </View>
                      ))}
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  navHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, backgroundColor: '#FFF',
    borderBottomWidth: 1, borderBottomColor: '#FCE7F3'
  },
  navBtn: { padding: 8, backgroundColor: '#FCE7F3', borderRadius: 8 },
  navTitle: { fontSize: 18, fontWeight: 'bold', color: '#831843' },
  content: { flex: 1, padding: 16 },
  summaryCard: {
    backgroundColor: '#9D174D', borderRadius: 16, padding: 20,
    alignItems: 'center', marginBottom: 16,
    shadowColor: '#9D174D', shadowOpacity: 0.3, shadowRadius: 10, elevation: 5,
  },
  summaryLabel: { color: '#FBCFE8', fontSize: 14, fontWeight: '600', marginBottom: 4 },
  summaryAmount: { color: '#FFF', fontSize: 36, fontWeight: 'bold', marginBottom: 8 },
  summarySub: { color: '#F9A8D4', fontSize: 14, fontWeight: '500' },
  chartContainer: {
    backgroundColor: '#FFF', borderRadius: 16, padding: 16, marginBottom: 16,
    alignItems: 'center',
    shadowColor: '#FDA4AF', shadowOpacity: 0.1, shadowRadius: 8, elevation: 2,
  },
  emptyState: {
    backgroundColor: '#FFF', borderRadius: 16, padding: 32, marginBottom: 16,
    alignItems: 'center', justifyContent: 'center',
  },
  emptyText: { color: '#9CA3AF', fontSize: 16 },
  listContainer: { gap: 12 },
  catCard: {
    backgroundColor: '#FFF', borderRadius: 16, overflow: 'hidden',
    shadowColor: '#FDA4AF', shadowOpacity: 0.1, shadowRadius: 8, elevation: 2,
  },
  catHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    padding: 16,
  },
  catIconRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  colorDot: { width: 16, height: 16, borderRadius: 8 },
  catName: { fontSize: 16, fontWeight: 'bold', color: '#4B5563', marginBottom: 2 },
  catCount: { fontSize: 12, color: '#9CA3AF' },
  catStatsRow: { flexDirection: 'row', alignItems: 'center' },
  catAmount: { fontSize: 16, fontWeight: 'bold', color: '#111827', marginBottom: 2 },
  catPercent: { fontSize: 13, color: '#6B7280' },
  
  txnList: {
    backgroundColor: '#F9FAFB', paddingHorizontal: 16, paddingBottom: 16,
    borderTopWidth: 1, borderTopColor: '#F3F4F6'
  },
  txnRow: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#E5E7EB'
  },
  txnLeft: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  txnDate: { fontSize: 14, color: '#9CA3AF', fontWeight: '600', width: 36 },
  txnMerchant: { fontSize: 15, color: '#374151', fontWeight: '500' },
  txnChannel: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  txnRight: { alignItems: 'flex-end' },
  txnAmt: { fontSize: 15, color: '#111827', fontWeight: '600' },
  txnCb: { fontSize: 12, color: '#059669', fontWeight: '600', marginTop: 2 },
  
  modalOverlay: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'center', alignItems: 'center'
  },
  monthPickerBox: {
    backgroundColor: '#fff', width: 300, borderRadius: 20, padding: 20, alignItems: 'center'
  },
  pickerYearRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: 16
  },
  pickerYearText: {
    fontSize: 20, fontWeight: '700', color: '#831843'
  },
  monthsGrid: {
    flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between'
  },
  monthCell: {
    width: '30%', paddingVertical: 12, alignItems: 'center', borderRadius: 12, marginBottom: 10, backgroundColor: '#F3F4F6'
  },
  monthCellActive: {
    backgroundColor: '#BE185D'
  },
  monthCellText: {
    fontSize: 16, color: '#4B5563', fontWeight: '500'
  },
  monthCellTextActive: {
    color: '#FFF', fontWeight: '700'
  },
  modalCloseBtn: {
    marginTop: 10, paddingVertical: 10, paddingHorizontal: 30, borderRadius: 20, backgroundColor: '#F3F4F6'
  },
  modalCloseBtnText: {
    color: '#4B5563', fontSize: 16, fontWeight: '600'
  },
  monthPill: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: '#FDF2F8', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20
  }
});
