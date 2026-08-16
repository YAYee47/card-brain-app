import axios from 'axios';

// 後端 API 基礎 URL 配置
// 優先使用環境變數設定的 URL，若無則預設指向 Render 雲端後台
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://card-brain-app.onrender.com/api/v1';

import AsyncStorage from '@react-native-async-storage/async-storage';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000, // 給予 45 秒以容納 Render 免費版的冷啟動喚醒時間
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加 Request Interceptor 來自動附帶 Device-UUID
apiClient.interceptors.request.use(async (config) => {
  try {
    const deviceUuid = await AsyncStorage.getItem('device_uuid');
    if (deviceUuid) {
      config.headers['X-Device-UUID'] = deviceUuid;
    }
  } catch (error) {
    console.error('讀取 device_uuid 發生錯誤:', error);
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

/**
 * 測試後端健康檢查 API 端點
 */
export const checkBackendHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('後端連線失敗:', error);
    throw error;
  }
};
