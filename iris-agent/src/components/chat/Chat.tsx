import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';
import { useProjectStore } from '../../stores/projectStore';
import { 
  Send, 
  Plus, 
  Search, 
  MoreVertical, 
  Paperclip,
  Mic,
  Square,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RotateCcw,
  Settings,
  ChevronDown,
  Sparkles,
  MessageCircle
} from 'lucide-react';
import { cn } from '../../lib/utils';

const Chat: React.FC = () => {
  const { 
    conversations, 
    activeConversation, 
    activeConversationId,
    messages,
    isStreaming,
    streamingMessageId,
    suggestions,
    setActiveConversation,
    createConversation,
    addMessage,
    appendToMessage,
    setStreamingMessage,
    setIsStreaming,
    setSuggestions,
    getCurrentMessages
  } = useChatStore();

  const { projects } = useProjectStore();
  
  const [inputValue, setInputValue] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [conversationFilter, setConversationFilter] = useState<'all' | 'recent' | 'project'>('all');
  const [selectedProject, setSelectedProject] = useState<string>('all');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, activeConversationId]);

  // Mock streaming function
  const simulateStreamingResponse = async (userMessage: string, conversationId: string) => {
    const assistantMessageId = Date.now().toString();
    
    // Add initial assistant message
    addMessage(conversationId, {
      role: 'assistant',
      content: 'Escribiendo...',
      isStreaming: true,
    });

    setStreamingMessage(assistantMessageId);
    setIsStreaming(true);

    // Simulate streaming response
    const responses = [
      '¡Hola! Me complace ayudarte con tu consulta.',
      'He analizado tu mensaje y tengo algunas sugerencias interesantes.',
      'Para resolver esto de manera óptima, te recomiendo:',
      '',
      '1. **Primera opción**: Implementar una solución modular',
      '2. **Segunda opción**: Usar un enfoque más directo',
      '3. **Tercera opción**: Considerar una arquitectura alternativa',
      '',
      '¿Te gustaría que profundice en alguna de estas opciones?',
    ];

    let responseIndex = 0;
    const interval = setInterval(() => {
      if (responseIndex < responses.length) {
        const content = responses.slice(0, responseIndex + 1).join('\n');
        appendToMessage(conversationId, assistantMessageId, 
          responseIndex === 0 ? content : '\n' + responses[responseIndex]
        );
        responseIndex++;
      } else {
        clearInterval(interval);
        setStreamingMessage(null);
        setIsStreaming(false);
        
        // Update message to remove streaming indicator
        const currentMessages = messages[conversationId] || [];
        const updatedMessages = currentMessages.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, isStreaming: false, content: msg.content }
            : msg
        );
      }
    }, 300);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isStreaming) return;

    let conversationId = activeConversationId;
    
    // Create new conversation if none exists
    if (!conversationId) {
      conversationId = createConversation(projects[0]?.id || '1', 'Nueva conversación');
    }

    // Add user message
    addMessage(conversationId, {
      role: 'user',
      content: inputValue.trim(),
    });

    const userMessage = inputValue.trim();
    setInputValue('');
    setShowSuggestions(false);

    // Simulate AI response
    await simulateStreamingResponse(userMessage, conversationId);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const MessageBubble: React.FC<{
    message: any;
    isLast: boolean;
  }> = ({ message, isLast }) => {
    const isUser = message.role === 'user';
    const isStreaming = message.isStreaming;

    return (
      <div className={cn(
        "flex gap-4 group",
        isUser ? "justify-end" : "justify-start"
      )}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-4 h-4 text-brand-500" />
          </div>
        )}
        
        <div className={cn(
          "max-w-[700px] px-6 py-4 rounded-2xl relative",
          isUser 
            ? "bg-brand-500 text-white rounded-br-md" 
            : "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 rounded-bl-md"
        )}>
          <div className="space-y-3">
            {/* Message content with markdown-like formatting */}
            <div className="prose prose-sm max-w-none">
              {message.content.split('\n').map((line: string, index: number) => (
                <p key={index} className="mb-2 last:mb-0">
                  {line}
                </p>
              ))}
            </div>

            {/* Streaming indicator */}
            {isStreaming && (
              <div className="iris-streaming-dots">
                <div className="iris-streaming-dot" />
                <div className="iris-streaming-dot" />
                <div className="iris-streaming-dot" />
              </div>
            )}

            {/* Message actions */}
            {!isStreaming && (
              <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="p-1 rounded hover:bg-black/10 dark:hover:bg-white/10">
                  <ThumbsUp className="w-4 h-4" />
                </button>
                <button className="p-1 rounded hover:bg-black/10 dark:hover:bg-white/10">
                  <ThumbsDown className="w-4 h-4" />
                </button>
                <button className="p-1 rounded hover:bg-black/10 dark:hover:bg-white/10">
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Timestamp */}
            <div className={cn(
              "text-xs opacity-70",
              isUser ? "text-right" : "text-left"
            )}>
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>

        {isUser && (
          <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center flex-shrink-0">
            <span className="text-white text-sm font-medium">U</span>
          </div>
        )}
      </div>
    );
  };

  const ConversationList: React.FC = () => (
    <div className="w-80 border-r border-border bg-background">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-title font-semibold">Conversaciones</h2>
          <button 
            onClick={() => createConversation(projects[0]?.id || '1')}
            className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            type="text"
            placeholder="Buscar conversaciones..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full h-10 pl-10 pr-4 bg-neutral-100 dark:bg-neutral-800 rounded-xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all"
          />
        </div>

        {/* Filter */}
        <div className="flex space-x-1">
          {(['all', 'recent'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setConversationFilter(filter)}
              className={cn(
                "px-3 py-1.5 text-sm font-medium rounded-lg transition-colors",
                conversationFilter === filter
                  ? "bg-brand-500 text-white"
                  : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
              )}
            >
              {filter === 'all' ? 'Todas' : 'Recientes'}
            </button>
          ))}
        </div>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-2">
          {conversations
            .filter(conv => {
              if (searchQuery) {
                return conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       conv.lastMessage.toLowerCase().includes(searchQuery.toLowerCase());
              }
              return true;
            })
            .map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => setActiveConversation(conversation.id)}
                className={cn(
                  "p-4 rounded-xl cursor-pointer transition-all duration-200",
                  activeConversationId === conversation.id
                    ? "bg-brand-50 dark:bg-brand-900/20 border border-brand-200 dark:border-brand-800"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-800"
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-sm truncate flex-1">
                    {conversation.title}
                  </h3>
                  <button className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-neutral-200 dark:hover:bg-neutral-700">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-neutral-500 line-clamp-2 mb-2">
                  {conversation.lastMessage}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-neutral-400">
                    {new Date(conversation.updated_at).toLocaleDateString()}
                  </span>
                  <span className="text-xs text-neutral-400">
                    {conversation.messages?.length || 0} mensajes
                  </span>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-full">
      {/* Conversations Sidebar */}
      <ConversationList />

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="border-b border-border bg-background px-8 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-subtitle font-semibold">
                    {activeConversation.title}
                  </h1>
                  <p className="text-sm text-neutral-500">
                    {activeConversation.messages.length} mensajes • 
                    Proyecto: {projects.find(p => p.id === activeConversation.projectId)?.name}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800">
                    <Settings className="w-5 h-5" />
                  </button>
                  <button className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
              {getCurrentMessages().map((message, index) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  isLast={index === getCurrentMessages().length - 1}
                />
              ))}
              
              {/* Streaming indicator */}
              {isStreaming && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-4 h-4 text-brand-500" />
                  </div>
                  <div className="bg-neutral-100 dark:bg-neutral-800 rounded-2xl rounded-bl-md px-6 py-4">
                    <div className="iris-streaming-dots">
                      <div className="iris-streaming-dot" />
                      <div className="iris-streaming-dot" />
                      <div className="iris-streaming-dot" />
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            {suggestions.length > 0 && !isStreaming && (
              <div className="px-8 py-4 border-t border-border">
                <p className="text-sm text-neutral-500 mb-3">Sugerencias:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setInputValue(suggestion)}
                      className="px-4 py-2 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-lg text-sm transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="border-t border-border bg-background p-8">
              <div className="relative">
                <div className="flex items-end space-x-4">
                  <div className="flex-1">
                    <textarea
                      ref={inputRef}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Escribe tu mensaje..."
                      className="w-full px-6 py-4 bg-neutral-100 dark:bg-neutral-800 rounded-2xl border-0 focus:ring-2 focus:ring-brand-500 focus:bg-background transition-all resize-none"
                      rows={1}
                      style={{
                        minHeight: '56px',
                        maxHeight: '120px',
                      }}
                    />
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center space-x-2">
                        <button className="p-2 rounded-lg hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors">
                          <Paperclip className="w-4 h-4" />
                        </button>
                        <button className="p-2 rounded-lg hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors">
                          <Mic className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-neutral-500">
                          {inputValue.length} / 4000
                        </span>
                        <button
                          onClick={handleSendMessage}
                          disabled={!inputValue.trim() || isStreaming}
                          className="iris-button-primary disabled:opacity-50 disabled:cursor-not-allowed p-3"
                        >
                          {isStreaming ? (
                            <Square className="w-4 h-4" />
                          ) : (
                            <Send className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : (
          /* No Conversation Selected */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-neutral-100 dark:bg-neutral-800 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <MessageCircle className="w-8 h-8 text-neutral-400" />
              </div>
              <h3 className="text-title font-semibold mb-3">
                Inicia una conversación
              </h3>
              <p className="text-neutral-600 dark:text-neutral-400 mb-8">
                Selecciona una conversación existente o crea una nueva para comenzar a chatear con IRIS.
              </p>
              <button
                onClick={() => createConversation(projects[0]?.id || '1')}
                className="iris-button-primary"
              >
                <Plus className="w-5 h-5 mr-2" />
                Nueva conversación
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;