import { apiClient } from './client';
import type { UsageStats, UsageEvent } from '../types';

export const usageApi = {
  async getCurrentPeriod(): Promise<UsageStats> {
    return apiClient.get<UsageStats>('/v1/usage/current-period');
  },

  async getHistory(limit: number = 50): Promise<UsageEvent[]> {
    // Note: This endpoint might not exist yet in backend
    // Using mock data for now
    return mockHistory.slice(0, limit);
  },
};

// Mock data for development
const mockHistory: UsageEvent[] = [
  { id: '1', audio_seconds: 45, success: true, created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), context: 'Slack' },
  { id: '2', audio_seconds: 120, success: true, created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), context: 'Email' },
  { id: '3', audio_seconds: 30, success: true, created_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), context: 'Notion' },
  { id: '4', audio_seconds: 180, success: true, created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), context: 'Meeting notes' },
  { id: '5', audio_seconds: 15, success: true, created_at: new Date(Date.now() - 1000 * 60 * 60 * 26).toISOString(), context: 'Slack' },
];
