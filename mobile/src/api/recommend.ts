import { apiClient } from './client';

export interface RecommendedCard {
  user_card_id: number;
  card_id: number;
  bank_name: string;
  card_name: string;
  
  billing_cycle_date: number;
  channel_name: string;
  base_rate: number;
  bonus_rate: number;
  monthly_cap_ntd: number | null;
  used_amount_ntd: number;
  remaining_cap_ntd: number | null;
  estimated_base_cashback: number;
  estimated_bonus_cashback: number;
  estimated_total_cashback: number;
  is_capped: boolean;
  score: number;
}

export interface RecommendResponse {
  amount: number;
  channel_name: string;
  results: RecommendedCard[];
  top_card: RecommendedCard | null;
}

/** 取得系統支援的支付通道清單 */
export const fetchChannels = async (): Promise<string[]> => {
  const res = await apiClient.get<string[]>('/recommend/channels');
  return res.data;
};

/** 提交消費金額與通道，取得推薦排序結果 */
export const fetchRecommendations = async (
  amount: number,
  channel_name: string,
): Promise<RecommendResponse> => {
  const res = await apiClient.post<RecommendResponse>('/recommend', {
    amount,
    channel_name,
  });
  return res.data;
};
