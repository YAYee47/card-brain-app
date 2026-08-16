import { apiClient } from './client';

export interface BenefitUsage {
  channel_name: string;
  base_rate: number;
  bonus_rate: number;
  monthly_cap_ntd: number | null;
  used_amount_ntd: number;
  remaining_cap_ntd: number | null;
  used_pct: number;
  is_warning: boolean;
  is_capped: boolean;
}

export interface CardDashboard {
  user_card_id: number;
  card_id: number;
  bank_name: string;
  card_name: string;
  
  billing_cycle_date: number;
  cycle_start_date: string;
  cycle_end_date: string;
  total_used_ntd: number;
  total_cashback_ntd: number;
  benefits: BenefitUsage[];
}

export interface DashboardSummary {
  total_cashback_ntd: number;
  total_spent_ntd: number;
  cards_count: number;
  cards: CardDashboard[];
  last_updated: string;
}

export const fetchDashboard = async (): Promise<DashboardSummary> => {
  const res = await apiClient.get<DashboardSummary>('/dashboard');
  return res.data;
};
