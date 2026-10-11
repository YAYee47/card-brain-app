import React from 'react';
import {
  StyleSheet, Text, View, ScrollView, SafeAreaView,
} from 'react-native';

export default function TutorialScreen() {
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
});
