import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { templatesService } from '../services/templatesService';
import { PencilIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

function TemplateEditor({ templateId }) {   
  const [chunks, setChunks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const loadTemplate = async () => {
      if (!templateId) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const templateChunks = await templatesService.getTemplateChunks(templateId);
        setChunks(templateChunks);
        
        // Set initial edit content
        const combined = templateChunks
          .sort((a, b) => a.template_chunk_order - b.template_chunk_order)
          .map(chunk => chunk.template_content.trim())
          .filter(content => content)
          .join('\n\n---\n\n');
        setEditContent(combined);
      } catch (err) {
        setError(err.message || 'Failed to load template');
      } finally {
        setLoading(false);
      }
    };

    loadTemplate();
  }, [templateId]);

  const handleEditClick = () => {
    setIsEditing(!isEditing);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await templatesService.updateTemplateContent(templateId, editContent);
      
      // Refresh the template content
      const templateChunks = await templatesService.getTemplateChunks(templateId);
      setChunks(templateChunks);
      
      setIsEditing(false);
    } catch (err) {
      setError(err.message || 'Failed to save template');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset edit content to current content
    const combined = chunks
      .sort((a, b) => a.template_chunk_order - b.template_chunk_order)
      .map(chunk => chunk.template_content.trim())
      .filter(content => content)
      .join('\n\n---\n\n');
    setEditContent(combined);
    setIsEditing(false);
  };

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

  return (
    <div className="flex flex-col h-full">
      <div className="flex-none px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Template Content</h1>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
                    bg-green-100 text-green-700 hover:bg-green-200 disabled:opacity-50 
                    disabled:cursor-not-allowed transition-colors"
                >
                  <CheckIcon className="h-4 w-4" />
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
                <button
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
                    bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 
                    disabled:cursor-not-allowed transition-colors"
                >
                  <XMarkIcon className="h-4 w-4" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={handleEditClick}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
                  bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              >
                <PencilIcon className="h-4 w-4" />
                Edit
              </button>
            )}
          </div>
        </div>
      </div>
      <div className="flex-1 min-h-0">
        <div className="h-full overflow-y-auto">
          <div className="p-4">
            <div className="prose max-w-none">
              {isEditing ? (
                <textarea
                  className="w-full h-full min-h-[500px] p-4 border border-gray-300 rounded-lg 
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                    font-mono text-sm"
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  disabled={isSaving}
                />
              ) : (
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
                  {editContent}
                </ReactMarkdown>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TemplateEditor; 