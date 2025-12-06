import React from 'react';
import ChatbotWidget from '../components/ChatbotWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}