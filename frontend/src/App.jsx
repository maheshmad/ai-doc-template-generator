import { useState } from 'react';
import Splitter from './components/Splitter';
import TemplatesMenu from './components/TemplatesMenu';
import TemplateEditor from './components/TemplateEditor';
import Chatbot from './components/Chatbot';
import logo from '@/assets/images/logo.svg';

function App() {
  const [selectedTemplateId, setSelectedTemplateId] = useState(null);

  const handleSelectTemplate = (templateId) => {
    console.log('Template selected:', templateId); // Debug log
    setSelectedTemplateId(templateId);
  };

  return (
    <div className='flex flex-col h-screen w-screen'>
      {/* Header Menu Bar */}
      <header className='h-14 bg-white border-b border-gray-200 flex items-center px-4 shrink-0'>
        <div className='flex items-center gap-4'>
          <img src={logo} alt='Logo' className='h-8 w-8' />
          <h1 className='text-xl font-semibold text-gray-800'>AI Assistant</h1>
        </div>
        <nav className='ml-8 flex gap-4'>
          <button className='px-3 py-1 text-gray-600 hover:text-gray-900'>Documents</button>
          <button className='px-3 py-1 text-gray-600 hover:text-gray-900'>Settings</button>
        </nav>
      </header>
      
      {/* Main Content */}
      <div className='flex flex-1 overflow-hidden'>
        {/* Left Side Panel with Templates */}
        <aside className='w-64 bg-gray-50 border-r border-gray-200 overflow-y-auto flex-shrink-0'>
          <TemplatesMenu onSelectTemplate={handleSelectTemplate} />
        </aside>

        {/* Main Content Area with Splitter */}
        <div className="flex-1 flex">
          <Splitter
            left={
              <section className='h-full overflow-auto'>
                <TemplateEditor templateId={selectedTemplateId} />
              </section>
            }
            right={
              <aside className='h-full border-l border-gray-200 overflow-hidden flex flex-col'>
                <Chatbot />
              </aside>
            }                 
          />
        </div>
      </div>
    </div>
  );
}

export default App;