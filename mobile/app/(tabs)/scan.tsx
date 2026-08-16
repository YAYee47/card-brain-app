import React, { useState, useCallback, useEffect } from 'react';
import {
  StyleSheet, Text, View, SafeAreaView, TouchableOpacity,
  ScrollView, TextInput, ActivityIndicator, Alert,
  KeyboardAvoidingView, Platform
} from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { fetchUserCards, UserCard } from '../../src/api/cards';
import { fetchChannels } from '../../src/api/recommend';
import { createTransaction, TransactionCreate, uploadImageForOcr } from '../../src/api/transactions';

// Components
import CardPickerModal from '../../components/scan/CardPickerModal';
import CurrencyPickerModal from '../../components/scan/CurrencyPickerModal';
import DatePickerModal from '../../components/scan/DatePickerModal';
import TrackSelector from '../../components/scan/TrackSelector';
import SuccessScreen from '../../components/scan/SuccessScreen';

// ── 常數 ─────────────────────────────────────────────────────
const CATEGORIES = ['餐飲', '購物', '交通', '數位網購', '娛樂', '固定支出', '其他'];
type TrackType = 'receipt' | 'manual' | 'qrcode';

type FormState = {
  amount: string;
  currency: string;
  merchant: string;
  channel: string;
  category: string;
  sourceType: string;
  transactedAt: string;
  cardMode?: string;
};

export default function ScanScreen() {
  const router = useRouter();
  const [activeTrack, setActiveTrack] = useState<TrackType | null>(null);
  
  const [userCards, setUserCards] = useState<UserCard[]>([]);
  const [channels, setChannels] = useState<string[]>([]);
  const [selectedUserCard, setSelectedUserCard] = useState<UserCard | null>(null);
  const today = new Date().toISOString().split('T')[0];
  const [form, setForm] = useState<FormState>({
    amount: '', currency: 'TWD', merchant: '', channel: '通用', category: '其他', sourceType: 'MANUAL', transactedAt: today, cardMode: '任意選'
  });
  
  const [submitting, setSubmitting] = useState(false);
  const [successTxn, setSuccessTxn] = useState<any>(null);
  
  // Modals visibility
  const [cardPickerVisible, setCardPickerVisible] = useState(false);
  const [currencyPickerVisible, setCurrencyPickerVisible] = useState(false);
  const [datePickerVisible, setDatePickerVisible] = useState(false);

  // QR Code track (left out in components to save time, kept here)
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [qrInput, setQrInput] = useState('');

  useEffect(() => {
    fetchUserCards().then(cards => {
      setUserCards(cards);
    }).catch(() => {});
    fetchChannels().then(chs => setChannels(chs)).catch(() => {});
  }, []);

  useFocusEffect(
    useCallback(() => {
      setSelectedUserCard(null);
    }, [])
  );

  const resetForm = () => {
    const today = new Date().toISOString().split('T')[0];
    setForm({ amount: '', currency: 'TWD', merchant: '', channel: '通用', category: '其他', sourceType: 'MANUAL', transactedAt: today, cardMode: '任意選' });
    setSelectedUserCard(null);
    setSuccessTxn(null);
    setActiveTrack(null);
  };

  const [ocrLoading, setOcrLoading] = useState(false);
  const handleImagePick = async (useCamera: boolean = false) => {
    try {
      if (useCamera) {
        const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
        if (!permissionResult.granted) {
          Alert.alert('需要權限', '請允許相機存取權限才能拍攝圖片。');
          return;
        }
      } else {
        const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (!permissionResult.granted) {
          Alert.alert('需要權限', '請允許相簿存取權限才能選取圖片。');
          return;
        }
      }

      const result = useCamera 
        ? await ImagePicker.launchCameraAsync({ quality: 0.8 })
        : await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ['images'],
            allowsEditing: false,
            quality: 0.8,
          });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setOcrLoading(true);
        const ocrData = await uploadImageForOcr(result.assets[0].uri, activeTrack === 'receipt' ? 'receipt' : 'screenshot');
        
        if (ocrData.confidence === 'low' && ocrData.raw_text?.includes('失敗')) {
          Alert.alert('辨識失敗', ocrData.raw_text);
        } else {
          setForm(f => ({
            ...f,
            amount: ocrData.amount ? String(ocrData.amount) : '',
            currency: ocrData.currency || 'TWD',
            merchant: ocrData.merchant_name || '',
            channel: ocrData.channel_name || '通用',
            category: ocrData.category || '其他',
            sourceType: activeTrack === 'receipt' ? 'RECEIPT' : 'SCREENSHOT',
            transactedAt: ocrData.transaction_date || '',
          }));
          
          if (!ocrData.amount) {
            Alert.alert('部分辨識成功', '無法清楚辨識金額，請您手動補填。');
          } else {
            Alert.alert('辨識成功', '已自動填寫表單！');
          }
        }
      }
    } catch (e: any) {
      Alert.alert('發生錯誤', e?.message || '發生錯誤');
    } finally {
      setOcrLoading(false);
    }
  };

  const handleBarcodeScanned = ({ type, data }: { type: string; data: string }) => {
    setScanned(true);
    handleParseQRCode(data);
  };

  const handleParseQRCode = (text: string) => {
    if (!text || text.length < 50) {
      Alert.alert('錯誤', '無效的發票 QR Code 字串');
      return;
    }
    const hexStr = text.substring(21, 29);
    const amount = parseInt(hexStr, 16);
    if (!isNaN(amount)) {
      setForm(f => ({ ...f, amount: String(amount), sourceType: 'INVOICE_QR' }));
    }
  };

  const handleSubmit = useCallback(async () => {
    const amt = parseFloat(form.amount);
    if (!selectedUserCard) {
      Alert.alert('請選擇信用卡', '請先選擇要記帳的信用卡。');
      return;
    }
    if (!amt || amt <= 0) {
      Alert.alert('金額錯誤', '請輸入有效的消費金額。');
      return;
    }
    setSubmitting(true);
    try {
      const payload: TransactionCreate = {
        user_card_id: selectedUserCard.id,
        channel_name: form.channel,
        category: form.category,
        merchant_name: form.merchant || undefined,
        original_amount: amt,
        currency: form.currency,
        source_type: form.sourceType,
        transacted_at: form.transactedAt ? form.transactedAt : undefined,
        card_mode: form.cardMode
      };
      const txn = await createTransaction(payload);
      setSuccessTxn(txn);
    } catch (e: any) {
      Alert.alert('記帳失敗', e?.response?.data?.detail ?? '請確認後端 API 連線正常。');
    } finally {
      setSubmitting(false);
    }
  }, [form, selectedUserCard]);

  // ── 成功畫面 ─────────────────────────────────────────────
  if (successTxn) {
    return <SuccessScreen successTxn={successTxn} onReset={resetForm} />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">

          {/* 四軌入口選擇 */}
          {!activeTrack && (
            <TrackSelector 
              onSelectTrack={(track) => setActiveTrack(track)}
              onNavigateAnalytics={() => router.push('/analytics')}
            />
          )}

          {/* ── 軌道 1：QR Code 掃描 ── */}
          {activeTrack === 'qrcode' && (
            <TrackSection title="📷 台灣電子發票 QR Code" onBack={() => {
                setActiveTrack(null);
                setSelectedUserCard(null);
              }}>
              {!permission ? (
                <ActivityIndicator color="#F472B6" />
              ) : !permission.granted ? (
                <View style={{ alignItems: 'center', marginVertical: 20 }}>
                  <Text style={{ textAlign: 'center', marginBottom: 10 }}>需要相機權限才能掃描 QR Code</Text>
                  <TouchableOpacity style={styles.parseBtn} onPress={requestPermission}>
                    <Text style={styles.parseBtnText}>允許相機權限</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={{ height: 300, borderRadius: 12, overflow: 'hidden', marginVertical: 10 }}>
                  <CameraView
                    style={{ flex: 1 }}
                    facing="back"
                    onBarcodeScanned={scanned ? undefined : handleBarcodeScanned}
                    barcodeScannerSettings={{
                      barcodeTypes: ["qr"],
                    }}
                  />
                  {scanned && (
                    <TouchableOpacity 
                      style={{ position: 'absolute', bottom: 20, alignSelf: 'center', backgroundColor: '#F472B6', padding: 12, borderRadius: 8 }}
                      onPress={() => setScanned(false)}
                    >
                      <Text style={{ color: '#fff', fontWeight: 'bold' }}>再次掃描</Text>
                    </TouchableOpacity>
                  )}
                </View>
              )}
              
              <Text style={styles.hint}>
                您也可以手動貼入 QR Code 原始字串進行測試：
              </Text>
              <TextInput
                style={styles.qrInput}
                value={qrInput}
                onChangeText={setQrInput}
                placeholder="貼入 QR Code 原始字串（左碼）"
                placeholderTextColor="#475569"
                multiline
              />
              <TouchableOpacity style={styles.parseBtn} onPress={() => handleParseQRCode(qrInput)}>
                <Text style={styles.parseBtnText}>解析文字 QR Code</Text>
              </TouchableOpacity>
              {form.amount !== '' && (
                <Text style={styles.parsedAmount}>解析金額：NT${parseFloat(form.amount).toLocaleString()}</Text>
              )}
            </TrackSection>
          )}

          {/* ── 軌道 2/3：AI 辨識說明 ── */}
          {(activeTrack === 'receipt') && (
            <TrackSection
              title={'🖼️ AI 收據辨識'}
              onBack={() => {
                setActiveTrack(null);
                setSelectedUserCard(null);
              }}
            >
              <View style={styles.aiBox}>
                <Text style={styles.aiBoxIcon}>🤖</Text>
                <Text style={styles.aiBoxTitle}>拍攝收據交 AI 解析</Text>
                <Text style={styles.aiBoxDesc}>點擊按鈕選取收據圖片，AI 將自動辨識消費金額、商家與幣別。</Text>
                <Text style={styles.aiBoxHint}>
                  ⓘ AI 辨識後會自動填入下方表單，您可確認後調整再送出。
                </Text>
                
                <View style={{ flexDirection: 'row', gap: 10, marginTop: 10 }}>
                  <TouchableOpacity 
                    style={[styles.uploadBtn, { flex: 1, backgroundColor: '#38BDF8' }]} 
                    onPress={() => handleImagePick(true)}
                    disabled={ocrLoading}
                  >
                    {ocrLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.uploadBtnText}>📷 拍攝收據</Text>}
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={[styles.uploadBtn, { flex: 1 }]} 
                    onPress={() => handleImagePick(false)}
                    disabled={ocrLoading}
                  >
                    {ocrLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.uploadBtnText}>🖼️ 從相簿選取</Text>}
                  </TouchableOpacity>
                </View>
              </View>

              <Text style={styles.sectionLabel}>記帳至哪張卡？</Text>
              <TouchableOpacity style={styles.cardPicker} onPress={() => setCardPickerVisible(true)}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cardPickerName}>{selectedUserCard?.card.card_name ?? '請選擇信用卡'}</Text>
                  {selectedUserCard && <Text style={styles.cardPickerBank}>{selectedUserCard.card.bank_name}</Text>}
                </View>
                <Text style={styles.cardPickerChevron}>›</Text>
              </TouchableOpacity>
            </TrackSection>
          )}

          {/* ── 軌道 4：手動記帳 ── */}
          {activeTrack === 'manual' && (
            <TrackSection title="✏️ 手動記帳" onBack={() => {
                setActiveTrack(null);
                setSelectedUserCard(null);
              }}>
              <Text style={styles.sectionLabel}>記帳至哪張卡？</Text>
              <TouchableOpacity style={styles.cardPicker} onPress={() => setCardPickerVisible(true)}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cardPickerName}>{selectedUserCard?.card.card_name ?? '請選擇信用卡'}</Text>
                  {selectedUserCard && <Text style={styles.cardPickerBank}>{selectedUserCard.card.bank_name}</Text>}
                </View>
                <Text style={styles.cardPickerChevron}>›</Text>
              </TouchableOpacity>
            </TrackSection>
          )}

          {/* ── 通用記帳表單（四軌共用）── */}
          {activeTrack !== null && (
            <>
              <Text style={styles.sectionLabel}>{activeTrack === 'manual' ? '輸入消費明細' : '消費明細確認'}</Text>
              <View style={styles.formCard}>

              {/* 金額 */}
              <FormField label="消費金額">
                <View style={styles.amountRow}>
                  <TextInput
                    style={styles.amountInput}
                    value={form.amount}
                    onChangeText={v => setForm(f => ({ ...f, amount: v }))}
                    keyboardType="numeric"
                    placeholder="0"
                    placeholderTextColor="#475569"
                  />
                  <TouchableOpacity
                    style={styles.currencyBtn}
                    onPress={() => setCurrencyPickerVisible(true)}
                  >
                    <Text style={styles.currencyBtnText}>{form.currency} ›</Text>
                  </TouchableOpacity>
                </View>
              </FormField>

              {/* 智慧輸入通道/商家 */}
              <FormField label="在哪裡消費 / 支付方式 (如：星巴克、LINE Pay)">
                <TextInput
                  style={styles.textInput}
                  value={form.channel}
                  onChangeText={v => setForm(f => ({ ...f, channel: v, merchant: v }))}
                  placeholder="輸入店名、平台或支付方式"
                  placeholderTextColor="#475569"
                />
                <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginTop: 10, marginHorizontal: -4 }}>
                  {['LINE Pay', 'Apple Pay', '全家', '7-11', '全聯', 'momo', '蝦皮', 'Uber Eats', '國外'].map(ch => (
                    <TouchableOpacity
                      key={ch}
                      style={[styles.chip, form.channel === ch && styles.chipActive, { marginBottom: 8, marginHorizontal: 4 }]}
                      onPress={() => setForm(f => ({ ...f, channel: ch, merchant: ch }))}
                    >
                      <Text style={[styles.chipText, form.channel === ch && styles.chipTextActive]}>
                        {ch}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </FormField>

              {/* 卡片模式選擇 (僅針對 Unicard) */}
              {selectedUserCard?.card.card_name.includes('Unicard') && (
                <FormField label="此卡目前的權益方案 (玉山 Unicard 專屬)">
                  <View style={{ flexDirection: 'row', gap: 10, marginTop: 5 }}>
                    {['簡單選', '任意選', 'UP選'].map(mode => (
                      <TouchableOpacity
                        key={mode}
                        style={[styles.chip, form.cardMode === mode && styles.chipActive, { flex: 1, paddingVertical: 12 }]}
                        onPress={() => setForm(f => ({ ...f, cardMode: mode }))}
                      >
                        <Text style={[styles.chipText, form.cardMode === mode && styles.chipTextActive, { textAlign: 'center' }]}>
                          {mode}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </FormField>
              )}

              {/* 刷卡日期 */}
              <FormField label="刷卡日期 (預設為今天)">
                <TouchableOpacity onPress={() => setDatePickerVisible(true)}>
                  <View pointerEvents="none">
                    <TextInput
                      style={styles.textInput}
                      value={form.transactedAt}
                      placeholder="YYYY-MM-DD"
                      placeholderTextColor="#475569"
                      editable={false}
                    />
                  </View>
                </TouchableOpacity>
              </FormField>

              {/* 消費分類 */}
              <FormField label="消費分類">
                <View style={styles.categoryGrid}>
                  {CATEGORIES.map(cat => (
                    <TouchableOpacity
                      key={cat}
                      style={[styles.catBtn, form.category === cat && styles.catBtnActive]}
                      onPress={() => setForm(f => ({ ...f, category: cat }))}
                    >
                      <Text style={[styles.catBtnText, form.category === cat && styles.catBtnTextActive]}>
                        {cat}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </FormField>

              {/* 送出 */}
              <TouchableOpacity
                style={[styles.submitBtn, submitting && { opacity: 0.6 }]}
                onPress={handleSubmit}
                disabled={submitting}
              >
                {submitting
                  ? <ActivityIndicator color="#fff" />
                  : <Text style={styles.submitBtnText}>確認記帳 →</Text>
                }
              </TouchableOpacity>
            </View>
            </>
          )}

        </ScrollView>
      </KeyboardAvoidingView>

      <CardPickerModal 
        visible={cardPickerVisible} 
        userCards={userCards}
        selectedUserCard={selectedUserCard}
        onSelect={setSelectedUserCard}
        onClose={() => setCardPickerVisible(false)}
      />

      <CurrencyPickerModal
        visible={currencyPickerVisible}
        selectedCurrency={form.currency}
        onSelect={(curr) => setForm(f => ({ ...f, currency: curr }))}
        onClose={() => setCurrencyPickerVisible(false)}
      />

      <DatePickerModal
        visible={datePickerVisible}
        value={form.transactedAt}
        onChange={(dateStr) => setForm(f => ({ ...f, transactedAt: dateStr }))}
        onClose={() => setDatePickerVisible(false)}
      />

    </SafeAreaView>
  );
}

// ── 子元件 ─────────────────────────────────────────────────────
function TrackSection({ title, onBack, children }: { title: string; onBack: () => void; children: React.ReactNode }) {
  return (
    <View style={styles.trackSection}>
      <View style={styles.trackSectionHeader}>
        <TouchableOpacity style={styles.backBtn} onPress={onBack}>
          <Text style={{ fontSize: 18, color: '#831843', marginRight: 4 }}>‹</Text>
          <Text style={styles.backBtnText}>返回</Text>
        </TouchableOpacity>
      </View>
      {children}
    </View>
  );
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View style={styles.formField}>
      <Text style={styles.formFieldLabel}>{label}</Text>
      {children}
    </View>
  );
}

// ── Styles ────────────────────────────────────────────────────
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  content: { padding: 16, paddingBottom: 48 },

  sectionLabel: { color: '#BE185D', fontSize: 13, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 12, marginTop: 8 },

  // 卡片選擇器
  cardPicker: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, flexDirection: 'row', alignItems: 'center', marginBottom: 20, borderWidth: 1, borderColor: '#FCE7F3', shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  cardPickerIcon: { fontSize: 26, marginRight: 12 },
  cardPickerName: { color: '#831843', fontSize: 16, fontWeight: 'bold' },
  cardPickerBank: { color: '#BE185D', fontSize: 13, marginTop: 2 },
  cardPickerChevron: { color: '#F472B6', fontSize: 24 },

  // 軌道 section
  trackSection: { marginBottom: 16 },
  trackSectionHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 16, gap: 12 },
  backBtn: { backgroundColor: '#FFFFFF', paddingHorizontal: 16, paddingVertical: 6, borderRadius: 24, flexDirection: 'row', alignItems: 'center', shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  backBtnText: { color: '#831843', fontSize: 15, fontWeight: '700' },

  // QR Code 軌道
  hint: { color: '#BE185D', fontSize: 12, lineHeight: 18, marginBottom: 12 },
  qrInput: { backgroundColor: '#FFF5F8', color: '#831843', borderRadius: 12, padding: 14, borderWidth: 1, borderColor: '#FCE7F3', fontSize: 13, height: 80, textAlignVertical: 'top', marginBottom: 12 },
  parseBtn: { backgroundColor: '#DB2777', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 8, shadowColor: '#DB2777', shadowOpacity: 0.3, shadowRadius: 6, elevation: 3 },
  parseBtnText: { color: '#fff', fontSize: 15, fontWeight: 'bold' },
  parsedAmount: { color: '#059669', fontSize: 16, fontWeight: '900', textAlign: 'center', marginBottom: 8 },

  // AI 辨識提示
  aiBox: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 24, alignItems: 'center', borderWidth: 1, borderColor: '#FCE7F3', marginBottom: 16, shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  aiBoxIcon: { fontSize: 36, marginBottom: 12 },
  aiBoxTitle: { color: '#831843', fontSize: 16, fontWeight: '800', marginBottom: 10, textAlign: 'center' },
  aiBoxDesc: { color: '#BE185D', fontSize: 13, textAlign: 'center', lineHeight: 22, marginBottom: 14 },
  aiBoxHint: { color: '#DB2777', fontSize: 12, textAlign: 'center', fontWeight: '500', marginBottom: 16 },
  uploadBtn: { backgroundColor: '#DB2777', borderRadius: 12, paddingVertical: 14, paddingHorizontal: 20, alignItems: 'center', shadowColor: '#DB2777', shadowOpacity: 0.3, shadowRadius: 6, elevation: 3 },
  uploadBtnText: { color: '#fff', fontSize: 15, fontWeight: 'bold' },

  // 通用表單
  formCard: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 20, borderWidth: 1, borderColor: '#FCE7F3', shadowColor: '#FDA4AF', shadowOpacity: 0.2, shadowRadius: 8, elevation: 3 },
  formTitle: { color: '#BE185D', fontSize: 13, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 20 },
  formField: { marginBottom: 18 },
  formFieldLabel: { color: '#9D174D', fontSize: 13, marginBottom: 10, fontWeight: '600' },
  amountRow: { flexDirection: 'row', alignItems: 'center', gap: 10, width: '100%' },
  amountInput: { flex: 1, minWidth: 0, color: '#831843', fontSize: 28, fontWeight: 'bold', backgroundColor: '#FFF5F8', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#FCE7F3' },
  currencyBtn: { backgroundColor: '#FCE7F3', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12 },
  currencyBtnText: { color: '#DB2777', fontSize: 15, fontWeight: '700' },
  textInput: { backgroundColor: '#FFF5F8', color: '#831843', borderRadius: 12, padding: 14, fontSize: 15, borderWidth: 1, borderColor: '#FCE7F3', minWidth: 0 },

  chipRow: { flexDirection: 'row', gap: 10, paddingVertical: 4 },
  chip: { backgroundColor: '#FFF0F5', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, borderWidth: 1, borderColor: '#FBCFE8' },
  chipActive: { backgroundColor: '#EC4899', borderColor: '#EC4899' },
  chipText: { color: '#BE185D', fontSize: 13, fontWeight: '500' },
  chipTextActive: { color: '#FFFFFF', fontWeight: '700' },

  categoryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  catBtn: { backgroundColor: '#FFF0F5', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, borderWidth: 1, borderColor: '#FBCFE8' },
  catBtnActive: { backgroundColor: '#EC4899', borderColor: '#EC4899' },
  catBtnText: { color: '#BE185D', fontSize: 14, fontWeight: '500' },
  catBtnTextActive: { color: '#FFFFFF', fontWeight: '700' },

  submitBtn: { backgroundColor: '#DB2777', borderRadius: 14, paddingVertical: 18, alignItems: 'center', marginTop: 12, shadowColor: '#DB2777', shadowOpacity: 0.4, shadowRadius: 12, elevation: 6 },
  submitBtnText: { color: '#fff', fontSize: 17, fontWeight: 'bold' },
});
