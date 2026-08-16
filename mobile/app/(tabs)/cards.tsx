import React, { useEffect, useState } from 'react';
import {
  StyleSheet, Text, View, ScrollView, TouchableOpacity,
  ActivityIndicator, Modal, TextInput, Alert, SafeAreaView,
  Keyboard, TouchableWithoutFeedback
} from 'react-native';
import { fetchAllCards, addUserCard, fetchUserCards, createCustomUserCard, deleteUserCard, Card, UserCard } from '../../src/api/cards';
import CardDetailsModal from '../../src/components/CardDetailsModal';
import { Ionicons } from '@expo/vector-icons';

export default function CardsScreen() {
  const [allCards, setAllCards] = useState<Card[]>([]);
  const [userCards, setUserCards] = useState<UserCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const userCardIds = new Set(userCards.map(uc => uc.card_id));

  // 卡片詳情 Modal 狀態
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [detailsCard, setDetailsCard] = useState<Card | null>(null);

  const [tutorialVisible, setTutorialVisible] = useState(false);

  // 自訂卡片 Modal
  const [customVisible, setCustomVisible] = useState(false);
  const [customBank, setCustomBank] = useState('');
  const [customName, setCustomName] = useState('');
  const [customUrl, setCustomUrl] = useState('');
  const [customCycle, setCustomCycle] = useState('');
  const [addingCustom, setAddingCustom] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [cards, uCards] = await Promise.all([fetchAllCards(), fetchUserCards()]);
      setAllCards(cards);
      setUserCards(uCards);
    } catch (e) {
      setError('無法連線至後端 API，請確認伺服器已啟動。');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleShowTutorial = () => {
    setTutorialVisible(true);
  };

  const handleAddCustom = async () => {
    if (!customBank || !customName || !customCycle) {
      Alert.alert('提示', '銀行名稱、卡片名稱與結帳日為必填項目。');
      return;
    }
    const cycleNum = parseInt(customCycle, 10);
    if (isNaN(cycleNum) || cycleNum < 1 || cycleNum > 31) {
      Alert.alert('提示', '請輸入 1~31 的結帳日。');
      return;
    }

    setAddingCustom(true);
    try {
      await createCustomUserCard({
        bank_name: customBank,
        card_name: customName,
        benefit_url: customUrl || undefined,
        billing_cycle_date: cycleNum
      });
      setCustomVisible(false);
      setCustomBank('');
      setCustomName('');
      setCustomUrl('');
      setCustomCycle('');
      loadData();
      Alert.alert('成功', '自訂卡片已加入錢包！\n您可以將多個網址用逗號分隔填入權益網址中。');
    } catch (e: any) {
      Alert.alert('錯誤', '新增自訂卡片失敗');
    } finally {
      setAddingCustom(false);
    }
  };

  const handleDeleteCard = async (userCardId: number) => {
    Alert.alert('確認移除', '確定要從錢包中移除這張卡片嗎？（歷史記帳紀錄將會保留）', [
      { text: '取消', style: 'cancel' },
      { 
        text: '確定移除', 
        style: 'destructive',
        onPress: async () => {
          try {
            await deleteUserCard(userCardId);
            setDetailsVisible(false);
            loadData();
          } catch (e) {
            Alert.alert('錯誤', '移除卡片失敗');
          }
        }
      }
    ]);
  };

  if (loading) {
    return (
      <View style={styles.centerBox}>
        <ActivityIndicator size="large" color="#38BDF8" />
        <Text style={styles.loadingText}>載入信用卡資料中...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerBox}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={loadData}>
          <Text style={styles.retryBtnText}>重試連線</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // 將卡片依是否已持有分組
  const ownedCards = allCards.filter(c => userCardIds.has(c.id));
  const notOwnedCards = allCards.filter(c => !userCardIds.has(c.id));

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>

        {/* 已持有卡片 */}
        {ownedCards.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>✅ 已追蹤的卡片 ({ownedCards.length})</Text>
            {ownedCards.map(card => {
              const uc = userCards.find(uc => uc.card_id === card.id);
              return (
                <TouchableOpacity 
                  key={card.id} 
                  style={[styles.cardRow, styles.cardOwned]}
                  onPress={() => { setDetailsCard(card); setDetailsVisible(true); }}
                >
                  <View style={styles.cardInfo}>
                    <Text style={styles.cardName}>{card.card_name}</Text>
                    <Text style={styles.bankName}>{card.bank_name}</Text>
                    <Text style={styles.billingInfo}>帳單結帳日：每月 {uc?.billing_cycle_date} 號</Text>
                  </View>
                  <View style={styles.ownedBadge}>
                    <Text style={styles.ownedBadgeText}>查看權益</Text>
                  </View>
                </TouchableOpacity>
              );
            })}
          </>
        )}

      </ScrollView>



      {/* 權益詳情 Modal */}
      <CardDetailsModal 
        visible={detailsVisible} 
        card={detailsCard} 
        userCardId={userCards.find(uc => uc.card_id === detailsCard?.id)?.id}
        onClose={() => setDetailsVisible(false)} 
        onDelete={handleDeleteCard}
      />

      {/* FAB 新增自訂卡片 */}
      <TouchableOpacity style={styles.fab} onPress={() => setCustomVisible(true)}>
        <Ionicons name="add" size={32} color="#FFF" />
      </TouchableOpacity>

      {/* 自訂卡片 Modal */}
      <Modal visible={customVisible} animationType="slide" transparent>
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.modalOverlay}>
            <TouchableWithoutFeedback>
              <View style={styles.modalBox}>
                <Text style={styles.modalTitle}>新增自訂卡片</Text>
                <Text style={styles.modalHint}>
                  手動建立您的專屬卡片並加入錢包{'\n'}
                  <Text style={{ fontSize: 12, color: '#F472B6' }}>加入錢包需要較久時間爬蟲，請耐心等待{'\n'}如果遇到鍵盤收不起來請點擊旁邊的淺粉色空白框即可收起鍵盤</Text>
                </Text>
                
                <Text style={styles.modalLabel}>卡片銀行 (必填)</Text>
                <TextInput style={styles.modalInputText} placeholder="例如：玉山銀行" value={customBank} onChangeText={setCustomBank} />
                
                <Text style={styles.modalLabel}>卡片名稱 (必填)</Text>
                <TextInput style={styles.modalInputText} placeholder="例如：U Bear 信用卡" value={customName} onChangeText={setCustomName} />
                
                <Text style={styles.modalLabel}>權益網址 (選填，可多個用逗號分隔)</Text>
                <TextInput style={styles.modalInputText} placeholder="例如：https://esun.com/ubear" value={customUrl} onChangeText={setCustomUrl} />
                
                <Text style={styles.modalLabel}>帳單結帳日 (1~31，必填)</Text>
                <TextInput 
                  style={styles.modalInputText} 
                  placeholder="例如：15" 
                  value={customCycle} 
                  onChangeText={setCustomCycle} 
                  keyboardType="numeric" 
                  returnKeyType="done"
                />

            <View style={styles.modalActions}>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setCustomVisible(false)}>
                <Text style={styles.cancelBtnText}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.confirmBtn} onPress={handleAddCustom} disabled={addingCustom}>
                {addingCustom ? <ActivityIndicator color="#FFF" /> : <Text style={styles.confirmBtnText}>新增至錢包</Text>}
              </TouchableOpacity>
            </View>
          </View>
        </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
      </Modal>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' }, // Very light girly pink
  content: { padding: 16, paddingBottom: 40 },
  centerBox: { flex: 1, backgroundColor: '#FFF0F5', justifyContent: 'center', alignItems: 'center', padding: 20 },
  loadingText: { color: '#BE185D', marginTop: 12, fontSize: 14 },
  errorText: { color: '#E11D48', fontSize: 14, textAlign: 'center', marginBottom: 16 },
  retryBtn: { backgroundColor: '#FCE7F3', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8, borderWidth: 1, borderColor: '#FBCFE8' },
  retryBtnText: { color: '#BE185D', fontSize: 14, fontWeight: '600' },
  sectionTitle: { color: '#9D174D', fontSize: 14, fontWeight: '700', marginBottom: 10, marginTop: 8, letterSpacing: 0.5 },
  cardRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3, borderWidth: 1, borderColor: '#FCE7F3' },
  cardOwned: { borderColor: '#F472B6', borderWidth: 2, backgroundColor: '#FFF5F8' },
  cardInfo: { flex: 1 },
  cardName: { color: '#831843', fontSize: 17, fontWeight: 'bold' },
  bankName: { color: '#BE185D', fontSize: 13, marginTop: 4 },
  benefitCount: { color: '#DB2777', fontSize: 12, marginTop: 6, fontWeight: '500' },
  billingInfo: { color: '#059669', fontSize: 12, marginTop: 6, fontWeight: '500' },
  ownedBadge: { backgroundColor: '#FCE7F3', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, borderWidth: 1, borderColor: '#FBCFE8' },
  ownedBadgeText: { color: '#DB2777', fontSize: 12, fontWeight: '700' },
  addBadge: { backgroundColor: '#EC4899', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, shadowColor: '#EC4899', shadowOpacity: 0.3, shadowRadius: 4, elevation: 2 },
  addBadgeText: { color: '#FFFFFF', fontSize: 12, fontWeight: '700' },
  tutorialBtn: { backgroundColor: '#FCE7F3', borderRadius: 12, paddingVertical: 14, alignItems: 'center', borderWidth: 1, borderColor: '#FBCFE8', marginTop: 16, marginBottom: 16 },
  tutorialBtnText: { color: '#9D174D', fontSize: 15, fontWeight: '700' },
  // Modal
  modalOverlay: { flex: 1, backgroundColor: 'rgba(131, 24, 67, 0.5)', justifyContent: 'center', alignItems: 'center', padding: 24 },
  modalBox: { backgroundColor: '#FFFFFF', borderRadius: 20, padding: 24, width: '100%', shadowColor: '#9D174D', shadowOpacity: 0.2, shadowRadius: 15, elevation: 10 },
  modalTitle: { color: '#831843', fontSize: 18, fontWeight: 'bold', marginBottom: 6 },
  
  // Tutorial Modal
  tutorialModalBox: { backgroundColor: '#FFF0F5', borderRadius: 24, padding: 24, width: '100%', shadowColor: '#EC4899', shadowOpacity: 0.3, shadowRadius: 20, elevation: 15, borderWidth: 2, borderColor: '#FBCFE8' },
  tutorialModalTitle: { color: '#9D174D', fontSize: 20, fontWeight: '800', textAlign: 'center', marginBottom: 24, letterSpacing: 1 },
  tutorialStep: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 20, backgroundColor: '#FFFFFF', padding: 16, borderRadius: 16, shadowColor: '#F9A8D4', shadowOpacity: 0.2, shadowRadius: 8, elevation: 2 },
  tutorialIcon: { fontSize: 24, marginRight: 16, marginTop: 2 },
  tutorialTextContainer: { flex: 1 },
  tutorialStepTitle: { color: '#BE185D', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  tutorialStepDesc: { color: '#831843', fontSize: 14, lineHeight: 20 },
  tutorialCloseBtn: { backgroundColor: '#EC4899', borderRadius: 16, paddingVertical: 14, alignItems: 'center', marginTop: 10, shadowColor: '#EC4899', shadowOpacity: 0.4, shadowRadius: 8, elevation: 4 },
  tutorialCloseBtnText: { color: '#FFFFFF', fontSize: 16, fontWeight: 'bold', letterSpacing: 1 },
  modalCard: { color: '#DB2777', fontSize: 15, marginBottom: 24, fontWeight: '600' },
  modalLabel: { color: '#9D174D', fontSize: 13, marginBottom: 8, fontWeight: '600' },
  modalInput: { backgroundColor: '#FFF0F5', color: '#831843', fontSize: 24, fontWeight: 'bold', textAlign: 'center', borderRadius: 12, paddingVertical: 14, borderWidth: 1, borderColor: '#FBCFE8', marginBottom: 12 },
  modalHint: { color: '#BE185D', fontSize: 12, textAlign: 'center', marginBottom: 24, lineHeight: 18 },
  modalActions: { flexDirection: 'row', gap: 12 },
  cancelBtn: { flex: 1, backgroundColor: '#FCE7F3', borderRadius: 12, paddingVertical: 14, alignItems: 'center', borderWidth: 1, borderColor: '#FBCFE8' },
  cancelBtnText: { color: '#9D174D', fontSize: 15, fontWeight: '700' },
  confirmBtn: { flex: 1, backgroundColor: '#EC4899', borderRadius: 12, paddingVertical: 14, alignItems: 'center', shadowColor: '#EC4899', shadowOpacity: 0.3, shadowRadius: 6, elevation: 3 },
  confirmBtnText: { color: '#FFFFFF', fontSize: 15, fontWeight: 'bold' },
  fab: { position: 'absolute', bottom: 20, right: 20, backgroundColor: '#EC4899', width: 64, height: 64, borderRadius: 32, justifyContent: 'center', alignItems: 'center', shadowColor: '#EC4899', shadowOpacity: 0.4, shadowRadius: 8, elevation: 5 },
  modalInputText: { backgroundColor: '#FFF0F5', color: '#831843', fontSize: 16, borderRadius: 12, paddingVertical: 12, paddingHorizontal: 16, borderWidth: 1, borderColor: '#FBCFE8', marginBottom: 16 },
});
