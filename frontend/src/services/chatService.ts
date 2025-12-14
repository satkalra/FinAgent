import api from './api';
import { ChatResponse, Conversation, Message } from '@/types';

export const chatService = {
  async sendMessage(message: string, conversationId?: number): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat/send', {
      message,
      conversation_id: conversationId,
      stream: false,
    });
    return response.data;
  },

  async getConversations(): Promise<Conversation[]> {
    const response = await api.get<Conversation[]>('/conversations');
    return response.data;
  },

  async getConversation(id: number): Promise<Conversation> {
    const response = await api.get<Conversation>(`/conversations/${id}`);
    return response.data;
  },

  async getMessages(conversationId: number): Promise<Message[]> {
    const response = await api.get<Message[]>(`/conversations/${conversationId}/messages`);
    return response.data;
  },

  async createConversation(title: string): Promise<Conversation> {
    const response = await api.post<Conversation>('/conversations', { title });
    return response.data;
  },

  async deleteConversation(id: number): Promise<void> {
    await api.delete(`/conversations/${id}`);
  },
};
