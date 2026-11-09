import React from 'react';

export const UafTridentLogo: React.FC<{ className?: string }> = ({ className = 'w-10 h-10' }) => {
  return React.createElement(
    'div',
    {
      className: `inline-flex items-center justify-center bg-uaf-mundyr border border-uaf-gold/40 rounded-sm shrink-0 ${className}`,
      title: 'Військовий Тризуб Збройних Сил України',
    },
    React.createElement(
      'svg',
      { viewBox: '0 0 100 120', className: 'w-7 h-7 fill-uaf-gold', xmlns: 'http://www.w3.org/2000/svg' },
      React.createElement('path', {
        d: 'M50 6 L57 26 L56 80 L72 80 L72 34 C72 24 79 17 86 14 L86 94 L57 94 L50 114 L43 94 L14 94 L14 14 C21 17 28 24 28 34 L28 80 L44 80 L43 26 Z',
      })
    )
  );
};
