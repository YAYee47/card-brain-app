import { apiClient } from './client';

export interface AppAlert {
  id: number;
  alert_type: string;
  severity: string;
  card_id: number | null;
  user_card_id: number | null;
  title: string;
  body: string;
  diff_detail: string | null;
  is_read: boolean;
  created_at: string;
}

export interface CrawlResult {
  status: string;
  checked: number;
  updated: number;
  alerts_created: number;
  quota_alerts: number;
  run_at: string;
}

/** 取得所有警報列表 */
export const fetchAlerts = async (unread_only = false, limit = 50): Promise<AppAlert[]> => {
  const res = await apiClient.get<AppAlert[]>('/alerts', { params: { unread_only, limit } });
  return res.data;
};

/** 將單筆警報標記為已讀 */
export const markAlertRead = async (id: number): Promise<void> => {
  await apiClient.post(`/alerts/${id}/read`);
};

/** 全部標記為已讀 */
export const markAllAlertsRead = async (): Promise<void> => {
  await apiClient.post('/alerts/read-all');
};

/** 手動觸發爬蟲與差異比對 (展示/除錯用途) */
export const triggerCrawl = async (): Promise<CrawlResult> => {
  const res = await apiClient.post<CrawlResult>('/crawl');
  return res.data;
};
