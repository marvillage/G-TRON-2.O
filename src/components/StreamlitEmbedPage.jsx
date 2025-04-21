// components/StreamlitEmbedPage.jsx
import { useEffect, useRef } from 'react';

const StreamlitEmbedPage = ({ title, url }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data.type === 'STREAMLIT_HEIGHT') {
        if (iframeRef.current) {
          iframeRef.current.style.height = `${event.data.height}px`;
        }
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return (
    <div className="w-full h-screen flex flex-col">
      {title && <h1 className="text-2xl font-bold px-2 py-1">{title}</h1>}
      <div className="flex-1 w-full">
        <iframe
          ref={iframeRef}
          id="streamlit-iframe"
          src={url}
          className="w-full h-full border-none"
          style={{ display: 'block' }}
          onLoad={() => {
            if (iframeRef.current) {
              iframeRef.current.contentWindow.postMessage({
                type: 'PARENT_URL',
                parentUrl: window.location.href
              }, '*');
            }
          }}
        />
      </div>
    </div>
  );
};

export default StreamlitEmbedPage;