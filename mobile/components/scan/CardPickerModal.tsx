import React from 'react';
import { Modal, View, Text, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { UserCard } from '../../../src/api/cards';

interface CardPickerModalProps {
  visible: boolean;
  userCards: UserCard[];
  selectedUserCard: UserCard | null;
  onSelect: (card: UserCard) => void;
  onClose: () => void;
}

export default function CardPickerModal({ visible, userCards, selectedUserCard, onSelect, onClose }: CardPickerModalProps) {
  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.modalBox}>
          <Text style={styles.modalTitle}>選擇記帳卡片</Text>
          <ScrollView style={{ maxHeight: '80%' }} showsVerticalScrollIndicator={false}>
            {userCards.length === 0
              ? <Text style={styles.modalEmpty}>請先至「名下卡片」頁面設定持有卡片。</Text>
              : userCards.map(uc => (
                <TouchableOpacity
                  key={uc.id}
                  style={[styles.modalCardRow, selectedUserCard?.id === uc.id && styles.modalCardRowActive]}
                  onPress={() => { onSelect(uc); onClose(); }}
                >
                  <View>
                    <Text style={styles.modalCardName}>{uc.card.card_name}</Text>
                    <Text style={styles.modalCardBank}>{uc.card.bank_name} · 結帳日 {uc.billing_cycle_date} 號</Text>
                  </View>
                  {selectedUserCard?.id === uc.id && <Text style={styles.modalCheckmark}>✓</Text>}
                </TouchableOpacity>
              ))
            }
          </ScrollView>
          <TouchableOpacity style={styles.modalCloseBtn} onPress={onClose}>
            <Text style={styles.modalCloseBtnText}>關閉</Text>
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
  modalEmpty: { color: '#BE185D', fontSize: 15, textAlign: 'center', paddingVertical: 24 },
  modalCardRow: { flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 16, marginBottom: 10, backgroundColor: '#FFF5F8', borderWidth: 1, borderColor: '#FCE7F3' },
  modalCardRowActive: { borderColor: '#EC4899', backgroundColor: '#FFF0F5' },
  modalCardName: { color: '#831843', fontSize: 16, fontWeight: 'bold' },
  modalCardBank: { color: '#BE185D', fontSize: 13, marginTop: 4 },
  modalCheckmark: { marginLeft: 'auto', color: '#EC4899', fontSize: 20, fontWeight: '900' },
  modalCloseBtn: { backgroundColor: '#FFF0F5', borderRadius: 16, paddingVertical: 16, alignItems: 'center', marginTop: 12, borderWidth: 1, borderColor: '#FCE7F3' },
  modalCloseBtnText: { color: '#DB2777', fontSize: 16, fontWeight: '700' },
});
