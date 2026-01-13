import React from 'react';
import clsx from 'clsx'; // Utility for conditional classes

interface MessageProps {
  role: 'user' | 'ai';
  text: string;
}

export const Message: React.FC<MessageProps> = ({ role, text }) => {
  const isUser = role === 'user';
  return (
    <div className={clsx("flex mb-4", isUser ? "justify-end" : "justify-start")}>
      <div
        className={clsx(
          "max-w-[80%] p-3 rounded-lg shadow-sm whitespace-pre-wrap",
          isUser ? "bg-blue-600 text-white rounded-br-none" : "bg-white text-gray-800 rounded-bl-none"
        )}
      >
        {text}
      </div>
    </div>
  );
};

