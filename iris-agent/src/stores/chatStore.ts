import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { mcpClient, ChatMessage } from '../lib/api';
import { storage, StoredConversation } from '../lib/storage';
import { useAppStore } from './appStore';

interface Message extends ChatMessage {
  isStreaming?: boolean;
  projectId?: string;
  conversationId?: string;
}

interface Conversation {
  id: string;
  projectId: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_activity: string;
  messageCount: number;
  lastMessage?: string;
  messages?: Message[];
}

interface ContextState {
  projectId: string | null;
  conversationId: string | null;
  files: string[];
  instructions: string;
}

interface ChatState {
  // Conversations
  conversations: Conversation[];
  activeConversation: Conversation | null;
  activeConversationId: string | null;
  
  // Messages
  messages: Record<string, Message[]>;
  streamingMessageId: string | null;
  isStreaming: boolean;
  
  // Context Management
  context: ContextState;
  contextUsage: number;
  maxContextSize: number;
  
  // UI State
  isTyping: boolean;
  suggestions: string[];
  autoScroll: boolean;
  
  // Chat Settings
  model: string;
  temperature: number;
  maxTokens: number;
  streamingEnabled: boolean;
  
  // Actions
  setActiveConversation: (conversationId: string | null) => void;
  createConversation: (projectId: string, title?: string) => string;
  updateConversation: (conversationId: string, updates: Partial<Conversation>) => void;
  deleteConversation: (conversationId: string) => void;
  
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (conversationId: string, messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (conversationId: string, messageId: string) => void;
  clearMessages: (conversationId: string) => void;
  
  setStreamingMessage: (messageId: string | null) => void;
  appendToMessage: (conversationId: string, messageId: string, content: string) => void;
  setIsStreaming: (streaming: boolean) => void;
  
  setContext: (context: Partial<ContextState>) => void;
  updateContextUsage: (usage: number) => void;
  
  setIsTyping: (typing: boolean) => void;
  sendMessage: (content: string, projectId?: string) => Promise<boolean>;
  loadConversations: () => void;
  loadMessages: (conversationId: string) => void;
  saveConversationsToStorage: () => void;
  importConversationsFromStorage: () => void;
  regenerateResponse: (conversationId: string, messageId: string) => Promise<boolean>;
  exportConversation: (conversationId: string) => string;
  getTokenUsage: (conversationId: string) => number;
  setSuggestions: (suggestions: string[]) => void;
  getCurrentMessages: () => Message[];
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial State
      conversations: [],
      activeConversation: null,
      activeConversationId: null,
      
      messages: {},
      streamingMessageId: null,
      isStreaming: false,
      
      context: {
        projectId: null,
        conversationId: null,
        files: [],
        instructions: '',
      },
      contextUsage: 0,
      maxContextSize: 128000, // 128k tokens
      
      isTyping: false,
      suggestions: [
        'Ayúdame a crear un componente React',
        'Explícame cómo funciona TypeScript',
        '¿Puedes revisar mi código?',
        'Dame sugerencias de optimización',
        'Crea una función para procesar datos',
      ],
      autoScroll: true,
      
      model: 'gpt-4',
      temperature: 0.7,
      maxTokens: 4000,
      streamingEnabled: true,
      
      // Actions
      setActiveConversation: (conversationId) => {
        const { conversations } = get();
        const conversation = conversations.find(c => c.id === conversationId) || null;
        set({ 
          activeConversation: conversation,
          activeConversationId: conversationId,
          context: {
            ...get().context,
            projectId: conversation?.projectId || null,
            conversationId: conversationId,
          }
        });
        
        // Load messages for this conversation
        if (conversationId) {
          get().loadMessages(conversationId);
        }
      },
      
      createConversation: (projectId, title) => {
        const conversationId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
        const conversationTitle = title || `Conversación ${new Date().toLocaleDateString()}`;
        
        const newConversation: Conversation = {
          id: conversationId,
          projectId,
          title: conversationTitle,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          last_activity: new Date().toISOString(),
          messageCount: 0,
        };
        
        set(state => ({
          conversations: [newConversation, ...state.conversations],
          activeConversation: newConversation,
          activeConversationId: conversationId,
          context: {
            ...state.context,
            projectId,
            conversationId,
          },
          messages: {
            ...state.messages,
            [conversationId]: [],
          }
        }));
        
        // Save to storage
        get().saveConversationsToStorage();
        
        return conversationId;
      },
      
      updateConversation: (conversationId, updates) => {
        set(state => ({
          conversations: state.conversations.map(c => 
            c.id === conversationId 
              ? { ...c, ...updates, updated_at: new Date().toISOString() }
              : c
          ),
          activeConversation: state.activeConversation?.id === conversationId
            ? { ...state.activeConversation, ...updates, updated_at: new Date().toISOString() }
            : state.activeConversation
        }));
        
        get().saveConversationsToStorage();
      },
      
      deleteConversation: (conversationId) => {
        set(state => ({
          conversations: state.conversations.filter(c => c.id !== conversationId),
          activeConversation: state.activeConversation?.id === conversationId ? null : state.activeConversation,
          activeConversationId: state.activeConversationId === conversationId ? null : state.activeConversationId,
          messages: Object.fromEntries(
            Object.entries(state.messages).filter(([id]) => id !== conversationId)
          ),
        }));
        
        storage.deleteConversation(conversationId);
      },
      
      addMessage: (conversationId, messageData) => {
        const message: Message = {
          ...messageData,
          id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
          timestamp: new Date().toISOString(),
          conversationId,
        };
        
        set(state => ({
          messages: {
            ...state.messages,
            [conversationId]: [...(state.messages[conversationId] || []), message],
          }
        }));
        
        // Update conversation
        get().updateConversation(conversationId, {
          last_activity: new Date().toISOString(),
          messageCount: (get().messages[conversationId]?.length || 0) + 1,
        });
        
        // Save to storage
        get().saveConversationsToStorage();
      },
      
      updateMessage: (conversationId, messageId, updates) => {
        set(state => ({
          messages: {
            ...state.messages,
            [conversationId]: (state.messages[conversationId] || []).map(m =>
              m.id === messageId ? { ...m, ...updates } : m
            ),
          }
        }));
      },
      
      deleteMessage: (conversationId, messageId) => {
        set(state => ({
          messages: {
            ...state.messages,
            [conversationId]: (state.messages[conversationId] || []).filter(m => m.id !== messageId),
          }
        }));
        
        get().saveConversationsToStorage();
      },
      
      clearMessages: (conversationId) => {
        set(state => ({
          messages: {
            ...state.messages,
            [conversationId]: [],
          }
        }));
        
        get().updateConversation(conversationId, { messageCount: 0 });
        get().saveConversationsToStorage();
      },
      
      setStreamingMessage: (messageId) => {
        set({ streamingMessageId: messageId });
      },
      
      appendToMessage: (conversationId, messageId, content) => {
        set(state => ({
          messages: {
            ...state.messages,
            [conversationId]: (state.messages[conversationId] || []).map(m =>
              m.id === messageId ? { ...m, content: m.content + content } : m
            ),
          }
        }));
      },
      
      setIsStreaming: (streaming) => {
        set({ isStreaming: streaming });
        if (!streaming) {
          set({ streamingMessageId: null });
        }
      },
      
      setContext: (contextUpdates) => {
        set(state => ({
          context: { ...state.context, ...contextUpdates }
        }));
      },
      
      updateContextUsage: (usage) => {
        set({ contextUsage: usage });
      },
      
      setIsTyping: (typing) => {
        set({ isTyping: typing });
      },
      
      sendMessage: async (content, projectId) => {
        const { activeConversationId, model, temperature, maxTokens, streamingEnabled } = get();
        const appStore = useAppStore.getState();
        
        // Get conversation and project ID
        const conversationId = activeConversationId || get().createConversation(projectId || 'default');
        const conversation = get().conversations.find(c => c.id === conversationId);
        const finalProjectId = projectId || conversation?.projectId || 'default';
        
        // Add user message
        const userMessage: Omit<Message, 'id' | 'timestamp'> = {
          role: 'user',
          content,
          projectId: finalProjectId,
          conversationId,
        };
        
        get().addMessage(conversationId, userMessage);
        
        // Create streaming assistant message
        const assistantMessageId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
        const assistantMessage: Omit<Message, 'id' | 'timestamp'> = {
          role: 'assistant',
          content: '',
          isStreaming: true,
          projectId: finalProjectId,
          conversationId,
        };
        
        get().addMessage(conversationId, assistantMessage);
        get().setStreamingMessage(assistantMessageId);
        get().setIsStreaming(true);
        get().setIsTyping(true);
        
        try {
          if (streamingEnabled) {
            // Use streaming API
            const result = await mcpClient.sendMessageStream(
              content,
              finalProjectId,
              conversationId,
              (chunk) => {
                get().appendToMessage(conversationId, assistantMessageId, chunk);
              }
            );
            
            if (result.success) {
              // Finalize streaming message
              get().updateMessage(conversationId, assistantMessageId, {
                isStreaming: false,
              });
              
              appStore.addNotification({
                type: 'info',
                title: 'Respuesta completada',
                message: 'La IA ha terminado de procesar tu mensaje',
                isRead: true,
              });
              
              return true;
            } else {
              // Handle streaming error
              get().updateMessage(conversationId, assistantMessageId, {
                content: 'Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta nuevamente.',
                isStreaming: false,
              });
              
              appStore.addNotification({
                type: 'error',
                title: 'Error en el chat',
                message: result.error || 'No se pudo procesar el mensaje',
                isRead: false,
              });
              
              return false;
            }
          } else {
            // Use regular API
            const response = await mcpClient.sendMessage(content, finalProjectId, conversationId);
            
            if (response && response.message) {
              get().updateMessage(conversationId, assistantMessageId, {
                content: response.message.content,
                isStreaming: false,
              });
              return true;
            } else {
              get().updateMessage(conversationId, assistantMessageId, {
                content: 'Lo siento, no pude procesar tu mensaje. Por favor, intenta nuevamente.',
                isStreaming: false,
              });
              return false;
            }
          }
        } catch (error) {
          console.error('Failed to send message:', error);
          
          get().updateMessage(conversationId, assistantMessageId, {
            content: 'Error de conexión. Verifica que el MCP Server esté funcionando.',
            isStreaming: false,
          });
          
          appStore.addNotification({
            type: 'error',
            title: 'Error de conexión',
            message: 'No se puede conectar con el servidor de chat',
            isRead: false,
          });
          
          return false;
        } finally {
          get().setIsStreaming(false);
          get().setIsTyping(false);
        }
      },
      
      loadConversations: () => {
        const storedConversations = storage.loadConversations();
        const conversations: Conversation[] = storedConversations.map(stored => ({
          id: stored.id,
          projectId: stored.projectId,
          title: stored.title,
          created_at: stored.created_at,
          updated_at: stored.updated_at,
          last_activity: stored.last_activity,
          messageCount: stored.messages.length,
          lastMessage: stored.messages.length > 0 ? stored.messages[stored.messages.length - 1].content : 'Sin mensajes',
          messages: stored.messages,
        }));
        
        set({ conversations });
      },
      
      loadMessages: (conversationId) => {
        const storedConversations = storage.loadConversations();
        const conversation = storedConversations.find(c => c.id === conversationId);
        
        if (conversation) {
          const messages: Message[] = conversation.messages.map(msg => ({
            ...msg,
            conversationId,
            projectId: conversation.projectId,
          }));
          
          set(state => ({
            messages: {
              ...state.messages,
              [conversationId]: messages,
            }
          }));
        }
      },
      
      saveConversationsToStorage: () => {
        const { conversations, messages } = get();
        const storedConversations: StoredConversation[] = conversations.map(conv => ({
          ...conv,
          messages: messages[conv.id] || [],
        }));
        
        // Save each conversation individually for better performance
        storedConversations.forEach(conv => {
          storage.saveConversation(conv);
        });
      },
      
      importConversationsFromStorage: () => {
        get().loadConversations();
      },
      
      regenerateResponse: async (conversationId, messageId) => {
        const { messages, activeConversationId } = get();
        const conversationMessages = messages[conversationId] || [];
        const messageIndex = conversationMessages.findIndex(m => m.id === messageId);
        
        if (messageIndex <= 0) return false;
        
        // Find the user message that prompted this response
        const userMessage = conversationMessages[messageIndex - 1];
        if (userMessage.role !== 'user') return false;
        
        // Remove the assistant message
        get().deleteMessage(conversationId, messageId);
        
        // Send the user message again
        return await get().sendMessage(userMessage.content, userMessage.projectId);
      },
      
      exportConversation: (conversationId) => {
        const { conversations, messages } = get();
        const conversation = conversations.find(c => c.id === conversationId);
        const conversationMessages = messages[conversationId] || [];
        
        if (!conversation) return '';
        
        return JSON.stringify({
          conversation,
          messages: conversationMessages,
          exportDate: new Date().toISOString(),
        }, null, 2);
      },
      
      getTokenUsage: (conversationId) => {
        const messages = get().messages[conversationId] || [];
        return messages.reduce((total, msg) => total + (msg.tokens || 0), 0);
      },
      
      setSuggestions: (suggestions) => {
        set({ suggestions });
      },
      
      getCurrentMessages: () => {
        const { activeConversationId, messages } = get();
        return activeConversationId ? messages[activeConversationId] || [] : [];
      },
    }),
    {
      name: 'iris-chat-store',
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        autoScroll: state.autoScroll,
        model: state.model,
        temperature: state.temperature,
        maxTokens: state.maxTokens,
        streamingEnabled: state.streamingEnabled,
      }),
    }
  )
);

// Load conversations from storage on initialization
if (typeof window !== 'undefined') {
  setTimeout(() => {
    const store = useChatStore.getState();
    store.loadConversations();
  }, 1000);
}