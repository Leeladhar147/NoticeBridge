import React from 'react';

/**
 * NoticeBridge Logo
 * Features the signature NB Bridge Monogram and NoticeBridge wordmark,
 * directly from the brand identity reference.
 * Sized appropriately to fit cleanly into the navbar space.
 */
export default function NoticeBridgeLogo({
  size = 38,
  showWordmark = true,
  className = ''
}) {
  const logoSrc = showWordmark
    ? '/noticebridge_logo_full.png'
    : '/noticebridge_nb_monogram.png';

  return (
    <div
      className={`noticebridge-logo-wrapper ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        userSelect: 'none',
        cursor: 'pointer'
      }}
    >
      <img
        src={logoSrc}
        alt="NoticeBridge"
        style={{
          height: `${size}px`,
          width: 'auto',
          display: 'block',
          objectFit: 'contain'
        }}
      />
    </div>
  );
}
