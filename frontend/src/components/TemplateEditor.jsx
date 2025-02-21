import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { templatesService } from '../services/templatesService';

function TemplateEditor({ templateId }) {   
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadTemplate = async () => {
      if (!templateId) return;
      
      setLoading(true);
      try {
        const templateChunks = await templatesService.getTemplateChunks(templateId);
        setChunks(templateChunks);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, [templateId]);

  if (!templateId) {
    return (
      <div className="flex flex-col h-full items-center justify-center text-gray-500">
        Select a template to view its content
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col h-full">
        <div className="animate-pulse space-y-4 p-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col h-full p-4">
        <div className="text-red-500">Error loading template: {error}</div>
      </div>
    );
  }

  // Combine all chunk content preserving newlines
  const combinedContent = chunks
    .sort((a, b) => a.template_chunk_order - b.template_chunk_order)
    .map(chunk => chunk.template_content.trim()) // Remove any leading/trailing whitespace
    .filter(content => content) // Remove empty chunks
    .join('\n\n'); // Add markdown horizontal rule between chunks with proper spacing

  return (
    <div className="flex flex-col h-full">
      <h1 className="text-2xl font-bold mb-4">Template Content</h1>
      <div className="flex-1 overflow-y-auto p-4 bg-white rounded shadow">
        <div className="prose max-w-none whitespace-pre-wrap">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              h1: ({node, ...props}) => <h1 className="text-2xl font-bold my-4" {...props} />,
              h2: ({node, ...props}) => <h2 className="text-xl font-bold my-3" {...props} />,
              h3: ({node, ...props}) => <h3 className="text-lg font-bold my-2" {...props} />,
              p: ({node, ...props}) => <p className="my-2" {...props} />,
              ul: ({node, ...props}) => <ul className="list-disc ml-4 my-2" {...props} />,
              ol: ({node, ...props}) => <ol className="list-decimal ml-4 my-2" {...props} />,
              li: ({node, ...props}) => <li className="my-1" {...props} />,
              a: ({node, ...props}) => <a className="text-blue-600 hover:underline" {...props} />,
              blockquote: ({node, ...props}) => (
                <blockquote className="border-l-4 border-gray-200 pl-4 my-2 italic" {...props} />
              ),
              code: ({node, inline, ...props}) => (
                inline ? 
                  <code className="bg-gray-100 rounded px-1" {...props} /> :
                  <code className="block bg-gray-100 p-2 rounded my-2" {...props} />
              ),
              hr: ({node, ...props}) => <hr className="my-8 border-t-2 border-gray-200" {...props} />,
            }}
          >
            {combinedContent}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default TemplateEditor; 