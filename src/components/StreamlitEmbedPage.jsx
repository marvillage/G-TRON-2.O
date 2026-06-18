// components/StreamlitEmbedPage.jsx
import { useEffect, useRef } from 'react';
import { Server, Github, TerminalSquare } from 'lucide-react';

// Detect URLs that only resolve on the developer's machine. These modules are
// Streamlit apps that run locally (ports 850x); they aren't part of the hosted
// deployment, so in production we show an informative placeholder instead of a
// broken iframe pointing at localhost.
const isLocalOnly = (url) =>
  !url || /localhost|127\.0\.0\.1/.test(url);

const StreamlitEmbedPage = ({ title, url }) => {
  const iframeRef = useRef(null);

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data?.type === 'STREAMLIT_HEIGHT' && iframeRef.current) {
        iframeRef.current.style.height = `${event.data.height}px`;
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  if (isLocalOnly(url)) {
    return (
      <div className="flex w-full flex-col gap-y-4">
        {title && <h1 className="title">{title}</h1>}
        <div className="card">
          <div className="card-body flex flex-col items-center gap-y-4 py-12 text-center">
            <div className="rounded-full bg-blue-500/10 p-4 text-blue-500">
              <Server size={32} />
            </div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50">
              {title} runs as a local Streamlit service
            </h2>
            <p className="max-w-xl text-slate-600 dark:text-slate-300">
              This module is a Python/Streamlit app (with ML models, Neo4j and LLM
              backends) that runs on your machine. It isn&apos;t part of this hosted
              demo. To explore it, clone the repo and run the Streamlit servers locally.
            </p>
            <div className="mt-2 flex items-center gap-x-2 rounded-lg bg-slate-100 px-4 py-2 font-mono text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-200">
              <TerminalSquare size={16} />
              <span>streamlit run app.py</span>
            </div>
            <a
              href="https://github.com/marvillage/G-TRON-2.O"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-flex items-center gap-x-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              <Github size={16} />
              View setup on GitHub
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full flex-col">
      {title && <h1 className="px-2 py-1 text-2xl font-bold">{title}</h1>}
      <div className="w-full flex-1">
        <iframe
          ref={iframeRef}
          id="streamlit-iframe"
          src={url}
          title={title}
          className="h-full w-full border-none"
          style={{ display: 'block' }}
          onLoad={() => {
            iframeRef.current?.contentWindow?.postMessage(
              { type: 'PARENT_URL', parentUrl: window.location.href },
              '*',
            );
          }}
        />
      </div>
    </div>
  );
};

export default StreamlitEmbedPage;
