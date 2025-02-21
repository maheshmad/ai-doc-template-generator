import { useState, useCallback, useEffect, useRef } from 'react';

const Splitter = ({ 
  left, 
  right,
  initialLeftWidth = '80%',
  minLeftWidth = 400,
  maxRightWidth = 600,
  children
}) => {
  const containerRef = useRef(null);
  const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
  const [isDragging, setIsDragging] = useState(false);

  // Initialize width on mount and window resize
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.offsetWidth;
        const initialWidth = typeof initialLeftWidth === 'string' 
          ? (containerWidth * parseInt(initialLeftWidth) / 100)
          : initialLeftWidth;
        
        // Ensure left width respects right panel max width
        const maxLeft = containerWidth - maxRightWidth;
        setLeftWidth(Math.min(Math.max(initialWidth, minLeftWidth), maxLeft));
      }
    };

    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, [initialLeftWidth, minLeftWidth, maxRightWidth]);

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging || !containerRef.current) return;
    
    const containerRect = containerRef.current.getBoundingClientRect();
    const containerWidth = containerRect.width;
    const maxLeft = containerWidth - maxRightWidth; // Maximum left width to respect right max width
    
    const newWidth = Math.min(
      Math.max(e.clientX - containerRect.left, minLeftWidth),
      maxLeft
    );
    
    setLeftWidth(newWidth);
  }, [isDragging, minLeftWidth, maxRightWidth]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.userSelect = 'none';
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.userSelect = '';
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div ref={containerRef} className="flex h-full w-full">
      {/* Left Panel */}
      <div 
        style={{ width: leftWidth }} 
        className="flex-shrink-0 overflow-hidden"
      >
        {typeof left === 'function' ? left({ width: leftWidth }) : left}
      </div>

      {/* Splitter Handle */}
      <div
        className={`w-1 hover:w-2 bg-gray-200 hover:bg-blue-400 cursor-col-resize transition-colors
          ${isDragging ? 'bg-blue-400 w-2' : ''}`}
        onMouseDown={handleMouseDown}
      />

      {/* Right Panel */}
      <div className="flex-1 overflow-hidden" style={{ maxWidth: maxRightWidth }}>
        {typeof right === 'function' ? right({ width: leftWidth }) : right}
      </div>

      {children}
    </div>
  );
};

export default Splitter; 