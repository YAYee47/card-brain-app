import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { View, Text, Platform } from 'react-native';

function CustomHeaderTitle({ icon, title, tintColor }: { icon: keyof typeof Ionicons.glyphMap; title: string; tintColor?: string }) {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
      <Ionicons name={icon} size={22} color={tintColor || '#831843'} />
      <Text style={{ fontSize: 18, fontWeight: '700', color: tintColor || '#831843' }}>{title}</Text>
    </View>
  );
}

/**
 * 底部 Tab 選單佈局 Layout
 */
export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarStyle: {
          backgroundColor: '#FFF0F5',
          borderTopColor: '#FCE7F3',
          paddingTop: 8,
          paddingBottom: Platform.OS === 'ios' ? 24 : 12,
          paddingHorizontal: 12,
          minHeight: Platform.OS === 'ios' ? 88 : 70,
        },
        tabBarActiveTintColor: '#DB2777', // Deep pink focus
        tabBarInactiveTintColor: '#F9A8D4', // Light pink inactive
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          paddingBottom: 4,
        },
        tabBarItemStyle: {
          flexDirection: 'column',
          justifyContent: 'center',
          paddingHorizontal: 4,
        },
        tabBarIconStyle: {
          marginBottom: 2,
        },
        headerStyle: {
          backgroundColor: '#FFF0F5',
        },
        headerTintColor: '#831843',
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: '額度儀表板',
          headerTitle: ({ tintColor }) => <CustomHeaderTitle icon="pie-chart" title="額度儀表板" tintColor={tintColor} />,
          tabBarIcon: ({ color, size }) => <Ionicons name="pie-chart" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="recommend"
        options={{
          title: '決策推薦',
          headerTitle: ({ tintColor }) => <CustomHeaderTitle icon="bulb" title="消費推薦試算" tintColor={tintColor} />,
          tabBarIcon: ({ color, size }) => <Ionicons name="bulb" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="scan"
        options={{
          title: '記帳分析',
          headerTitle: ({ tintColor }) => <CustomHeaderTitle icon="wallet" title="記帳與消費分析" tintColor={tintColor} />,
          tabBarIcon: ({ color, size }) => <Ionicons name="wallet" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="cards"
        options={{
          title: '名下卡片',
          headerTitle: ({ tintColor }) => <CustomHeaderTitle icon="card" title="信用卡權益管理" tintColor={tintColor} />,
          tabBarIcon: ({ color, size }) => <Ionicons name="card" size={size} color={color} />,
        }}
      />
      <Tabs.Screen
        name="tutorial"
        options={{
          title: '使用教學',
          headerTitle: ({ tintColor }) => <CustomHeaderTitle icon="book" title="App 使用秘笈" tintColor={tintColor} />,
          tabBarIcon: ({ color, size }) => <Ionicons name="book" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
