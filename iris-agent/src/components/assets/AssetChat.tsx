import React, { useState, useRef, useEffect } from 'react';
import { 
  PaperAirplaneIcon, 
  PhotoIcon, 
  SparklesIcon,
  UserIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import { AssetChatResponse, AssetResponse } from '../../lib/api';
import mcpClient from '../../lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  asset?: AssetResponse;
}

interface AssetChatProps {
  className?: string;
  onAssetGenerated?: (asset: AssetResponse) => void;
}

const AssetChat: React.FC<AssetChatProps> = ({ 
  className = '', 
  onAssetGenerated 
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '¡Hola! Soy IRIS, tu asistente para generar assets increíbles. ¿Qué asset te gustaría que creara para ti? Puedo generar logos, páginas web, dashboards, y mucho más.',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al final
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Enviar mensaje
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Enviar a IRIS para procesamiento
      const response = await mcpClient.chatWithAssetGeneration(
        inputMessage.trim(),
        conversationId
      );

      if (response) {
        // Actualizar conversation_id
        setConversationId(response.conversation_id);

        const assistantMessage: Message = {
          id: response.message_id,
          role: 'assistant',
          content: response.response,
          timestamp: new Date(response.timestamp),
          asset: response.asset_generated || undefined
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Notificar si se generó un asset
        if (response.asset_generated) {
          onAssetGenerated?.(response.asset_generated);
        }
      } else {
        // Respuesta de error
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Lo siento, hubo un error procesando tu mensaje. ¿Podrías intentarlo de nuevo?',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Lo siento, hay un problema de conexión. ¿Podrías intentar de nuevo?',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Manejar Enter
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Obtener icono del asset
  const getAssetIcon = (category: string) => {
    switch (category) {
      case 'branding': return '🎨';
      case 'mobile_ui': return '📱';
      case 'marketing': return '📊';
      case 'saas_platform': return '💼';
      case 'ecommerce': return '🛒';
      case 'executive': return '📈';
      case 'ai_stress_test': return '🤖';
      default: return '✨';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg flex flex-col ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <SparklesIcon className="w-5 h-5 text-purple-600" />
          Chat con IRIS
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Habla conmigo para generar assets automáticamente
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`flex gap-3 max-w-[80%] ${
                message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {message.role === 'user' ? (
                  <UserIcon className="w-4 h-4" />
                ) : (
                  <ComputerDesktopIcon className="w-4 h-4" />
                )}
              </div>

              {/* Message content */}
              <div
                className={`rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                
                {/* Asset generado */}
                {message.asset && message.asset.status === 'completed' && (
                  <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">
                        {getAssetIcon(message.asset.category)}
                      </span>
                      <span className="text-xs font-medium text-gray-600">
                        {message.asset.category.toUpperCase()} • {message.asset.format.toUpperCase()}
                      </span>
                    </div>
                    
                    {message.asset.preview_url && (
                      <img
                        src={message.asset.preview_url}
                        alt="Generated asset"
                        className="w-full h-32 object-contain border border-gray-100 rounded"
                      />
                    )}
                    
                    <div className="mt-2 space-y-1">
                      {message.asset.files.map((file, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between text-xs"
                        >
                          <span className="text-gray-600">{file.filename}</span>
                          {file.url && (
                            <a
                              href={file.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-purple-600 hover:text-purple-800"
                            >
                              Ver
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="text-xs mt-1 opacity-70">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
              <ComputerDesktopIcon className="w-4 h-4" />
            </div>
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                <span className="text-sm text-gray-600">IRIS está pensando...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Escribe un mensaje... ej: 'Crea un logo moderno para mi startup'"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className={`px-4 py-2 rounded-md flex items-center gap-2 transition-colors ${
              !inputMessage.trim() || isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700 text-white'
            }`}
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
        
        <div className="text-xs text-gray-500 mt-2">
          <span>💡 Tip: Describe lo que quieres crear de forma natural</span>
        </div>
      </div>
    </div>
  );
};

export default AssetChat;