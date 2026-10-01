import React, { useEffect, useState, useRef } from 'react';

/**
 * TopNavigationLine:
 * Single accent navigation transition line (NoticeBridge Green).
 * Animates ONCE smoothly across the top of the viewport strictly when activePage changes.
 * Completely static (hidden/idle) while sitting on a page.
 * No loops, no pulses, no continuous movement, no rainbow colors.
 */
export default function TopNavigationLine({ activePage }) {
  const [animating, setAnimating] = useState(false);
  const firstRender = useRef(true);

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }

    // Trigger one smooth, medium-pace subtle animation
    setAnimating(true);
    const timer = setTimeout(() => {
      setAnimating(false);
    }, 850);

    return () => clearTimeout(timer);
  }, [activePage]);

  return (
    <div
      className="nav-line-container"
      aria-hidden="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '3.5px',
        zIndex: 9999,
        pointerEvents: 'none',
        overflow: 'hidden',
        background: 'transparent'
      }}
    >
      <div
        className={`nav-line-bar ${animating ? 'nav-line-animating' : ''}`}
        style={{
          height: '100%',
          background: '#10B981', // Single NoticeBridge Green accent
          width: animating ? '100%' : '0%',
          opacity: animating ? 1 : 0,
          boxShadow: animating ? '0 0 10px rgba(16, 185, 129, 0.5)' : 'none',
          transition: animating
            ? 'width 0.85s cubic-bezier(0.25, 1, 0.35, 1), opacity 0.2s ease 0.75s'
            : 'none'
        }}
      />
    </div>
  );
}
