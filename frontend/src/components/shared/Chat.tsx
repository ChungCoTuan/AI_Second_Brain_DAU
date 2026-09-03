import React from 'react';
import './Shared.css';
import { CitationBadge } from './Badge';

interface Citation {
  id: string;
  source: string;
}

interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  citations?: Citation[];
  onCitationClick?: (id: string) => void;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message, isUser, citations, onCitationClick }) => {
  return (
    <div className={`chat-bubble-container ${isUser ? 'user' : 'system'}`}>
      <div className="chat-bubble">
        {message}
      </div>
      {!isUser && citations && citations.length > 0 && (
        <div className="chat-citations">
          {citations.map((cit, idx) => (
            <CitationBadge 
              key={idx} 
              id={cit.id} 
              source={cit.source} 
              onClick={() => onCitationClick && onCitationClick(cit.id)} 
            />
          ))}
        </div>
      )}
    </div>
  );
};
