import { useState } from 'react';
import { useImmer } from 'use-immer';
import api from '@/api';
import { parseSSEStream } from '@/utils';
import ChatMessages from '@/components/ChatMessages';
import ChatInput from '@/components/ChatInput';

function Chatbot() {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState('');

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(draft => [...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', sources: [], loading: true }
    ]);
    setNewMessage('');

    let chatIdOrNew = chatId;
    try {
      if (!chatId) {
        const { id } = await api.createChat();
        setChatId(id);
        chatIdOrNew = id;
      }

      const stream = await api.sendChatMessage(chatIdOrNew, trimmedMessage);
      for await (const textChunk of parseSSEStream(stream)) {
        setMessages(draft => {
          draft[draft.length - 1].content += textChunk;
        });
      }
      setMessages(draft => {
        draft[draft.length - 1].loading = false;
      });
    } catch (err) {
      console.log(err);
      setMessages(draft => {
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
      });
    }
  }

  return (
    <div className="flex flex-col h-full w-full">
      {messages.length === 0 ? (
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center text-gray-500">
            <p className="text-xl mb-2">👋 Welcome!</p>
            <p>Start a conversation about your template.</p>
          </div>
        </div>
      ) : (
        <ChatMessages
          messages={messages}
          isLoading={isLoading}
        />
      )}
      
      <div className="flex-none w-full p-4 border-t border-gray-200 bg-white">
        <ChatInput
          newMessage={newMessage}
          setNewMessage={setNewMessage}
          submitNewMessage={submitNewMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

export default Chatbot;