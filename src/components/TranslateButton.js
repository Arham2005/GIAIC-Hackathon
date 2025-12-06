import React, { useState } from 'react';

export default function TranslateButton() {
  const [translating, setTranslating] = useState(false);
  const [translated, setTranslated] = useState(false);
  const [originalContent, setOriginalContent] = useState(null);

  const translateToUrdu = async () => {
    setTranslating(true);
    
    try {
      // Get the main article content
      const article = document.querySelector('article');
      
      if (!article) {
        alert('Content not found');
        return;
      }

      // Save original content if not already saved
      if (!originalContent) {
        setOriginalContent(article.innerHTML);
      }

      // Get all text content
      const textElements = article.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th');
      
      // Translate each element using your backend
      const API_URL = 'http://localhost:8000'; // Your backend URL
      
      for (const element of textElements) {
        const originalText = element.textContent;
        
        // Skip code blocks and very short text
        if (element.closest('pre') || originalText.length < 10) {
          continue;
        }

        try {
          const response = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: originalText,
              target_language: 'urdu'
            })
          });

          const data = await response.json();
          element.textContent = data.translated_text;
        } catch (err) {
          console.error('Translation error:', err);
        }
      }

      setTranslated(true);
    } catch (error) {
      console.error('Translation failed:', error);
      alert('Translation failed. Please try again.');
    } finally {
      setTranslating(false);
    }
  };

  const restoreOriginal = () => {
    const article = document.querySelector('article');
    if (article && originalContent) {
      article.innerHTML = originalContent;
      setTranslated(false);
    }
  };

  return (
    <div style={{
      position: 'sticky',
      top: '60px',
      zIndex: 100,
      backgroundColor: 'var(--ifm-background-color)',
      padding: '10px',
      marginBottom: '20px',
      borderBottom: '2px solid var(--ifm-color-emphasis-300)',
      display: 'flex',
      gap: '10px',
      alignItems: 'center'
    }}>
      {!translated ? (
        <button
          onClick={translateToUrdu}
          disabled={translating}
          style={{
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '6px',
            cursor: translating ? 'wait' : 'pointer',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>🌐</span>
          {translating ? 'Translating to Urdu...' : 'Translate to Urdu (اردو میں ترجمہ کریں)'}
        </button>
      ) : (
        <button
          onClick={restoreOriginal}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>🔄</span>
          Show Original (English)
        </button>
      )}
      
      {translating && (
        <div style={{
          fontSize: '14px',
          color: 'var(--ifm-color-emphasis-700)'
        }}>
          Translating content... Please wait.
        </div>
      )}
    </div>
  );
}