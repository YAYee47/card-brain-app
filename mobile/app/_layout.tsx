import React, { useEffect, useState } from 'react';
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { View, StyleSheet, Platform, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * 根佈局 Root Layout
 */
export default function RootLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const uuid = await AsyncStorage.getItem('device_uuid');
        setIsAuthenticated(!!uuid);
      } catch (e) {
        setIsAuthenticated(false);
      }
    };
    checkAuth();
  }, []);

  useEffect(() => {
    const checkAuthAndRoute = async () => {
      try {
        const uuid = await AsyncStorage.getItem('device_uuid');
        const isAuth = !!uuid;
        setIsAuthenticated(isAuth);

        const inAuthGroup = segments[0] === 'welcome';
        const inTabsGroup = segments[0] === '(tabs)';

        if (!isAuth && !inAuthGroup) {
          router.replace('/welcome');
        } else if (isAuth && inAuthGroup) {
          router.replace('/'); // 登入狀態下，如果還在 welcome 頁，導向首頁
        }
      } catch (e) {
        setIsAuthenticated(false);
      }
    };
    
    checkAuthAndRoute();
  }, [segments]);

  if (isAuthenticated === null) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#EC4899" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: {
            backgroundColor: '#FFF0F5',
          },
          headerTintColor: '#831843',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="welcome" options={{ headerShown: false, animation: 'fade' }} />
      </Stack>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF0F5',
    ...Platform.select({
      web: {
        maxWidth: 480,
        width: '100%',
        marginHorizontal: 'auto',
        shadowColor: '#000',
        shadowOpacity: 0.5,
        shadowRadius: 20,
        elevation: 10,
      },
    }),
  },
});

