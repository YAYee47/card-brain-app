import { apiClient } from './client';

export interface CardBenefit {
  id: number;
  channel_name: string;
  base_rate: number;
  bonus_rate: number;
  monthly_cap_ntd: number | null;
  effective_date: string;
}

export interface Card {
  id: number;
  bank_name: string;
  card_name: string;
  
  benefit_url?: string | null;
  last_synced_at?: string | null;
  benefits: CardBenefit[];
}

export interface UserCard {
  id: number;
  card_id: number;
  billing_cycle_date: number;
  is_active: boolean;
  card: Card;
}

/** 取得所有支援的信用卡列表（供 Onboarding 選卡用） */
export const fetchAllCards = async (): Promise<Card[]> => {
  const res = await apiClient.get<Card[]>('/cards');
  return res.data;
};

/** 取得使用者已選取的持有卡片清單 */
export const fetchUserCards = async (): Promise<UserCard[]> => {
  const res = await apiClient.get<UserCard[]>('/user-cards');
  return res.data;
};

/** Onboarding：新增使用者持有信用卡並設定帳單結帳日 */
export const addUserCard = async (card_id: number, billing_cycle_date: number): Promise<UserCard> => {
  const res = await apiClient.post<UserCard>('/user-cards', { card_id, billing_cycle_date });
  return res.data;
};

/** 新增自訂卡片並直接加入錢包 (包含 AI 爬蟲，給予較長 timeout) */
export const createCustomUserCard = async (data: { bank_name: string, card_name: string, benefit_url?: string, billing_cycle_date: number }): Promise<UserCard> => {
  const res = await apiClient.post<UserCard>('/user-cards/custom', data, { timeout: 30000 });
  return res.data;
};

/** 更新使用者信用卡設定（帳單結帳日或啟用狀態） */
export const updateUserCard = async (
  user_card_id: number,
  data: { billing_cycle_date?: number; is_active?: boolean }
): Promise<UserCard> => {
  const res = await apiClient.patch<UserCard>(`/user-cards/${user_card_id}`, data);
  return res.data;
};

/** 刪除(停用)使用者信用卡追蹤 */
export const deleteUserCard = async (user_card_id: number): Promise<void> => {
  await apiClient.delete(`/user-cards/${user_card_id}`);
};
