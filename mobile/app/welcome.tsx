import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, SafeAreaView, ActivityIndicator, ScrollView } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useRouter } from 'expo-router';
import { apiClient } from '../src/api/client';

export default function WelcomeScreen() {
  const [nickname, setNickname] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [existingUsers, setExistingUsers] = useState<any[]>([]);
  const router = useRouter();
  const passwordInputRef = useRef<TextInput>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await apiClient.get('/users');
        setExistingUsers(res.data);
      } catch (e) {
        console.error('無法載入已儲存身分', e);
      }
    };
    fetchUsers();
  }, []);

  // 產生簡單的 UUID
  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  const handleSelectExisting = (user: any) => {
    setNickname(user.nickname);
    setPassword('');
    Alert.alert('請輸入密碼', `請在下方輸入 ${user.nickname} 的密碼以登入`);
    passwordInputRef.current?.focus();
  };

  const handleLogin = async (isGuest: boolean) => {
    if (!isGuest) {
      if (!nickname.trim()) {
        Alert.alert('提示', '請輸入您的專屬暱稱！');
        return;
      }
      if (!password.trim() || password.length < 4 || password.length > 20) {
        Alert.alert('提示', '請設定或輸入密碼 (4~20碼)！');
        return;
      }
    }

    setLoading(true);
    try {
      // 如果是訪客，產生全新的 guest UUID。如果是註冊/登入，產生新的 UUID 用來綁定設備
      const uuid = isGuest ? `guest-${generateUUID()}` : generateUUID();
      const name = isGuest ? `訪客 ${uuid.substring(0, 5)}` : nickname.trim();

      const response = await apiClient.post('/users/auth', {
        device_uuid: uuid,
        nickname: name,
        password: isGuest ? null : password,
        is_guest: isGuest
      });

      const user = response.data;
      
      // 儲存至 AsyncStorage，包含 is_guest 標記以便後續退出
      await AsyncStorage.setItem('device_uuid', user.device_uuid);
      await AsyncStorage.setItem('nickname', user.nickname);
      await AsyncStorage.setItem('is_guest', user.is_guest ? 'true' : 'false');

      router.replace('/');
    } catch (error: any) {
      console.error(error);
      if (error.response && error.response.status === 401) {
        Alert.alert('登入失敗', error.response.data.detail || '密碼錯誤');
      } else {
        Alert.alert('錯誤', '無法連線至伺服器，請確認網路或後端狀態。');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>歡迎使用 Card Brain</Text>
        <Text style={styles.subtitle}>您的智慧信用卡記帳管家</Text>

        {existingUsers.length > 0 && (
          <View style={styles.card}>
            <Text style={styles.label}>已存在的帳號</Text>
            {existingUsers.map(user => (
              <TouchableOpacity 
                key={user.id}
                style={[styles.btn, styles.existingBtn]} 
                onPress={() => handleSelectExisting(user)}
                disabled={loading}
              >
                <Text style={styles.existingBtnText}>登入 {user.nickname}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        <View style={styles.card}>
          <Text style={styles.label}>登入或建立新帳號</Text>
          <TextInput
            style={styles.input}
            placeholder="請輸入暱稱 (例如: YAYee)"
            value={nickname}
            onChangeText={setNickname}
            placeholderTextColor="#FBCFE8"
          />
          <TextInput
            ref={passwordInputRef}
            style={styles.input}
            placeholder="請輸入密碼 (4~20碼)"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            placeholderTextColor="#FBCFE8"
          />
          <TouchableOpacity 
            style={[styles.btn, styles.primaryBtn]} 
            onPress={() => handleLogin(false)}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="#FFF" /> : <Text style={styles.primaryBtnText}>進入我的錢包</Text>}
          </TouchableOpacity>
        </View>

        <View style={styles.divider}>
          <View style={styles.line} />
          <Text style={styles.orText}>或</Text>
          <View style={styles.line} />
        </View>

        <View style={styles.card}>
          <Text style={styles.label}>無痕試用模式</Text>
          <Text style={styles.desc}>不需輸入資料，可隨意測試記帳與新增卡片。離開時資料將自動銷毀，不留痕跡。</Text>
          <TouchableOpacity 
            style={[styles.btn, styles.secondaryBtn]} 
            onPress={() => handleLogin(true)}
            disabled={loading}
          >
             <Text style={styles.secondaryBtnText}>以訪客身分試用</Text>
          </TouchableOpacity>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF0F5' },
  content: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  title: { fontSize: 28, fontWeight: '800', color: '#831843', textAlign: 'center', marginBottom: 8 },
  subtitle: { fontSize: 16, color: '#BE185D', textAlign: 'center', marginBottom: 40 },
  card: { backgroundColor: '#FFFFFF', padding: 24, borderRadius: 20, shadowColor: '#FDA4AF', shadowOpacity: 0.3, shadowRadius: 10, elevation: 5, marginBottom: 20 },
  label: { fontSize: 18, fontWeight: 'bold', color: '#9D174D', marginBottom: 12 },
  desc: { fontSize: 14, color: '#BE185D', marginBottom: 16, lineHeight: 20 },
  input: { backgroundColor: '#FFF5F8', borderWidth: 1, borderColor: '#FBCFE8', borderRadius: 12, padding: 14, fontSize: 16, color: '#831843', marginBottom: 16 },
  btn: { padding: 16, borderRadius: 12, alignItems: 'center' },
  primaryBtn: { backgroundColor: '#EC4899', shadowColor: '#EC4899', shadowOpacity: 0.4, shadowRadius: 8, elevation: 4 },
  primaryBtnText: { color: '#FFFFFF', fontSize: 16, fontWeight: 'bold' },
  secondaryBtn: { backgroundColor: '#FCE7F3', borderWidth: 1, borderColor: '#FBCFE8' },
  secondaryBtnText: { color: '#DB2777', fontSize: 16, fontWeight: 'bold' },
  existingBtn: { backgroundColor: '#FDF2F8', borderWidth: 1, borderColor: '#F472B6', marginBottom: 10 },
  existingBtnText: { color: '#831843', fontSize: 16, fontWeight: 'bold' },
  divider: { flexDirection: 'row', alignItems: 'center', marginVertical: 10 },
  line: { flex: 1, height: 1, backgroundColor: '#FBCFE8' },
  orText: { marginHorizontal: 16, color: '#F472B6', fontWeight: 'bold' }
});
