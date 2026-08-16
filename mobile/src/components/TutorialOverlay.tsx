import React, { useState, useEffect } from 'react';
import {
  Modal, View, Text, TouchableOpacity, StyleSheet, Dimensions, Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TUTORIAL_KEY = 'has_seen_tutorial_v1';

const STEPS = [
  {
    emoji: '💳',
    title: '歡迎使用信用卡大腦！',
    body: '接下來用 3 個步驟帶您快速認識這個 App，幫您把每一分錢的回饋都賺到最大！',
  },
  {
    emoji: '📊',
    title: '當月消費進度一目瞭然',
    body: '首頁儀表板顯示每張卡片的加碼額度使用量與進度條。\n橘色 = 快到上限，紅色 = 已封頂，要換卡刷！',
  },
  {
    emoji: '📷',
    title: 'OCR 掃描自動記帳',
    body: '拍下發票或帳單截圖，AI 會自動抓取金額並幫您選最划算的卡片記帳。\n支援台幣、日幣、美金等幣別自動換算！',
  },
  {
    emoji: '🎯',
    title: '決策推薦引擎',
    body: '消費前先查詢！輸入金額與消費通路（如 Apple Pay、外送平台），\n我們會即時推薦當下回饋率最高且額度未滿的卡片。',
  },
];

interface TutorialOverlayProps {
  show: boolean;
}

export default function TutorialOverlay({ show }: TutorialOverlayProps) {
  const [visible, setVisible] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (show) {
      AsyncStorage.getItem(TUTORIAL_KEY).then(val => {
        if (val !== 'true') {
          setVisible(true);
        }
      });
    }
  }, [show]);

  const handleNext = async () => {
    if (step < STEPS.length - 1) {
      setStep(s => s + 1);
    } else {
      await AsyncStorage.setItem(TUTORIAL_KEY, 'true');
      setVisible(false);
    }
  };

  const handleSkip = async () => {
    await AsyncStorage.setItem(TUTORIAL_KEY, 'true');
    setVisible(false);
  };

  const current = STEPS[step];

  return (
    <Modal visible={visible} transparent animationType="fade" statusBarTranslucent>
      {/* 半透明背景遮罩 */}
      <View style={styles.overlay}>
        {/* 教學卡片 */}
        <View style={styles.card}>
          {/* 步驟進度點 */}
          <View style={styles.dots}>
            {STEPS.map((_, i) => (
              <View key={i} style={[styles.dot, i === step && styles.dotActive]} />
            ))}
          </View>

          <Text style={styles.emoji}>{current.emoji}</Text>
          <Text style={styles.title}>{current.title}</Text>
          <Text style={styles.body}>{current.body}</Text>

          {/* 步驟 X / N */}
          <Text style={styles.stepLabel}>{step + 1} / {STEPS.length}</Text>

          <View style={styles.actions}>
            {step < STEPS.length - 1 ? (
              <>
                <TouchableOpacity style={styles.btnSkip} onPress={handleSkip}>
                  <Text style={styles.btnSkipText}>略過</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.btnNext} onPress={handleNext}>
                  <Text style={styles.btnNextText}>下一步 →</Text>
                </TouchableOpacity>
              </>
            ) : (
              <TouchableOpacity style={[styles.btnNext, styles.btnFinish]} onPress={handleNext}>
                <Text style={styles.btnNextText}>🚀 開始使用！</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </View>
    </Modal>
  );
}

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.75)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  card: {
    backgroundColor: '#FFF0F5',
    borderRadius: 24,
    padding: 28,
    width: Math.min(width - 48, 420),
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#FCE7F3',
    shadowColor: '#DB2777',
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 10,
  },
  dots: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 20,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FBCFE8',
  },
  dotActive: {
    backgroundColor: '#DB2777',
    width: 24,
  },
  emoji: {
    fontSize: 56,
    marginBottom: 16,
  },
  title: {
    color: '#831843',
    fontSize: 20,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: 12,
    letterSpacing: -0.3,
  },
  body: {
    color: '#9D174D',
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 8,
  },
  stepLabel: {
    color: '#BE185D',
    fontSize: 12,
    marginBottom: 24,
    marginTop: 4,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
  },
  btnSkip: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#F9A8D4',
    alignItems: 'center',
    backgroundColor: '#FFF',
  },
  btnSkipText: {
    color: '#DB2777',
    fontSize: 15,
    fontWeight: '600',
  },
  btnNext: {
    flex: 2,
    paddingVertical: 14,
    borderRadius: 12,
    backgroundColor: '#DB2777',
    alignItems: 'center',
  },
  btnFinish: {
    flex: 1,
    backgroundColor: '#BE185D',
  },
  btnNextText: {
    color: '#FFF0F5',
    fontSize: 15,
    fontWeight: '700',
  },
});
