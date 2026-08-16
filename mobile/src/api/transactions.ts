import { apiClient } from './client';

export interface OcrResult {
  amount: number | null;
  currency: string;
  merchant_name: string | null;
  transaction_date: string | null;
  channel_name: string | null;
  category: string | null;
  confidence: string;
  raw_text: string | null;
}

export interface TransactionCreate {
  user_card_id: number;
  channel_name: string;
  category: string;
  merchant_name?: string;
  original_amount: number;
  currency: string;
  source_type: string;
  transacted_at?: string;
}

export interface TransactionOut {
  id: number;
  user_card_id: number;
  channel_name: string;
  category: string;
  merchant_name: string | null;
  original_amount: number;
  currency: string;
  ntd_amount: number;
  exchange_rate: number;
  earned_cashback_ntd: number;
  source_type: string;
  transacted_at: string;
}

/** 上傳收據/截圖圖片給 AI 辨識 */
export const uploadImageForOcr = async (
  imageUri: string,
  type: 'receipt' | 'screenshot',
): Promise<OcrResult> => {
  const formData = new FormData();
  const filename = imageUri.split('/').pop() ?? 'image.jpg';
  formData.append('file', {
    uri: imageUri,
    name: filename,
    type: 'image/jpeg',
  } as any);

  const endpoint = type === 'receipt' ? '/ocr/receipt' : '/ocr/screenshot';
  const res = await apiClient.post<OcrResult>(endpoint, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  });
  return res.data;
};

/** 新增交易記帳 */
export const createTransaction = async (payload: TransactionCreate): Promise<TransactionOut> => {
  const res = await apiClient.post<TransactionOut>('/transactions', payload);
  return res.data;
};

/** 取得交易明細列表 */
export const fetchTransactions = async (
  user_card_id?: number,
  start_date?: string,
  end_date?: string
): Promise<TransactionOut[]> => {
  const params: any = {};
  if (user_card_id) params.user_card_id = user_card_id;
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  
  const res = await apiClient.get<TransactionOut[]>('/transactions', { params });
  return res.data;
};
