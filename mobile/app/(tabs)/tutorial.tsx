import React, { useState } from 'react';
import {
  StyleSheet, Text, View, ScrollView,
  TouchableOpacity, ActivityIndicator, Alert, SafeAreaView,
} from 'react-native';
import { triggerCrawl } from '../../src/api/alerts';

export default function TutorialScreen() {
  const [crawling, setCrawling] = useState(false);

  const handleCrawl = async () => {
    setCrawling(true);
    try {
      const result = await triggerCrawl();
      Alert.alert(
        '爬蟲執行完成',
        `檢查了 ${result.checked} 筆權益\n更新了 ${result.updated} 筆資料\n產生了 ${result.alerts_created} 則權益警報\n產生了 ${result.quota_alerts} 則額度警報`
      );
    } catch (e: any) {
      Alert.alert('執行失敗', '無法啟動爬蟲任務');
    } finally {
      setCrawling(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        
        <View style={styles.tutorialBox}>
          <Text style={styles.tutorialTitle}>✨ App 使用秘笈 ✨</Text>
          
          <View style={styles.tutorialStep}>
            <Text style={styles.tutorialIcon}>📸</Text>
            <View style={styles.tutorialTextContainer}>
              <Text style={styles.tutorialStepTitle}>1. 掃描消費</Text>
              <Text style={styles.tutorialStepDesc}>切換至「相機記帳」頁面，拍攝您的結帳畫面，AI 將自動為您挑選最適合的信用卡。</Text>
            </View>
          </View>

          <View style={styles.tutorialStep}>
            <Text style={styles.tutorialIcon}>🔍</Text>
            <View style={styles.tutorialTextContainer}>
              <Text style={styles.tutorialStepTitle}>2. 權益切換</Text>
              <Text style={styles.tutorialStepDesc}>點擊「名下卡片」列表中的「查看權益」，可檢視該卡的詳細回饋通路與限時活動。</Text>
            </View>
          </View>

          <View style={styles.tutorialStep}>
            <Text style={styles.tutorialIcon}>📅</Text>
            <View style={styles.tutorialTextContainer}>
              <Text style={styles.tutorialStepTitle}>3. 結帳日自動計算</Text>
              <Text style={styles.tutorialStepDesc}>系統已記錄您的結帳日，每月會自動重新計算各卡的加碼額度消耗狀況！</Text>
            </View>
          </View>
        </View>

        {/* 開發測試工具區 (保留給手動爬蟲) */}
        <View style={styles.devTools}>
          <Text style={styles.devToolsTitle}>🧪 測試與自動化</Text>
          <TouchableOpacity
            style={[styles.crawlBtn, crawling && { opacity: 0.6 }]}
            onPress={handleCrawl}
            disabled={crawling}
          >
            {crawling ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.crawlBtnText}>手動觸發權益爬蟲與額度掃描</Text>
            )}
          </TouchableOpacity>
          <Text style={styles.devToolsDesc}>
            正常情況下，系統會在每月 1 號 00:05 自動執行爬蟲，並於每日 09:00 執行額度掃描。
            此按鈕供展示與測試用途。
          </Text>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  content: { padding: 16, paddingBottom: 40 },
  
  tutorialBox: { backgroundColor: '#FFFFFF', borderRadius: 24, padding: 24, shadowColor: '#EC4899', shadowOpacity: 0.15, shadowRadius: 20, elevation: 5, borderWidth: 1, borderColor: '#FCE7F3', marginBottom: 24 },
  tutorialTitle: { color: '#9D174D', fontSize: 20, fontWeight: '800', textAlign: 'center', marginBottom: 24, letterSpacing: 1 },
  tutorialStep: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 20, backgroundColor: '#FFF0F5', padding: 16, borderRadius: 16, borderWidth: 1, borderColor: '#FBCFE8' },
  tutorialIcon: { fontSize: 24, marginRight: 16, marginTop: 2 },
  tutorialTextContainer: { flex: 1 },
  tutorialStepTitle: { color: '#BE185D', fontSize: 16, fontWeight: '700', marginBottom: 6 },
  tutorialStepDesc: { color: '#831843', fontSize: 14, lineHeight: 20 },

  devTools: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#FBCFE8', borderStyle: 'dashed', shadowColor: '#FDA4AF', shadowOpacity: 0.1, shadowRadius: 8, elevation: 2 },
  devToolsTitle: { color: '#831843', fontSize: 14, fontWeight: '800', marginBottom: 12 },
  crawlBtn: { backgroundColor: '#EC4899', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginBottom: 10, shadowColor: '#EC4899', shadowOpacity: 0.3, shadowRadius: 6, elevation: 3 },
  crawlBtnText: { color: '#fff', fontSize: 14, fontWeight: 'bold' },
  devToolsDesc: { color: '#BE185D', fontSize: 12, lineHeight: 18 },
});
