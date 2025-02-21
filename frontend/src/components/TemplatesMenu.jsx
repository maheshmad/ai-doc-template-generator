import { useState, useEffect } from 'react';
import { ChevronDownIcon, ChevronRightIcon, DocumentIcon } from '@heroicons/react/24/outline';
import { templatesService } from '../services/templatesService';
import { format, parseISO } from 'date-fns';

const TreeNode = ({ label, children, level = 0, templateId, onSelectTemplate }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = children && children.length > 0;
  
  const handleClick = () => {
    console.log('templateId', templateId);
    if (hasChildren) {
      setIsExpanded(!isExpanded);
    } else if (templateId) {
      console.log('templateId', templateId);
      onSelectTemplate(templateId);
    }
  };
  
  return (
    <div className="select-none">
      <div 
        className={`flex items-center gap-1 p-2 hover:bg-gray-100 rounded cursor-pointer ${level > 0 ? 'ml-4' : ''}`}
        onClick={handleClick}
      >
        {hasChildren ? (
          isExpanded ? (
            <ChevronDownIcon className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronRightIcon className="h-4 w-4 text-gray-500" />
          )
        ) : (
          <DocumentIcon className="h-4 w-4 text-gray-500" />
        )}
        <span className="text-sm text-gray-700">{label}</span>
      </div>
      
      {isExpanded && hasChildren && (
        <div className="ml-2">
          {children.map((child, index) => (
            <TreeNode 
              key={`${child.label}-${index}`}
              label={child.label}
              children={child.children}
              level={level + 1}
              templateId={child.template_id}
              onSelectTemplate={onSelectTemplate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const TemplatesMenu = ({ onSelectTemplate }) => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const data = await templatesService.getTemplates();
        
        // Organize templates by update date
        const organized = data.reduce((acc, template) => {
          const updateDate = parseISO(template.template_updated);
          const category = format(updateDate, 'MMM dd, yyyy');

          if (!acc[category]) {
            acc[category] = [];
          }
          acc[category].push(template);
          return acc;
        }, {});

        // Convert to tree structure with sorted dates (newest first)
        const treeData = Object.entries(organized)
          .sort(([a], [b]) => parseISO(b).getTime() - parseISO(a).getTime())
          .map(([category, items]) => ({
            label: category,
            children: items.map(item => ({
              label: item.template_name,
              template_id: item.template_id
            }))
          }));

        setTemplates(treeData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-500">
        Error loading templates: {error}
      </div>
    );
  }

  return (
    <div className="p-4">
      <h2 className="text-lg font-medium text-gray-700 mb-4">Templates</h2>
      <div className="space-y-1">
        {templates.map((node, index) => (
          <TreeNode 
            key={`${node.label}-${index}`}
            label={node.label}
            children={node.children}
            onSelectTemplate={onSelectTemplate}
          />
        ))}
      </div>
    </div>
  );
};

export default TemplatesMenu; 