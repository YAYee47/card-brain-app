import React from 'react';
import {
  StyleSheet, Text, View, Modal, TouchableOpacity, ScrollView, Linking
} from 'react-native';
import { Card } from '../api/cards';

interface CardDetailsModalProps {
  visible: boolean;
  card: Card | null;
  userCardId?: number;
  onClose: () => void;
  onDelete?: (userCardId: number) => void;
}

export default function CardDetailsModal({ visible, card, userCardId, onClose, onDelete }: CardDetailsModalProps) {
  if (!card) return null;

  const isJCB = card.bank_name.includes('JCB') || card.card_name.includes('JCB');

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modalBox}>
          
          <View style={styles.header}>
            <Text style={styles.cardTitle}>{card.bank_name} {card.card_name}</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Text style={styles.closeBtnText}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {/* JCB APP 活動區塊 */}
            {isJCB && (
              <View style={styles.jcbBox}>
                <Text style={styles.jcbTitle}>✨ JCB APP 限定活動</Text>
                <Text style={styles.jcbDesc}>JCB 專屬活動（如 MyJapan+）需至官方 APP 手動登錄，請前往查看並登錄以享有優惠。</Text>
                <TouchableOpacity 
                  style={styles.jcbBtn} 
                  onPress={() => Linking.openURL('https://www.specialoffers.jcb/zh-tw/')}
                >
                  <Text style={styles.jcbBtnText}>前往 JCB 官網查看活動 →</Text>
                </TouchableOpacity>
              </View>
            )}

            <Text style={styles.sectionTitle}>💳 信用卡權益</Text>
            {card.benefits.length === 0 ? (
              <View style={styles.emptyBenefits}>
                <Text style={styles.emptyBenefitsText}>此卡片目前沒有自動爬取的權益資料（可能是因為您沒有提供網址，或網頁防爬蟲機制阻擋）。但您依然可以將它用於「相機記帳」與額度管理！</Text>
              </View>
            ) : (
              <View style={styles.table}>
                <View style={styles.tableHeader}>
                  <Text style={[styles.th, { flex: 2 }]}>通路</Text>
                  <Text style={[styles.th, { flex: 1, textAlign: 'center' }]}>基礎</Text>
                  <Text style={[styles.th, { flex: 1, textAlign: 'center' }]}>加碼</Text>
                  <Text style={[styles.th, { flex: 1.5, textAlign: 'right' }]}>加碼上限</Text>
                </View>
              {card.benefits.map((b) => (
                <View key={b.id} style={styles.tableRow}>
                  <Text style={[styles.td, { flex: 2 }]} numberOfLines={2}>{b.channel_name}</Text>
                  <Text style={[styles.td, { flex: 1, textAlign: 'center' }]}>
                    {b.base_rate}%{'\n'}
                    <Text style={{ fontSize: 10, color: '#DB2777' }}>(無上限)</Text>
                  </Text>
                  <Text style={[styles.td, { flex: 1, textAlign: 'center', color: '#EC4899', fontWeight: 'bold' }]}>
                    {b.bonus_rate > 0 ? `+${b.bonus_rate}%` : '-'}
                  </Text>
                  <Text style={[styles.td, { flex: 1.5, textAlign: 'right' }]}>
                    {b.monthly_cap_ntd ? `$${b.monthly_cap_ntd}` : '無上限'}
                  </Text>
                </View>
              ))}
            </View>
            )}

            <View style={styles.footer}>
              {card.last_synced_at && card.benefits.length > 0 && (
                <Text style={styles.footerText}>
                  最後更新：{new Date(card.last_synced_at).toLocaleString('zh-TW', { hour12: false })}
                </Text>
              )}
              {card.benefit_url && (
                <TouchableOpacity 
                  onPress={() => Linking.openURL(card.benefit_url!.split(',')[0].trim())} 
                  style={styles.linkBtn}
                >
                  <Text style={styles.linkText}>查看官方網頁 →</Text>
                </TouchableOpacity>
              )}
              
              {userCardId && onDelete && (
                <TouchableOpacity onPress={() => onDelete(userCardId)} style={styles.deleteBtn}>
                  <Text style={styles.deleteBtnText}>從錢包移除此卡片</Text>
                </TouchableOpacity>
              )}
            </View>
          </ScrollView>

        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: { 
    flex: 1, 
    backgroundColor: 'rgba(252, 231, 243, 0.8)', // Light pink overlay
    justifyContent: 'flex-end' 
  },
  modalBox: { 
    backgroundColor: '#FFFFFF', // White background
    borderTopLeftRadius: 32, 
    borderTopRightRadius: 32, 
    padding: 24, 
    height: '85%',
    borderTopWidth: 1, 
    borderColor: '#FBCFE8',
    shadowColor: '#FDA4AF',
    shadowOpacity: 0.3,
    shadowRadius: 15,
    elevation: 10
  },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: 20 
  },
  cardTitle: { 
    color: '#831843', 
    fontSize: 22, 
    fontWeight: '900' 
  },
  closeBtn: { 
    padding: 8, 
    backgroundColor: '#FFF0F5', 
    borderRadius: 20 
  },
  closeBtnText: { 
    color: '#EC4899', 
    fontSize: 16, 
    fontWeight: 'bold' 
  },
  content: { 
    flex: 1 
  },
  jcbBox: { 
    backgroundColor: '#FFF5F8', 
    padding: 16, 
    borderRadius: 16, 
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#FBCFE8'
  },
  jcbTitle: { 
    color: '#DB2777', 
    fontSize: 16, 
    fontWeight: '800', 
    marginBottom: 8 
  },
  jcbDesc: { 
    color: '#9D174D', 
    fontSize: 13, 
    lineHeight: 20, 
    marginBottom: 12 
  },
  jcbBtn: { 
    backgroundColor: '#EC4899', 
    paddingVertical: 12, 
    borderRadius: 12, 
    alignItems: 'center',
    shadowColor: '#EC4899',
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 3
  },
  jcbBtnText: { 
    color: '#FFFFFF', 
    fontSize: 14, 
    fontWeight: 'bold' 
  },
  sectionTitle: { 
    color: '#DB2777', 
    fontSize: 16, 
    fontWeight: '800', 
    marginBottom: 12 
  },
  table: { 
    backgroundColor: '#FFFFFF', 
    borderRadius: 16, 
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#FCE7F3'
  },
  tableHeader: { 
    flexDirection: 'row', 
    backgroundColor: '#FFF0F5', 
    paddingVertical: 12, 
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#FCE7F3'
  },
  th: { 
    color: '#831843', 
    fontSize: 12, 
    fontWeight: '700' 
  },
  tableRow: { 
    flexDirection: 'row', 
    borderBottomWidth: 1, 
    borderBottomColor: '#FFF0F5', 
    paddingVertical: 14, 
    paddingHorizontal: 12, 
    alignItems: 'center' 
  },
  td: { 
    color: '#9D174D', 
    fontSize: 13,
    fontWeight: '500'
  },
  footer: { 
    marginTop: 24, 
    alignItems: 'center', 
    paddingBottom: 40 
  },
  footerText: { 
    color: '#BE185D', 
    fontSize: 12, 
    marginBottom: 12,
    fontWeight: '500'
  },
  linkBtn: { 
    borderWidth: 2, 
    borderColor: '#DB2777', 
    paddingHorizontal: 20, 
    paddingVertical: 10, 
    borderRadius: 20,
    marginBottom: 16
  },
  linkText: { 
    color: '#DB2777', 
    fontSize: 14, 
    fontWeight: '700' 
  },
  deleteBtn: {
    backgroundColor: '#FFF0F5',
    paddingHorizontal: 20, 
    paddingVertical: 12, 
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#FBCFE8'
  },
  deleteBtnText: {
    color: '#E11D48',
    fontSize: 14,
    fontWeight: '700'
  },
  emptyBenefits: {
    backgroundColor: '#FFF5F8',
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#FCE7F3',
    alignItems: 'center'
  },
  emptyBenefitsText: {
    color: '#9D174D',
    fontSize: 14,
    lineHeight: 22,
    textAlign: 'center',
    fontWeight: '600'
  }
});
