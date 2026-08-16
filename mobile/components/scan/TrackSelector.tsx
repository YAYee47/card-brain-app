import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

const TRACK_LABELS: { key: 'receipt' | 'manual'; icon: string; label: string; desc: string }[] = [
  { key: 'receipt', icon: '🖼️', label: 'AI 收據辨識', desc: '拍攝紙本/外幣收據交 AI 解析' },
  { key: 'manual', icon: '✏️', label: '手動記帳', desc: '3 秒快速輸入金額' },
];

interface TrackSelectorProps {
  onSelectTrack: (track: 'receipt' | 'manual') => void;
  onNavigateAnalytics: () => void;
}

export default function TrackSelector({ onSelectTrack, onNavigateAnalytics }: TrackSelectorProps) {
  return (
    <>
      <Text style={styles.sectionLabel}>選擇記帳方式</Text>
      <View style={styles.trackGrid}>
        {TRACK_LABELS.map(t => (
          <TouchableOpacity key={t.key} style={styles.trackCard} onPress={() => onSelectTrack(t.key)}>
            <Text style={styles.trackIcon}>{t.icon}</Text>
            <Text style={styles.trackLabel}>{t.label}</Text>
            <Text style={styles.trackDesc}>{t.desc}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.sectionLabel}>財務分析</Text>
      <TouchableOpacity 
        style={[styles.trackCard, { width: '100%', flexDirection: 'row', alignItems: 'center' }]} 
        onPress={onNavigateAnalytics}
      >
        <View style={{ flex: 1 }}>
          <Text style={[styles.trackIcon, { fontSize: 32 }]}>📊</Text>
          <Text style={[styles.trackLabel, { fontSize: 16 }]}>本月消費分析</Text>
          <Text style={styles.trackDesc}>以圓餅圖查看本月花費與獲得回饋</Text>
        </View>
        <Text style={{ fontSize: 24, color: '#F472B6', fontWeight: 'bold' }}>→</Text>
      </TouchableOpacity>
    </>
  );
}

const styles = StyleSheet.create({
  sectionLabel: { color: '#BE185D', fontSize: 13, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 12, marginTop: 8 },
  trackGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 8 },
  trackCard: { width: '47%', backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#FCE7F3', alignItems: 'flex-start', shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  trackIcon: { fontSize: 28, marginBottom: 8 },
  trackLabel: { color: '#831843', fontSize: 14, fontWeight: '800', marginBottom: 6 },
  trackDesc: { color: '#BE185D', fontSize: 12, lineHeight: 18 },
});
