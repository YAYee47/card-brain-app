import React from 'react';
import { View, Text, TouchableOpacity, SafeAreaView, StyleSheet } from 'react-native';

interface SuccessScreenProps {
  successTxn: any;
  onReset: () => void;
}

export default function SuccessScreen({ successTxn, onReset }: SuccessScreenProps) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.successBox}>
        <Text style={styles.successIcon}>✅</Text>
        <Text style={styles.successTitle}>記帳成功！</Text>
        <View style={styles.successCard}>
          <Row label="消費金額" value={`${successTxn.currency} ${successTxn.original_amount.toLocaleString()}`} />
          <Row label="台幣換算" value={`NT$${successTxn.ntd_amount.toLocaleString()}`} />
          <Row label="支付通道" value={successTxn.channel_name} />
          <Row label="消費分類" value={successTxn.category} />
          {successTxn.merchant_name && <Row label="商家" value={successTxn.merchant_name} />}
          <View style={styles.divider} />
          <Row label="本次獲得回饋" value={`+NT$${successTxn.earned_cashback_ntd}`} highlight />
          <Row label="來源" value={successTxn.source_type} small />
        </View>
        <TouchableOpacity style={styles.doneBtn} onPress={onReset}>
          <Text style={styles.doneBtnText}>繼續記帳</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

function Row({ label, value, highlight, small }: { label: string; value: string; highlight?: boolean; small?: boolean }) {
  return (
    <View style={styles.successRow}>
      <Text style={[styles.successRowLabel, small && { fontSize: 11 }]}>{label}</Text>
      <Text style={[styles.successRowValue, highlight && styles.successRowHighlight, small && { fontSize: 11 }]}>
        {value}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  successBox: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, backgroundColor: '#FFF0F5' },
  successIcon: { fontSize: 64, marginBottom: 16 },
  successTitle: { color: '#831843', fontSize: 26, fontWeight: '900', marginBottom: 24 },
  successCard: { backgroundColor: '#FFFFFF', borderRadius: 20, padding: 24, width: '100%', borderWidth: 1, borderColor: '#FCE7F3', marginBottom: 28, shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  successRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10 },
  successRowLabel: { color: '#9D174D', fontSize: 14, fontWeight: '500' },
  successRowValue: { color: '#831843', fontSize: 14, fontWeight: '700' },
  successRowHighlight: { color: '#059669', fontSize: 18, fontWeight: '900' },
  divider: { height: 1, backgroundColor: '#FCE7F3', marginVertical: 8 },
  doneBtn: { backgroundColor: '#DB2777', borderRadius: 16, paddingVertical: 18, paddingHorizontal: 56, shadowColor: '#DB2777', shadowOpacity: 0.3, shadowRadius: 10, elevation: 5 },
  doneBtnText: { color: '#fff', fontSize: 17, fontWeight: 'bold' },
});
