import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Spinner from '@/components/Spinner';
import userIcon from '@/assets/images/user.svg';
import errorIcon from '@/assets/images/error.svg';

function ChatMessages({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Scroll when messages update

  return (
    <div className="flex-1 min-h-0"> {/* Enable scroll for flex child */}
      <div className="h-full w-full px-4">
        <div className="space-y-6 py-4">
          {messages.map((message, index) => (
            <div 
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user' 
                    ? 'bg-primary-blue text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="prose max-w-none whitespace-pre-wrap">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({node, ...props}) => <p className="my-1" {...props} />,
                      // Add other markdown components as needed
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
                {message.loading && (
                  <div className="mt-2 text-sm opacity-70">
                    Typing...
                  </div>
                )}
                {message.error && (
                  <div className="mt-2 text-sm text-red-500">
                    Error: Failed to send message
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} /> {/* Scroll anchor */}
        </div>
      </div>
    </div>
  );
}

export default ChatMessages;