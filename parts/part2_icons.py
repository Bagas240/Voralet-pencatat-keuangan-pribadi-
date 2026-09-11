PART2_ICONS = """
    // =========================================================================
    // 2. ICON SYSTEM (Apple SF Symbols Thin-Stroke SVG Icons & Badge System)
    // =========================================================================
    const Icon = ({ name, className = "w-5 h-5", strokeWidth = 2 }) => {
      const computedClass = className.includes('aspect-square')
        ? className
        : `${className} flex-shrink-0 aspect-square`;
      switch (name) {
        case 'x':
        case 'X':
        case 'close':
        case 'Close':
        case 'dismiss':
          return (
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className={computedClass}>
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          );
        case 'wallet':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="5" width="20" height="14" rx="3" />
              <line x1="2" y1="10" x2="22" y2="10" />
              <circle cx="16.5" cy="14.5" r="1.2" fill="currentColor" />
            </svg>
          );
        case 'bank':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 21h18M3 10h18M5 10v11M9 10v11M15 10v11M19 10v11M12 3l9 7H3l9-7z" />
            </svg>
          );
        case 'cash':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="6" width="20" height="12" rx="2.5" />
              <circle cx="12" cy="12" r="3" />
              <path d="M6 12h.01M18 12h.01" />
            </svg>
          );
        case 'smartphone':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="6" y="2" width="12" height="20" rx="3" />
              <line x1="11" y1="18" x2="13" y2="18" />
            </svg>
          );
        case 'receipt':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 2v20l3-2 3 2 3-2 3 2 4-2V2l-4 2-3-2-3 2-3-2-3 2z" />
              <line x1="8" y1="7" x2="16" y2="7" />
              <line x1="8" y1="11" x2="16" y2="11" />
              <line x1="8" y1="15" x2="12" y2="15" />
            </svg>
          );
        case 'arrow-up-right':
        case 'trending-down':
        case 'expense':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M7 17L17 7M17 7H7M17 7V17" />
            </svg>
          );
        case 'arrow-down-left':
        case 'trending-up':
        case 'income':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 7L7 17M7 17H17M7 17V7" />
            </svg>
          );
        case 'plus-circle':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="16" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
          );
        case 'minus-circle':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
          );
        case 'chevron-right':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          );
        case 'eye':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          );
        case 'eye-off':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          );
        case 'lock':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="4" y="11" width="16" height="11" rx="2.5" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          );
        case 'settings':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="3" />
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
          );
        case 'plus':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          );
        case 'trash':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          );
        case 'edit':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
            </svg>
          );
        case 'backspace':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 4H8l-7 8 7 8h13a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2z" />
              <line x1="18" y1="9" x2="12" y2="15" />
              <line x1="12" y1="9" x2="18" y2="15" />
            </svg>
          );
        case 'download':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          );
        case 'upload':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          );
        case 'shield-check':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <polyline points="9 12 11 14 15 10" />
            </svg>
          );
        case 'target':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <circle cx="12" cy="12" r="6" />
              <circle cx="12" cy="12" r="2" />
            </svg>
          );
        case 'pie-chart':
        case 'chart':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
              <path d="M22 12A10 10 0 0 0 12 2v10z" />
            </svg>
          );
        case 'search':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
          );
        case 'award':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="8" r="7" />
              <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
            </svg>
          );
        case 'zap':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          );
        case 'check':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          );
        case 'check-circle':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          );
        case 'credit-card':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="5" width="20" height="14" rx="3" />
              <line x1="2" y1="10" x2="22" y2="10" />
            </svg>
          );
        case 'sparkles':
        case 'sparkle':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2l2.4 5 5 2.4-5 2.4-2.4 5-2.4-5-5-2.4 5-2.4z" />
              <path d="M19 15l1.2 2.5 2.5 1.2-2.5 1.2-1.2 2.5-1.2-2.5-2.5-1.2 2.5-1.2z" />
            </svg>
          );
        case 'layers':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
          );
        case 'chevron-down':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          );
        case 'chevron-up':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="18 15 12 9 6 15" />
            </svg>
          );
        case 'contactless':
        case 'wifi':
          return (
            <svg className={computedClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M8.5 16.5a5 5 0 0 1 0-9" />
              <path d="M12 19a8.5 8.5 0 0 0 0-14" />
              <path d="M15.5 21.5a12 12 0 0 0 0-19" />
            </svg>
          );
        case 'apple':
          return (
            <svg className={computedClass} viewBox="0 0 170 170" fill="currentColor">
              <path d="M150.37 130.25c-2.45 5.66-5.35 10.87-8.71 15.66-4.58 6.53-8.33 11.05-11.22 13.56-4.48 4.12-9.28 6.23-14.42 6.35-3.69 0-8.14-1.05-13.32-3.18-5.19-2.12-9.97-3.17-14.34-3.17-4.58 0-9.49 1.05-14.75 3.17-5.26 2.13-9.5 3.24-12.74 3.35-4.35.13-9.16-1.9-14.42-6.08-3.7-3.04-7.58-7.7-11.64-13.98-6.19-9.57-11.19-20.71-15-33.42-3.8-12.71-5.71-24.62-5.71-35.73 0-13.7 3.37-25.26 10.12-34.69 6.75-9.43 15.35-14.28 25.8-14.56 4.9.11 10.22 1.34 15.96 3.7 5.74 2.36 9.4 3.6 10.98 3.72 2.19-.24 6.23-1.66 12.13-4.25 5.9-2.6 11.28-3.79 16.14-3.58 11.75.64 21.43 5.09 29.04 13.34-10.45 6.33-15.56 15.22-15.32 26.68.25 9.07 3.68 16.7 10.3 22.89 6.62 6.19 14.52 9.77 23.7 10.74-2.58 7.64-5.83 15.38-9.75 23.21zM119.22 31.84c0-7.14 2.6-13.88 7.8-20.21 5.2-6.33 11.65-10.59 19.34-12.78.36 1.45.54 2.8.54 4.05 0 7.15-2.67 13.98-8.01 20.48-5.34 6.51-11.83 10.78-19.47 12.82-.12-1.46-.2-2.92-.2-4.36z"/>
            </svg>
          );
        case 'sun':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          );
        case 'moon':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          );
        case 'camera':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
          );
        case 'food':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8h1a4 4 0 0 1 0 8h-1M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
              <line x1="6" y1="1" x2="6" y2="4" />
              <line x1="10" y1="1" x2="10" y2="4" />
              <line x1="14" y1="1" x2="14" y2="4" />
            </svg>
          );
        case 'transport':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="12" rx="2" />
              <line x1="3" y1="10" x2="21" y2="10" />
              <circle cx="7" cy="18" r="2" />
              <circle cx="17" cy="18" r="2" />
            </svg>
          );
        case 'shopping':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <path d="M16 10a4 4 0 0 1-8 0" />
            </svg>
          );
        case 'bill':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          );
        case 'entertainment':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <polygon points="10 8 16 12 10 16 10 8" />
            </svg>
          );
        case 'health':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          );
        case 'salary':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" />
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
            </svg>
          );
        case 'gift':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 12 20 22 4 22 4 12" />
              <rect x="2" y="7" width="20" height="5" />
              <line x1="12" y1="22" x2="12" y2="7" />
              <path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z" />
              <path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z" />
            </svg>
          );
        case 'investment':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
              <polyline points="17 6 23 6 23 12" />
            </svg>
          );
        case 'duplicate':
        case 'copy':
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
          );
        case 'tag':
        default:
          return (
            <svg className={computedClass} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
              <line x1="7" y1="7" x2="7.01" y2="7" />
            </svg>
          );
      }
    };

    // Soft Circular or Rounded-Square Badge Wrapper
    const IconBadge = ({ icon, className = "p-2.5 rounded-2xl bg-sky-100 dark:bg-slate-800 text-sky-600 dark:text-sky-400 shrink-0", iconClass = "w-5 h-5", strokeWidth = 2 }) => {
      const isEmoji = typeof icon === 'string' && /\\p{Extended_Pictographic}/u.test(icon);
      return (
        <div className={`flex items-center justify-center select-none ${className}`}>
          {isEmoji ? (
            <span className="text-base leading-none select-none flex items-center justify-center">{icon}</span>
          ) : (
            <Icon name={icon} className={iconClass} strokeWidth={strokeWidth} />
          )}
        </div>
      );
    };

    // Dynamic Brand Logo Configuration (Voralet Brand Mark & Badge from 2.jpg)
    const APP_LOGO_SRC = ""; // Set image path, base64 or URL if custom logo asset is supplied

    // The signature double-wave mark from the Voralet logo in 2.jpg
    const VoraletWaves = ({ className = "w-full h-full", color = "#0099FF" }) => (
      <svg
        viewBox="0 0 100 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
      >
        {/* Upper flowing crest wave */}
        <path
          d="M 18 36 C 26 20, 36 14, 46 14 C 56 14, 62 26, 68 37 C 74 48, 80 36, 86 24"
          stroke={color}
          strokeWidth="8.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Lower nested fluid return wave */}
        <path
          d="M 29 47 C 32 38, 38 34, 42 34 C 48 34, 53 44, 60 54 C 67 64, 78 50, 86 24"
          stroke={color}
          strokeWidth="8.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );

    // Exact Voralet App Icon Squircle Badge as shown in 2.jpg (White squircle card with blue waves & blue Voralet text)
    const VoraletLogo = ({ 
      size = "md", 
      className = "", 
      rounded = "rounded-[28%]", 
      shadow = "shadow-[0_12px_36px_rgba(0,0,0,0.14)]" 
    }) => {
      const sizeMap = {
        xs: { card: "w-9 h-9 rounded-xl", waveStroke: "11", text: "text-[9px] font-black" },
        sm: { card: "w-11 h-11 rounded-2xl", waveStroke: "11.5", text: "text-[11px] font-black" },
        md: { card: "w-16 h-16 rounded-[20px]", waveStroke: "12", text: "text-xs font-black" },
        lg: { card: "w-24 h-24 rounded-[26px]", waveStroke: "12", text: "text-base font-black" },
        xl: { card: "w-32 h-32 rounded-[32px]", waveStroke: "12", text: "text-xl font-black" },
        splash: { card: "w-44 h-44 sm:w-48 sm:h-48 rounded-[44px]", waveStroke: "12", text: "text-2xl sm:text-3xl font-black" }
      };
      const cfg = sizeMap[size] || sizeMap.md;

      return (
        <div className={`relative aspect-square flex flex-col items-center justify-center bg-[#FFFFFF] ${shadow} overflow-hidden select-none ${cfg.card} ${className}`}>
          {/* Wave mark container */}
          <div className="w-[68%] h-[46%] flex items-center justify-center -mt-1 text-[#02A9FF]">
            <svg
              viewBox="0 0 100 70"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-full h-full"
            >
              {/* Upper flowing crest wave */}
              <path
                d="M 16 32 C 24 16, 36 10, 48 10 C 60 10, 66 22, 72 34 C 78 46, 84 32, 90 20"
                stroke="#02A9FF"
                strokeWidth={cfg.waveStroke}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              {/* Lower nested fluid return wave */}
              <path
                d="M 28 44 C 32 34, 40 28, 46 28 C 52 28, 58 40, 64 50 C 72 62, 82 46, 90 20"
                stroke="#02A9FF"
                strokeWidth={cfg.waveStroke}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          {/* Voralet text in rounded bold font */}
          <div className="w-full text-center mt-1">
            <span className={`text-[#02A9FF] font-['Inter',system-ui,sans-serif] tracking-tight leading-none select-none ${cfg.text}`}>
              Voralet
            </span>
          </div>
        </div>
      );
    };

    // VoraletBadge backwards-compatible wrapper pointing to official VoraletLogo
    const VoraletBadge = ({ className = "w-32 h-32", rounded = "rounded-[32%]", shadow = "shadow-[0_16px_48px_rgba(0,0,0,0.16)]" }) => (
      <VoraletLogo size="xl" className={className} rounded={rounded} shadow={shadow} />
    );

    const AppLogo = ({ 
      size = "md", 
      showText = true, 
      variant = "auto", // "auto" | "badge" | "mark"
      className = "", 
      textColor = "text-[#0099FF] dark:text-[#38BDF8]" 
    }) => {
      const sizeMap = {
        sm: { icon: "w-6 h-6", text: "text-base font-bold tracking-tight", badge: "w-9 h-9 rounded-xl" },
        md: { icon: "w-8 h-8", text: "text-lg font-bold tracking-tight", badge: "w-11 h-11 rounded-2xl" },
        lg: { icon: "w-12 h-12", text: "text-2xl font-extrabold tracking-tight", badge: "w-16 h-16 rounded-[20px]" },
        xl: { icon: "w-16 h-16", text: "text-3xl font-black tracking-tight", badge: "w-32 h-32 rounded-[32px]" }
      };
      const cfg = sizeMap[size] || sizeMap.md;

      if (variant === "badge" || (variant === "auto" && size === "xl" && !showText)) {
        return (
          <div className={`inline-flex items-center justify-center ${className}`}>
            <VoraletLogo size={size} className={cfg.badge} />
          </div>
        );
      }

      return (
        <div className={`inline-flex items-center gap-2 select-none ${className}`}>
          {APP_LOGO_SRC ? (
            <img src={APP_LOGO_SRC} alt="Voralet Logo" className={`${cfg.icon} object-contain`} />
          ) : (
            <div className={`${cfg.icon} flex-shrink-0 flex items-center justify-center text-[#02A9FF] dark:text-[#38BDF8] transition-transform duration-200`}>
              <VoraletWaves color="currentColor" />
            </div>
          )}
          {showText && (
            <span className={`${cfg.text} ${textColor} font-['Inter',sans-serif]`}>
              Voralet
            </span>
          )}
        </div>
      );
    };

    // iOS Interactive Swipe-to-Dismiss Handle for Bottom Sheets
    const ModalDragHandle = ({ onDismiss }) => {
      const startY = useRef(0);
      const isDragging = useRef(false);
      const handleRef = useRef(null);

      const handleTouchStart = (e) => {
        if (!e.touches || e.touches.length === 0) return;
        startY.current = e.touches[0].clientY;
        isDragging.current = true;
        const card = (handleRef.current && handleRef.current.closest) ? handleRef.current.closest('.ios-modal-card') : null;
        if (card) {
          card.style.transition = 'none';
        }
      };

      const handleTouchMove = (e) => {
        if (!isDragging.current || !e.touches || e.touches.length === 0) return;
        const delta = e.touches[0].clientY - startY.current;
        if (delta > 0) {
          const card = (handleRef.current && handleRef.current.closest) ? handleRef.current.closest('.ios-modal-card') : null;
          if (card) {
            card.style.transform = `translate3d(0, ${delta}px, 0)`;
          }
        }
      };

      const handleTouchEnd = (e) => {
        if (!isDragging.current) return;
        isDragging.current = false;
        const card = (handleRef.current && handleRef.current.closest) ? handleRef.current.closest('.ios-modal-card') : null;
        const endY = e.changedTouches && e.changedTouches[0] ? e.changedTouches[0].clientY : startY.current;
        const delta = endY - startY.current;

        if (card) {
          if (delta > 70) {
            card.style.transition = 'transform 0.22s cubic-bezier(0.32, 0.72, 0, 1)';
            card.style.transform = 'translate3d(0, 100%, 0)';
            setTimeout(() => {
              if (typeof onDismiss === 'function') onDismiss();
            }, 200);
          } else {
            card.style.transition = 'transform 0.28s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            card.style.transform = 'translate3d(0, 0, 0)';
          }
        } else if (delta > 70) {
          if (typeof onDismiss === 'function') onDismiss();
        }
      };

      return (
        <div
          ref={handleRef}
          className="w-full pt-2 pb-1 flex justify-center items-center cursor-grab active:cursor-grabbing touch-none select-none"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          title="Geser ke bawah untuk menutup"
        >
          <div className="w-12 h-1.5 bg-slate-300 dark:bg-slate-600 rounded-full mx-auto my-2 transition-colors" />
        </div>
      );
    };

    // Apple-Style Modal Close Button with exact inline SVG
    const ModalCloseButton = ({ onClick, ariaLabel = "Tutup" }) => {
      return (
        <button
          type="button"
          onClick={onClick}
          className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap shrink-0"
          aria-label={ariaLabel}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 flex-shrink-0 aspect-square">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      );
    };

    // =========================================================================
    // REUSABLE UI PRIMITIVES (Apple Human Interface Design Language)
    // =========================================================================
    const Button = ({
      children,
      onClick,
      type = "button",
      variant = "primary",
      size = "md",
      icon = null,
      iconPosition = "left",
      disabled = false,
      loading = false,
      fullWidth = false,
      className = "",
      ...props
    }) => {
      const variantClasses = {
        primary: "bg-[#0284C7] hover:bg-[#0369A1] text-white shadow-sm",
        secondary: "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700",
        outline: "border border-slate-200 dark:border-slate-700 bg-transparent text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800",
        danger: "bg-rose-600 hover:bg-rose-700 text-white shadow-sm",
        emerald: "bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm",
        ghost: "bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
      };

      const sizeClasses = {
        sm: "px-3 py-1.5 text-xs rounded-xl gap-1.5",
        md: "px-4 py-2.5 text-xs font-bold rounded-xl gap-2",
        lg: "px-5 py-3.5 text-sm font-bold rounded-2xl gap-2.5"
      };

      return (
        <button
          type={type}
          onClick={onClick}
          disabled={disabled || loading}
          className={`inline-flex items-center justify-center font-semibold transition-all ios-btn-tap select-none ${
            variantClasses[variant] || variantClasses.primary
          } ${sizeClasses[size] || sizeClasses.md} ${fullWidth ? "w-full" : ""} ${
            disabled ? "opacity-50 cursor-not-allowed pointer-events-none" : ""
          } ${className}`}
          {...props}
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              {icon && iconPosition === "left" && <Icon name={icon} className="w-4 h-4" strokeWidth={2.4} />}
              {children}
              {icon && iconPosition === "right" && <Icon name={icon} className="w-4 h-4" strokeWidth={2.4} />}
            </>
          )}
        </button>
      );
    };

    const InputField = ({
      label,
      value,
      onChange,
      type = "text",
      placeholder = "",
      error = "",
      hint = "",
      required = false,
      autoFocus = false,
      prefix = null,
      icon = null,
      className = "",
      inputClassName = "",
      ...props
    }) => {
      return (
        <div className={`space-y-1 ${className}`}>
          {label && (
            <label className="block text-xs font-semibold text-slate-800 dark:text-slate-200">
              {label} {required && <span className="text-rose-500">*</span>}
            </label>
          )}
          <div className="relative flex items-center">
            {prefix && (
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 font-mono text-sm font-bold select-none">
                {prefix}
              </span>
            )}
            {icon && !prefix && (
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 select-none">
                <Icon name={icon} className="w-4 h-4" />
              </span>
            )}
            <input
              type={type}
              value={value}
              onChange={onChange}
              placeholder={placeholder}
              required={required}
              autoFocus={autoFocus}
              onFocus={handleGlobalInputFocus}
              onBlur={handleGlobalInputBlur}
              className={`w-full py-2.5 rounded-xl border bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-xs font-medium focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors ${
                prefix ? "pl-8 pr-3.5" : icon ? "pl-10 pr-3.5" : "px-3.5"
              } ${error ? "border-rose-400 dark:border-rose-500" : "border-slate-200 dark:border-slate-700"} ${inputClassName}`}
              {...props}
            />
          </div>
          {hint && !error && <p className="text-[11px] text-slate-400">{hint}</p>}
          {error && <p className="text-[11px] font-semibold text-rose-500">{error}</p>}
        </div>
      );
    };

    const Card = ({ children, className = "", onClick, ...props }) => {
      return (
        <div
          onClick={onClick}
          className={`ios-inset-group ${onClick ? "cursor-pointer ios-card-tap" : ""} ${className}`}
          {...props}
        >
          {children}
        </div>
      );
    };

    // Resilient Error Boundary to safeguard against render crashes
    class ErrorBoundary extends React.Component {
      constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
      }
      static getDerivedStateFromError(error) {
        return { hasError: true, error };
      }
      componentDidCatch(error, errorInfo) {
        // Silently capture error for application resilience
      }
      render() {
        if (this.state.hasError) {
          if (this.props.fallback) return this.props.fallback;
          return (
            <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-300 text-xs text-center my-3">
              <p className="font-bold">Gagal memuat komponen ini</p>
              <button
                type="button"
                onClick={() => this.setState({ hasError: false, error: null })}
                className="mt-2 px-3 py-1 bg-amber-200 dark:bg-amber-900/60 rounded-lg font-semibold ios-btn-tap"
              >
                Muat Ulang
              </button>
            </div>
          );
        }
        return this.props.children;
      }
    }
"""
