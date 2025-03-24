import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Spinner from '@/components/Spinner';
import userIcon from '@/assets/images/user.svg';
import errorIcon from '@/assets/images/error.svg';
import Popup from './Popup';

function ChatMessages({ messages, isLoading }) {
  const messagesEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const [selectedPrompt, setSelectedPrompt] = useState(null);

  const scrollToBottom = () => {
    if (!scrollContainerRef.current) return;
    
    const { scrollHeight, clientHeight } = scrollContainerRef.current;
    scrollContainerRef.current.scrollTop = scrollHeight - clientHeight;
  };

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handlePromptClick = async (promptId) => {
    try {
      // Fetch prompt data from your API
      const response = await fetch(`/api/prompts/${promptId}`);
      if (!response.ok) throw new Error('Failed to fetch prompt');
      const promptData = await response.json();
      setSelectedPrompt(promptData);
    } catch (error) {
      console.error('Error fetching prompt:', error);
    }
  };

  return (
    <>
      <div 
        ref={scrollContainerRef}
        className="h-full overflow-y-auto"
      >
        <div className="px-4 py-4 space-y-6">
          {messages.map((message, index) => (
            <div 
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({node, ...props}) => <p className="m-0" {...props} />,
                      pre: ({node, ...props}) => (
                        <pre className="bg-gray-800 rounded p-2 overflow-x-auto my-2" {...props} />
                      ),
                      code: ({node, inline, ...props}) => (
                        inline 
                          ? <code className="bg-gray-700 rounded px-1" {...props} />
                          : <code className="block" {...props} />
                      ),
                      ul: ({node, ...props}) => <ul className="list-disc pl-4 my-2" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal pl-4 my-2" {...props} />,
                      li: ({node, ...props}) => <li className="my-1" {...props} />,
                      a: ({node, ...props}) => (
                        <a className="text-blue-300 hover:underline" {...props} />
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
                {message.linked_prompt_id && (
                  <button
                    onClick={() => handlePromptClick(message.linked_prompt_id)}
                    className="mt-2 text-xs px-2 py-1 rounded bg-opacity-20 hover:bg-opacity-30 transition-colors
                      bg-gray-500 text-gray-700"
                  >
                    View Prompt Details
                  </button>
                )}
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

      <Popup
        isOpen={!!selectedPrompt}
        onClose={() => setSelectedPrompt(null)}
        title="Prompt Details"
      >
        {selectedPrompt && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Prompt ID</h3>
              <p className="mt-1">{selectedPrompt.prompt_id}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Name</h3>
              <p className="mt-1">{selectedPrompt.name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Description</h3>
              <p className="mt-1 whitespace-pre-wrap">{selectedPrompt.description}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Content</h3>
              <pre className="mt-1 p-4 bg-gray-50 rounded-lg overflow-x-auto">
                <code>{selectedPrompt.content}</code>
              </pre>
            </div>
            {selectedPrompt.metadata && (
              <div>
                <h3 className="text-sm font-medium text-gray-500">Metadata</h3>
                <pre className="mt-1 p-4 bg-gray-50 rounded-lg overflow-x-auto">
                  <code>{JSON.stringify(selectedPrompt.metadata, null, 2)}</code>
                </pre>
              </div>
            )}
          </div>
        )}
      </Popup>
    </>
  );
}

export default ChatMessages;