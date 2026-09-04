import React from 'react';
import { Modal, View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface CurrencyPickerModalProps {
  visible: boolean;
  selectedCurrency: string;
  onSelect: (currency: string) => void;
  onClose: () => void;
}

const CURRENCIES = ['TWD', 'JPY', 'KRW', 'CNY', 'USD'];

export default function CurrencyPickerModal({ visible, selectedCurrency, onSelect, onClose }: CurrencyPickerModalProps) {
  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.modalBox}>
          <Text style={styles.modalTitle}>選擇幣別</Text>
          {CURRENCIES.map(curr => (
            <TouchableOpacity
              key={curr}
              style={[styles.modalCardRow, selectedCurrency === curr && styles.modalCardRowActive]}
              onPress={() => {
                onSelect(curr);
                onClose();
              }}
            >
              <Text style={styles.modalCardName}>
                {curr}
              </Text>
              {selectedCurrency === curr && <Text style={styles.modalCheckmark}>✓</Text>}
            </TouchableOpacity>
          ))}
          <TouchableOpacity style={styles.modalCloseBtn} onPress={onClose}>
            <Text style={styles.modalCloseBtnText}>取消</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: { flex: 1, backgroundColor: 'rgba(252, 231, 243, 0.8)', justifyContent: 'flex-end' },
  modalBox: { backgroundColor: '#FFFFFF', borderTopLeftRadius: 32, borderTopRightRadius: 32, padding: 24, paddingBottom: 48, shadowColor: '#FDA4AF', shadowOpacity: 0.3, shadowRadius: 15, elevation: 10, borderWidth: 1, borderColor: '#FCE7F3' },
  modalTitle: { color: '#831843', fontSize: 18, fontWeight: '900', marginBottom: 20 },
  modalCardRow: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 16, marginBottom: 10, backgroundColor: '#FFF5F8', borderWidth: 1, borderColor: '#FCE7F3' },
  modalCardRowActive: { borderColor: '#EC4899', backgroundColor: '#FFF0F5' },
  modalCardName: { color: '#831843', fontSize: 16, fontWeight: 'bold' },
  modalCheckmark: { marginLeft: 'auto', color: '#EC4899', fontSize: 20, fontWeight: '900' },
  modalCloseBtn: { backgroundColor: '#FFF0F5', borderRadius: 16, paddingVertical: 16, alignItems: 'center', marginTop: 12, borderWidth: 1, borderColor: '#FCE7F3' },
  modalCloseBtnText: { color: '#DB2777', fontSize: 16, fontWeight: '700' },
});
