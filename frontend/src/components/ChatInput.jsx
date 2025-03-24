import { useState, useRef, useEffect } from 'react';
import sendIcon from '@/assets/images/send.svg';

function ChatInput({ newMessage, isLoading, setNewMessage, submitNewMessage }) {
  const [rows, setRows] = useState(1);
  const textAreaRef = useRef(null);

  const adjustTextAreaHeight = () => {
    const textArea = textAreaRef.current;
    if (!textArea) return;

    // Reset height to allow shrinking
    textArea.style.height = 'auto';
    
    // Calculate new height
    const newHeight = Math.min(
      Math.max(textArea.scrollHeight, 40), // minimum 40px
      120 // maximum 120px
    );
    
    textArea.style.height = `${newHeight}px`;
  };

  useEffect(() => {
    adjustTextAreaHeight();
  }, [newMessage]); // Adjust height when message changes

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitNewMessage(newMessage);
    }
  };

  const handleSubmit = () => {
    submitNewMessage(newMessage);
  };

  const handleChange = (e) => {
    setNewMessage(e.target.value);
  };

  return (
    <div className="p-4 bg-white shadow-t-lg">
      <div className="flex w-full items-end gap-2">
        <textarea
          ref={textAreaRef}
          value={newMessage}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1 min-h-[40px] p-2 border border-gray-300 rounded-lg 
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:bg-gray-100 disabled:cursor-not-allowed resize-none overflow-y-hidden"
        />
        <button
          onClick={handleSubmit}
          disabled={isLoading || !newMessage.trim()}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 
            disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors
            h-[40px] flex-shrink-0"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatInput;