import React from 'react';
import { Modal, View, Text, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';

interface DatePickerModalProps {
  visible: boolean;
  value: string;
  onChange: (dateStr: string) => void;
  onClose: () => void;
}

export default function DatePickerModal({ visible, value, onChange, onClose }: DatePickerModalProps) {
  if (!visible) return null;

  const dateObj = value ? new Date(value) : new Date();

  if (Platform.OS === 'ios') {
    return (
      <Modal visible={visible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={[styles.modalBox, { padding: 0 }]}>
            <View style={styles.header}>
              <Text style={styles.headerTitle}>選擇刷卡日期</Text>
              <TouchableOpacity onPress={onClose}>
                <Text style={styles.headerBtn}>完成</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.pickerContainer}>
              <DateTimePicker
                value={dateObj}
                mode="date"
                display="inline"
                themeVariant="light"
                onChange={(event, date) => {
                  if (date) {
                    onChange(date.toISOString().split('T')[0]);
                  }
                }}
              />
            </View>
          </View>
        </View>
      </Modal>
    );
  }

  // Android implementation
  return (
    <DateTimePicker
      value={dateObj}
      mode="date"
      display="default"
      onChange={(event, date) => {
        onClose();
        if (event.type === 'set' && date) {
          onChange(date.toISOString().split('T')[0]);
        }
      }}
    />
  );
}

const styles = StyleSheet.create({
  modalOverlay: { flex: 1, backgroundColor: 'rgba(252, 231, 243, 0.8)', justifyContent: 'flex-end' },
  modalBox: { backgroundColor: '#FFFFFF', borderTopLeftRadius: 32, borderTopRightRadius: 32, paddingBottom: 48, shadowColor: '#FDA4AF', shadowOpacity: 0.3, shadowRadius: 15, elevation: 10, borderWidth: 1, borderColor: '#FCE7F3' },
  header: { flexDirection: 'row', justifyContent: 'space-between', padding: 16, backgroundColor: '#FDF2F8', borderTopLeftRadius: 20, borderTopRightRadius: 20, width: '100%' },
  headerTitle: { fontSize: 16, fontWeight: 'bold', color: '#831843' },
  headerBtn: { fontSize: 16, fontWeight: 'bold', color: '#BE185D' },
  pickerContainer: { backgroundColor: '#fff', padding: 16, borderBottomLeftRadius: 20, borderBottomRightRadius: 20, width: '100%', alignItems: 'center' }
});
