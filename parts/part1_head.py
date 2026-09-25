HTML_HEAD = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>Voralet - Authentic iOS Personal Finance</title>
  <meta name="description" content="Aplikasi pencatat keuangan pribadi modern ala iOS dengan brankas PIN lokal dan pelacak hutang piutang." />
  
  <!-- Apple HIG & PWA Pure White Card Home Screen Icons (NO outer blue frame) -->
  <link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180' width='180' height='180'%3E%3Crect width='180' height='180' fill='%23FFFFFF'/%3E%3Cpath d='M 32 72 C 44 44, 66 32, 88 32 C 110 32, 120 54, 132 78 C 142 98, 154 74, 164 50' fill='none' stroke='%2302A9FF' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M 54 94 C 62 76, 76 66, 88 66 C 100 66, 110 88, 122 108 C 136 128, 152 98, 164 50' fill='none' stroke='%2302A9FF' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ctext x='90' y='152' text-anchor='middle' fill='%2302A9FF' font-family='-apple-system, BlinkMacSystemFont, Inter, sans-serif' font-weight='800' font-size='34'%3EVoralet%3C/text%3E%3C/svg%3E" />
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180' width='180' height='180'%3E%3Crect width='180' height='180' fill='%23FFFFFF'/%3E%3Cpath d='M 32 72 C 44 44, 66 32, 88 32 C 110 32, 120 54, 132 78 C 142 98, 154 74, 164 50' fill='none' stroke='%2302A9FF' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M 54 94 C 62 76, 76 66, 88 66 C 100 66, 110 88, 122 108 C 136 128, 152 98, 164 50' fill='none' stroke='%2302A9FF' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ctext x='90' y='152' text-anchor='middle' fill='%2302A9FF' font-family='-apple-system, BlinkMacSystemFont, Inter, sans-serif' font-weight='800' font-size='34'%3EVoralet%3C/text%3E%3C/svg%3E" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="default" />
  <meta name="theme-color" content="#FFFFFF" />
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS Configuration (MANDATORY BEFORE CDN SCRIPT FOR darkMode: 'class') -->
  <script>
    window.tailwind = {
      config: {
        darkMode: 'class',
        theme: {
          extend: {
            colors: {
              brand: {
                DEFAULT: '#0284C7',
                hover: '#0369A1',
                light: '#E0F2FE',
                soft: '#F0F9FF',
                dark: '#0284C7'
              },
              sky: {
                50: '#F0F9FF',
                100: '#E0F2FE',
                200: '#BAE6FD',
                300: '#7DD3FC',
                400: '#38BDF8',
                500: '#0EA5E9',
                600: '#0284C7',
                700: '#0369A1',
                800: '#075985',
                900: '#0C4A6E'
              },
              slate: {
                950: '#020617',
                900: '#0F172A', // Dark Mode Main Background
                850: '#151F32',
                800: '#1E293B', // Dark Mode Cards / Containers
                750: '#293548',
                700: '#334155', // Dark Mode Borders
                600: '#475569',
                500: '#64748B', // Secondary Text Light Mode
                400: '#94A3B8', // Secondary Text Dark Mode
                300: '#CBD5E1',
                200: '#E2E8F0',
                100: '#F1F5F9',
                50: '#F8FAFC'  // Primary Text Dark Mode
              }
            },
            fontFamily: {
              sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'Segoe UI', 'Roboto', 'sans-serif']
            }
          }
        }
      }
    };
  </script>
  <!-- Tailwind CSS (Local asset with CDN fallback) -->
  <script src="./vendor/tailwindcss.js"></script>
  <script>
    if (!window.tailwind) {
      document.write('<script src="https://cdn.tailwindcss.com"><\/script>');
    }
  </script>
  <script>
    if (window.tailwind) {
      window.tailwind.config = window.tailwind.config || {};
      window.tailwind.config.darkMode = 'class';
    }
  </script>

  <!-- React 18 & ReactDOM 18 & Babel Standalone (Local assets with CDN fallback) -->
  <script src="./vendor/react.production.min.js"></script>
  <script>
    if (!window.React) {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"><\/script>');
    }
  </script>
  <script src="./vendor/react-dom.production.min.js"></script>
  <script>
    if (!window.ReactDOM) {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"><\/script>');
    }
  </script>
  <script src="./vendor/babel.min.js"></script>
  <script>
    if (!window.Babel) {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.4/babel.min.js"><\/script>');
    }
  </script>
  <script>
    // Configure Babel to suppress deoptimisation warnings on large bundled inline scripts
    try {
      if (window.Babel && window.Babel.transform) {
        // Suppress compact warning for scripts > 500KB
        const originalTransform = window.Babel.transform;
        window.Babel.transform = function(code, opts) {
          opts = opts || {};
          if (opts.compact === undefined) opts.compact = false;
          return originalTransform.call(this, code, opts);
        };
      }
    } catch (e) {}
  </script>

  <!-- html2pdf.js for Client-Side PDF Generation (Local asset with CDN fallback) -->
  <script src="./vendor/html2pdf.bundle.min.js"></script>
  <script>
    if (!window.html2pdf) {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"><\/script>');
    }
  </script>

  <!-- Theme Synchronization Initialization -->
  <script>
    (function() {
      try {
        const savedTheme = localStorage.getItem('voralet_theme');
        const mediaQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
        const prefersDark = mediaQuery ? mediaQuery.matches : false;
        const initialTheme = (savedTheme === 'dark' || savedTheme === 'light')
          ? savedTheme
          : (prefersDark ? 'dark' : 'light');

        if (initialTheme === 'dark') {
          document.documentElement.classList.add('dark');
          if (document.body) document.body.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
          if (document.body) document.body.classList.remove('dark');
        }
      } catch (e) {
        document.documentElement.classList.remove('dark');
      }
    })();
  </script>

  <!-- Haptic & Vibration Feedback Engine - Disabled per user request -->
  <script>
    (function() {
      // Unified Voralet Haptics Engine - Completely silent
      window.VoraletHaptics = {
        trigger: function() {},
        tap: function() {},
        pinKey: function() {},
        pinBackspace: function() {},
        pinSuccess: function() {},
        pinError: function() {},
        save: function() {},
        delete: function() {},
        selection: function() {}
      };
    })();
  </script>

  <style>
    :root {
      --ios-ease: cubic-bezier(0.25, 1, 0.5, 1);
      --ios-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
      --ios-bouncy: cubic-bezier(0.34, 1.68, 0.64, 1);
      --ios-fluid: cubic-bezier(0.16, 1, 0.3, 1);
      --ios-snap: cubic-bezier(0.2, 0.9, 0.3, 1);
      --ios-overshoot: cubic-bezier(0.175, 0.885, 0.32, 1.275);
      --glass-light-bg: rgba(255, 255, 255, 0.84);
      --glass-light-border: rgba(255, 255, 255, 0.82);
      --glass-dark-bg: rgba(30, 41, 59, 0.82);
      --glass-dark-border: rgba(255, 255, 255, 0.16);
    }
    * {
      -webkit-tap-highlight-color: transparent;
      box-sizing: border-box;
    }
    html, body {
      height: 100%;
      width: 100%;
      margin: 0;
      padding: 0;
      overscroll-behavior-y: contain;
      -webkit-overflow-scrolling: touch;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
      background-color: #F8FAFC;
      color: #0F172A;
      transition: background-color 300ms ease-in-out, color 300ms ease-in-out;
    }
    html.dark body, body.dark {
      background-color: #0F172A !important;
      color: #F8FAFC !important;
    }
    #root {
      height: 100%;
      width: 100%;
      overflow: hidden;
      background: transparent;
      color: #0F172A;
      position: relative;
    }
    html.dark #root {
      background: transparent !important;
      color: #F8FAFC !important;
    }

    /* iOS 26 Dynamic Ambient Liquid Glass Canvas (Composited Background) */
    .ios-liquid-bg {
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 0;
      overflow: hidden;
      background: #F8FAFC;
      transform: translateZ(0);
      will-change: transform;
    }
    .ios-liquid-orb-1, .ios-liquid-orb-2 {
      display: none !important;
    }
    .dark .ios-liquid-bg, html.dark .ios-liquid-bg {
      background: #0F172A !important;
    }

    /* iOS Inset Grouped Block - Clean Flat Solid Surfaces (Zero Gradients) */
    .ios-inset-group, .ios-liquid-glass {
      position: relative;
      border-radius: 24px;
      background: #FFFFFF;
      padding: 1.15rem;
      border: 1px solid #E2E8F0;
      box-shadow: 0 2px 8px -1px rgba(15, 23, 42, 0.04);
      transition: background 250ms ease, border-color 250ms ease, color 250ms ease;
      contain: layout style;
      transform: translateZ(0);
      will-change: transform;
    }
    .dark .ios-inset-group, html.dark .ios-inset-group,
    .dark .ios-liquid-glass, html.dark .ios-liquid-glass {
      background: #1E293B !important;
      border: 1px solid #334155 !important;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45) !important;
      color: #F8FAFC !important;
    }

    /* iOS Flat Pill & Tag Badges - Zero Gradients */
    .ios-glass-pill {
      background: #F0F9FF;
      border: 1px solid #BAE6FD;
      box-shadow: 0 2px 6px -1px rgba(2, 132, 199, 0.08);
    }
    .dark .ios-glass-pill, html.dark .ios-glass-pill {
      background: #1E293B !important;
      border: 1px solid #334155 !important;
      box-shadow: 0 2px 8px -1px rgba(0, 0, 0, 0.35) !important;
    }

    /* iOS Floating & Capsule Shadows */
    .ios-drop-shadow {
      box-shadow: 0 8px 24px -4px rgba(2, 132, 199, 0.12), 0 2px 8px -2px rgba(15, 23, 42, 0.05);
    }
    .dark .ios-drop-shadow {
      box-shadow: 0 10px 28px -4px rgba(0, 0, 0, 0.65), 0 2px 8px -2px rgba(0, 0, 0, 0.4);
    }
    .ios-nav-shadow {
      box-shadow: 0 16px 40px -6px rgba(15, 23, 42, 0.2), 0 4px 16px -2px rgba(15, 23, 42, 0.08);
    }
    .dark .ios-nav-shadow {
      box-shadow: 0 20px 44px -6px rgba(0, 0, 0, 0.8), 0 4px 18px -2px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.08);
    }

    /* Hairline Divider */
    .ios-hairline {
      border-bottom: 1px solid rgba(226, 232, 240, 0.8);
      transition: border-color 300ms ease-in-out;
    }
    .dark .ios-hairline, html.dark .ios-hairline {
      border-bottom: 1px solid rgba(51, 65, 85, 0.8) !important;
    }

    /* Bulletproof Fallbacks for Dark Mode */
    html.dark, html.dark body, body.dark, html.dark #root, .dark #root {
      background-color: #0F172A !important;
      color: #F8FAFC !important;
    }
    .dark .bg-slate-50, html.dark .bg-slate-50 {
      background-color: #0F172A !important;
    }
    .dark .bg-white, html.dark .bg-white {
      background-color: #1E293B !important;
      color: #F8FAFC !important;
    }
    .dark .text-slate-900, html.dark .text-slate-900,
    .dark .text-slate-800, html.dark .text-slate-800 {
      color: #F8FAFC !important;
    }
    .dark .text-slate-700, html.dark .text-slate-700,
    .dark .text-slate-600, html.dark .text-slate-600 {
      color: #CBD5E1 !important;
    }
    .dark .border-slate-200, html.dark .border-slate-200,
    .dark .border-slate-100, html.dark .border-slate-100 {
      border-color: #334155 !important;
    }

    /* Scrollbar hide */
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }

    /* Tactile Touch Animation (Authentic Apple iOS Bouncy Spring Physics 120 FPS) */
    .ios-btn-tap, .ios-touch-item {
      transition: transform 0.44s cubic-bezier(0.34, 1.68, 0.64, 1), opacity 0.16s ease;
      user-select: none;
      -webkit-user-select: none;
      will-change: transform;
      transform: translate3d(0, 0, 0);
      touch-action: manipulation;
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .ios-btn-tap:active, .ios-touch-item:active {
      transform: scale3d(0.92, 0.92, 1) translate3d(0, 0, 0) !important;
      opacity: 0.78;
      transition: transform 0.08s cubic-bezier(0.25, 0.1, 0.25, 1), opacity 0.08s ease;
    }
    .ios-card-tap {
      transition: transform 0.46s cubic-bezier(0.34, 1.68, 0.64, 1), opacity 0.18s ease, box-shadow 0.35s ease;
      user-select: none;
      -webkit-user-select: none;
      will-change: transform, box-shadow;
      transform: translate3d(0, 0, 0);
      touch-action: manipulation;
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .ios-card-tap:active {
      transform: scale3d(0.95, 0.95, 1) translate3d(0, 0, 0) !important;
      opacity: 0.88;
      box-shadow: 0 4px 12px -2px rgba(2, 132, 199, 0.15) !important;
      transition: transform 0.08s cubic-bezier(0.25, 0.1, 0.25, 1), opacity 0.08s ease;
    }

    /* Navigation, view transitions, and bottom sheets */
    .ios-view-transition, .animate-ios-tab-view {
      transition: transform 0.34s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.26s cubic-bezier(0.32, 0.72, 0, 1);
      will-change: transform, opacity;
      transform: translate3d(0, 0, 0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    /* Apple Wallet Dynamic Card Stack & Motion */
    .apple-wallet-card-collapsed {
      height: 74px;
      border-radius: 1.25rem;
      position: relative;
      overflow: hidden;
      background-color: #38bdf8;
      box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.18), inset 0 1px 1px rgba(255, 255, 255, 0.35);
      transition: height 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease;
      will-change: height;
      transform: translateZ(0);
    }
    .apple-wallet-card-expanded {
      height: 195px;
      border-radius: 1.35rem;
      position: relative;
      overflow: hidden;
      background-color: #38bdf8;
      box-shadow: 0 16px 36px -8px rgba(0, 0, 0, 0.38), 0 0 0 2px rgba(255, 255, 255, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.4);
      transition: height 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease;
      will-change: height;
      transform: translateZ(0);
    }
    @media (min-width: 640px) {
      .apple-wallet-card-expanded {
        height: 210px;
        border-radius: 1.5rem;
      }
    }
    .apple-atm-shimmer {
      display: none !important;
    }
    .apple-card-emboss {
      text-shadow: 0 1px 1px rgba(0, 0, 0, 0.4), 0 -1px 0 rgba(255, 255, 255, 0.2);
    }

    /* CardsView Card Stack Spring-Based Lift Animation & Depth (Authentic Apple Wallet Bouncy Physics) */
    .ios-card-stack-item {
      position: relative;
      transition: transform 0.48s cubic-bezier(0.34, 1.68, 0.64, 1), 
                  box-shadow 0.45s cubic-bezier(0.34, 1.56, 0.64, 1), 
                  opacity 0.32s ease, 
                  filter 0.32s ease;
      will-change: transform, box-shadow;
      transform-origin: center center;
      touch-action: pan-y;
      -webkit-backface-visibility: hidden;
      backface-visibility: hidden;
    }
    .ios-card-stack-item.is-lifted {
      animation: iosWalletCardSpringLift 0.46s cubic-bezier(0.34, 1.68, 0.64, 1) forwards;
      box-shadow: 0 24px 48px -10px rgba(2, 132, 199, 0.45), 
                  0 10px 22px -4px rgba(0, 0, 0, 0.22), 
                  0 0 0 1.5px rgba(255, 255, 255, 0.65),
                  inset 0 1.5px 2px rgba(255, 255, 255, 0.55);
      z-index: 30 !important;
    }
    @keyframes iosWalletCardSpringLift {
      0% {
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
      45% {
        transform: translate3d(0, -13px, 0) scale3d(1.034, 1.034, 1);
      }
      75% {
        transform: translate3d(0, -8px, 0) scale3d(1.020, 1.020, 1);
      }
      100% {
        transform: translate3d(0, -9px, 0) scale3d(1.026, 1.026, 1);
      }
    }
    html.dark .ios-card-stack-item.is-lifted, .dark .ios-card-stack-item.is-lifted {
      box-shadow: 0 26px 52px -10px rgba(0, 0, 0, 0.78), 
                  0 12px 26px -4px rgba(3, 105, 161, 0.48), 
                  0 0 0 1.5px rgba(56, 189, 248, 0.55),
                  inset 0 1.5px 2px rgba(255, 255, 255, 0.35);
    }
    .ios-card-stack-item.is-dimmed {
      animation: iosWalletCardSpringStackDown 0.42s cubic-bezier(0.34, 1.68, 0.64, 1) forwards;
      opacity: 0.82;
      filter: brightness(0.93) saturate(0.9);
      box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.12);
    }
    @keyframes iosWalletCardSpringStackDown {
      0% {
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
      50% {
        transform: translate3d(0, 8px, 0) scale3d(0.965, 0.965, 1);
      }
      100% {
        transform: translate3d(0, 5px, 0) scale3d(0.976, 0.976, 1);
      }
    }
    html.dark .ios-card-stack-item.is-dimmed, .dark .ios-card-stack-item.is-dimmed {
      filter: brightness(0.85) saturate(0.88);
    }
    .ios-card-stack-item:active:not(.is-lifted):not(.is-dragging) {
      transform: translate3d(0, 2px, 0) scale3d(0.978, 0.978, 1);
      transition-duration: 0.1s;
    }

    /* CardsView Drag & Drop Reordering & Apple Wallet Floating Physics */
    .ios-card-stack-item.is-dragging {
      opacity: 0.96;
      animation: iosWalletCardFloat 0.32s cubic-bezier(0.34, 1.68, 0.64, 1) forwards;
      box-shadow: 0 32px 60px -12px rgba(2, 132, 199, 0.55),
                  0 14px 28px -6px rgba(0, 0, 0, 0.30),
                  0 0 0 2px rgba(255, 255, 255, 0.95),
                  inset 0 1px 3px rgba(255, 255, 255, 0.65) !important;
      z-index: 60 !important;
      cursor: grabbing !important;
      transition: box-shadow 0.2s ease, opacity 0.2s ease !important;
    }
    @keyframes iosWalletCardFloat {
      0% {
        transform: scale3d(1, 1, 1) rotate(0deg);
      }
      55% {
        transform: scale3d(1.048, 1.048, 1) translate3d(0, -6px, 0) rotate(-1.6deg);
      }
      100% {
        transform: scale3d(1.040, 1.040, 1) translate3d(0, -4px, 0) rotate(-1.1deg);
      }
    }
    html.dark .ios-card-stack-item.is-dragging, .dark .ios-card-stack-item.is-dragging {
      box-shadow: 0 34px 64px -12px rgba(0, 0, 0, 0.88),
                  0 16px 32px -6px rgba(3, 105, 161, 0.55),
                  0 0 0 2px rgba(56, 189, 248, 0.85),
                  inset 0 1px 3px rgba(255, 255, 255, 0.45) !important;
    }
    .ios-card-stack-item.is-settling {
      animation: iosWalletDropSettle 0.45s cubic-bezier(0.34, 1.68, 0.64, 1) forwards;
    }
    @keyframes iosWalletDropSettle {
      0% {
        transform: scale3d(1.04, 1.04, 1) translate3d(0, -4px, 0) rotate(-1.1deg);
      }
      45% {
        transform: scale3d(0.975, 0.975, 1) translate3d(0, 3px, 0) rotate(0.5deg);
      }
      75% {
        transform: scale3d(1.008, 1.008, 1) translate3d(0, -1px, 0) rotate(-0.15deg);
      }
      100% {
        transform: scale3d(1, 1, 1) translate3d(0, 0, 0) rotate(0deg);
      }
    }
    .ios-card-stack-item.is-drag-target {
      transform: scale3d(0.985, 0.985, 1) translate3d(0, 2px, 0);
      opacity: 0.76;
      outline: 2.5px dashed rgba(2, 132, 199, 0.7);
      outline-offset: 4px;
      transition: transform 0.3s cubic-bezier(0.34, 1.68, 0.64, 1), outline 0.2s ease;
    }
    html.dark .ios-card-stack-item.is-drag-target {
      outline-color: rgba(56, 189, 248, 0.8);
    }
    .ios-wallet-drawer {
      animation: iosWalletDrawerOpen 0.42s cubic-bezier(0.34, 1.68, 0.64, 1) forwards;
      will-change: transform, opacity;
      transform-origin: top center;
    }
    @keyframes iosWalletDrawerOpen {
      0% {
        opacity: 0;
        transform: translate3d(0, -10px, 0) scale3d(0.97, 0.97, 1);
      }
      65% {
        opacity: 1;
        transform: translate3d(0, 2.5px, 0) scale3d(1.008, 1.008, 1);
      }
      100% {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
    }
    .ios-card-drop-indicator {
      height: 4px;
      margin: -2px 10px;
      border-radius: 9999px;
      background: #0284C7;
      box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
      z-index: 45;
      pointer-events: none;
    }

    /* Transaction Search Bar Expand & Collapse Animation */
    .tx-search-container {
      transition: all 0.32s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: transform, box-shadow, flex;
    }
    .tx-search-container.is-focused {
      flex: 1 1 100% !important;
      transform: scale3d(1.008, 1.008, 1);
    }
    .tx-search-container input {
      transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .tx-search-container.is-focused input {
      box-shadow: 0 4px 14px -2px rgba(2, 132, 199, 0.22),
                  0 0 0 3px rgba(56, 189, 248, 0.25);
      border-color: #0284C7 !important;
    }
    html.dark .tx-search-container.is-focused input, .dark .tx-search-container.is-focused input {
      box-shadow: 0 4px 18px -2px rgba(3, 105, 161, 0.35),
                  0 0 0 3px rgba(56, 189, 248, 0.3);
      border-color: #38BDF8 !important;
    }
    .tx-search-sibling-btn {
      transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      will-change: opacity, transform, max-width, margin, padding;
    }
    .tx-search-sibling-btn.is-compact {
      opacity: 0.88;
      transform: scale(0.96);
    }

    /* iOS Theme Cross-Fade Transition Overlay */
    .ios-theme-crossfade-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 99999;
      animation: iosThemeCrossfade 380ms cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: opacity;
      transform: translateZ(0);
    }
    .ios-theme-crossfade-overlay.from-light {
      background: #F8FAFC;
    }
    .ios-theme-crossfade-overlay.from-dark {
      background: #0F172A;
    }
    @keyframes iosThemeCrossfade {
      0% {
        opacity: 0.95;
      }
      100% {
        opacity: 0;
      }
    }

    /* Active cross-fade global smoothing during theme transitions */
    .theme-crossfade-active,
    .theme-crossfade-active *,
    .theme-crossfade-active *::before,
    .theme-crossfade-active *::after {
      transition: background-color 380ms cubic-bezier(0.32, 0.72, 0, 1),
                  border-color 380ms cubic-bezier(0.32, 0.72, 0, 1),
                  color 380ms cubic-bezier(0.32, 0.72, 0, 1),
                  fill 380ms cubic-bezier(0.32, 0.72, 0, 1),
                  stroke 380ms cubic-bezier(0.32, 0.72, 0, 1),
                  box-shadow 380ms cubic-bezier(0.32, 0.72, 0, 1) !important;
    }

    /* Browser View Transitions API cross-fade overlay specs */
    ::view-transition-old(root) {
      animation: 380ms cubic-bezier(0.32, 0.72, 0, 1) both iosViewTransitionFadeOut;
    }
    ::view-transition-new(root) {
      animation: 380ms cubic-bezier(0.32, 0.72, 0, 1) both iosViewTransitionFadeIn;
    }
    @keyframes iosViewTransitionFadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
    @keyframes iosViewTransitionFadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    /* Keypad Button with iOS Spring Physics */
    .ios-keypad-btn {
      transition: transform 0.36s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.18s ease, background-color 0.2s ease;
      touch-action: manipulation;
      user-select: none;
      -webkit-user-select: none;
      will-change: transform, opacity;
      transform: translate3d(0, 0, 0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .ios-keypad-btn:active {
      transform: scale3d(0.88, 0.88, 1) translate3d(0, 0, 0) !important;
      opacity: 0.70;
      transition: transform 0.06s cubic-bezier(0.2, 0, 0, 1), opacity 0.06s ease;
    }

    /* iOS Native Modal Sheet Stacking Layer (Hardware composited, zero re-layout) */
    .ios-modal-depth-layer {
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .ios-modal-depth-stacked {
      opacity: 0.98;
    }

    /* Ultra-Smooth Spring Pop for Dialogs & Alert Toasts */
    @keyframes iosSpringPop {
      0% {
        transform: scale3d(0.85, 0.85, 1) translate3d(0, 0, 0);
        opacity: 0;
      }
      70% {
        transform: scale3d(1.03, 1.03, 1) translate3d(0, 0, 0);
        opacity: 1;
      }
      100% {
        transform: scale3d(1, 1, 1) translate3d(0, 0, 0);
        opacity: 1;
      }
    }
    .animate-ios-spring-pop {
      animation: iosSpringPop 0.38s cubic-bezier(0.34, 1.68, 0.64, 1) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    /* iOS Modal & Sheet Keyframes (Luxurious Relaxed Bouncy Spring Physics) */
    @keyframes iosSheetEnter {
      0% {
        transform: translate3d(0, 100%, 0);
        opacity: 0.2;
      }
      64% {
        transform: translate3d(0, -10px, 0);
        opacity: 1;
      }
      84% {
        transform: translate3d(0, 2px, 0);
      }
      100% {
        transform: translate3d(0, 0, 0);
        opacity: 1;
      }
    }
    @keyframes iosSheetExit {
      0% {
        transform: translate3d(0, 0, 0);
        opacity: 1;
      }
      100% {
        transform: translate3d(0, 100%, 0);
        opacity: 0;
      }
    }
    @keyframes iosBackdropFadeIn {
      0% { opacity: 0; }
      100% { opacity: 1; }
    }
    @keyframes iosBackdropFadeOut {
      0% { opacity: 1; }
      100% { opacity: 0; }
    }
    .animate-ios-sheet {
      animation: iosSheetEnter 0.58s cubic-bezier(0.28, 1.15, 0.42, 1) forwards;
      will-change: transform;
      transform: translateZ(0);
      -webkit-backface-visibility: hidden;
      backface-visibility: hidden;
    }
    .animate-ios-sheet-exit {
      animation: iosSheetExit 0.38s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: transform;
      transform: translateZ(0);
      -webkit-backface-visibility: hidden;
      backface-visibility: hidden;
    }
    .animate-ios-backdrop {
      animation: iosBackdropFadeIn 0.45s cubic-bezier(0.25, 1, 0.5, 1) forwards;
      will-change: opacity;
      transform: translateZ(0);
    }
    .animate-ios-backdrop-exit {
      animation: iosBackdropFadeOut 0.32s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: opacity;
      transform: translateZ(0);
    }

    /* iOS Navigation & Tab Slide View Transitions (Silky Snappy 120 FPS) */
    @keyframes iosTabSlideForward {
      0% {
        opacity: 0;
        transform: translate3d(36px, 0, 0) scale3d(0.96, 0.96, 1);
      }
      70% {
        transform: translate3d(-4px, 0, 0) scale3d(1.008, 1.008, 1);
      }
      88% {
        transform: translate3d(1.5px, 0, 0) scale3d(0.998, 0.998, 1);
      }
      100% {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
    }
    @keyframes iosTabSlideBackward {
      0% {
        opacity: 0;
        transform: translate3d(-36px, 0, 0) scale3d(0.96, 0.96, 1);
      }
      70% {
        transform: translate3d(4px, 0, 0) scale3d(1.008, 1.008, 1);
      }
      88% {
        transform: translate3d(-1.5px, 0, 0) scale3d(0.998, 0.998, 1);
      }
      100% {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
    }
    @keyframes iosTabFadeIn {
      0% {
        opacity: 0;
        transform: scale3d(0.97, 0.97, 1) translate3d(0, 8px, 0);
      }
      75% {
        transform: scale3d(1.005, 1.005, 1) translate3d(0, -2px, 0);
      }
      100% {
        opacity: 1;
        transform: scale3d(1, 1, 1) translate3d(0, 0, 0);
      }
    }
    .animate-ios-tab-slide-forward {
      animation: iosTabSlideForward 0.36s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .animate-ios-tab-slide-backward {
      animation: iosTabSlideBackward 0.36s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .animate-ios-tab-view {
      animation: iosTabFadeIn 0.34s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    /* Transaction List Layout Animations (Hardware Accelerated) */
    @keyframes dashboardCardEntry {
      0% {
        opacity: 0;
        transform: translate3d(0, 14px, 0) scale3d(0.985, 0.985, 1);
      }
      100% {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
    }
    .animate-dashboard-card {
      animation: dashboardCardEntry 0.32s cubic-bezier(0.28, 0.84, 0.42, 1) both;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    @keyframes valuePulseHighlight {
      0% { transform: scale(1); }
      40% { transform: scale(1.025); }
      100% { transform: scale(1); }
    }
    .animate-value-pulse {
      animation: valuePulseHighlight 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-block;
      will-change: transform;
      transform: translateZ(0);
    }

    @keyframes txCardEntry {
      0% {
        opacity: 0;
        transform: translate3d(0, 10px, 0) scale3d(0.99, 0.99, 1);
      }
      100% {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale3d(1, 1, 1);
      }
    }
    .animate-tx-card-entry {
      animation: txCardEntry 0.28s cubic-bezier(0.28, 0.84, 0.42, 1) both;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    @keyframes txSlideIn {
      0% {
        opacity: 0;
        max-height: 0px;
        transform: translate3d(0, -14px, 0) scale(0.96);
      }
      60% {
        opacity: 0.9;
        max-height: 82px;
        transform: translate3d(0, 2px, 0) scale(1.01);
      }
      100% {
        opacity: 1;
        max-height: 82px;
        transform: translate3d(0, 0, 0) scale(1);
      }
    }
    .animate-tx-slide-in {
      animation: txSlideIn 0.42s cubic-bezier(0.175, 0.885, 0.32, 1.2) forwards;
      overflow: hidden;
      will-change: transform, opacity, max-height;
    }

    @keyframes txFadeOut {
      0% {
        opacity: 1;
        max-height: 82px;
        transform: translate3d(0, 0, 0) scale(1);
      }
      30% {
        opacity: 0.65;
        transform: translate3d(14px, 0, 0) scale(0.98);
      }
      65% {
        opacity: 0;
        transform: translate3d(32px, 0, 0) scale(0.94);
        max-height: 48px;
      }
      100% {
        opacity: 0;
        max-height: 0px;
        padding-top: 0px;
        padding-bottom: 0px;
        margin-top: 0px;
        margin-bottom: 0px;
        transform: translate3d(40px, 0, 0) scale(0.9);
      }
    }
    .animate-tx-fade-out {
      animation: txFadeOut 0.32s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      pointer-events: none;
      overflow: hidden;
      will-change: opacity, transform, max-height;
    }

    @keyframes txHighlightGlow {
      0% {
        background-color: rgba(2, 132, 199, 0.18);
      }
      50% {
        background-color: rgba(2, 132, 199, 0.08);
      }
      100% {
        background-color: transparent;
      }
    }
    .animate-tx-highlight {
      animation: txHighlightGlow 1.2s ease-out forwards;
    }

    html.dark .animate-tx-highlight,
    body.dark .animate-tx-highlight,
    .dark .animate-tx-highlight {
      animation: txHighlightGlowDark 1.2s ease-out forwards;
    }
    @keyframes txHighlightGlowDark {
      0% {
        background-color: rgba(56, 189, 248, 0.22);
      }
      50% {
        background-color: rgba(56, 189, 248, 0.08);
      }
      100% {
        background-color: transparent;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .animate-dashboard-card,
      .animate-value-pulse,
      .animate-tx-card-entry,
      .animate-tx-slide-in,
      .animate-tx-fade-out,
      .animate-ios-tab-slide-forward,
      .animate-ios-tab-slide-backward,
      .animate-ios-tab-view {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transform: none !important;
      }
    }

    /* iOS Spring Banner Toast (Dynamic Island Physics) */
    @keyframes iosToastSpringDown {
      0% { transform: translate3d(-50%, -120%, 0) scale3d(0.82, 0.82, 1); opacity: 0; }
      60% { transform: translate3d(-50%, 8px, 0) scale3d(1.035, 1.035, 1); opacity: 1; }
      82% { transform: translate3d(-50%, -3px, 0) scale3d(0.99, 0.99, 1); }
      100% { transform: translate3d(-50%, 0, 0) scale3d(1, 1, 1); opacity: 1; }
    }
    @keyframes iosToastSpringUp {
      0% { transform: translate3d(-50%, 0, 0) scale3d(1, 1, 1); opacity: 1; }
      100% { transform: translate3d(-50%, -120%, 0) scale3d(0.88, 0.88, 1); opacity: 0; }
    }
    .animate-ios-toast {
      animation: iosToastSpringDown 0.48s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }
    .animate-ios-toast-exit {
      animation: iosToastSpringUp 0.28s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    /* Modal Backdrop & Card (iOS 26 Liquid Glass Sheet) */
    .ios-modal-backdrop {
      position: fixed;
      inset: 0;
      z-index: 50;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      background-color: rgba(15, 23, 42, 0.55);
      backdrop-filter: blur(16px) saturate(180%);
      -webkit-backdrop-filter: blur(16px) saturate(180%);
      overscroll-behavior: contain;
      padding: 0;
      will-change: opacity;
      transform: translateZ(0);
      -webkit-backface-visibility: hidden;
      backface-visibility: hidden;
      contain: strict;
    }
    @media (min-width: 640px) {
      .ios-modal-backdrop {
        align-items: center;
        padding: 1.25rem;
      }
    }
    .ios-modal-card {
      width: 100%;
      max-width: 28rem;
      max-height: 90dvh;
      display: flex;
      flex-direction: column;
      border-top-left-radius: 1.75rem;
      border-top-right-radius: 1.75rem;
      overflow: hidden;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-bottom: none;
      box-shadow: 0 -10px 32px -6px rgba(15, 23, 42, 0.14);
      color: #0F172A;
      will-change: transform;
      transform: translateZ(0);
      -webkit-backface-visibility: hidden;
      backface-visibility: hidden;
      contain: layout style;
    }
    .dark .ios-modal-card, html.dark .ios-modal-card {
      background: #1E293B !important;
      border: 1px solid #334155 !important;
      border-bottom: none !important;
      box-shadow: 0 -12px 38px -6px rgba(0, 0, 0, 0.65) !important;
      color: #F8FAFC !important;
    }
    @media (min-width: 640px) {
      .ios-modal-card {
        border-radius: 1.5rem;
        max-height: 85vh;
      }
    }
    .ios-modal-header {
      flex-shrink: 0;
      z-index: 10;
    }
    .ios-modal-body {
      flex: 1 1 auto;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior: contain;
      padding-bottom: 9rem !important;
    }

    /* Popover spring */
    @keyframes popoverSpring {
      0% { transform: scale3d(0.85, 0.85, 1) translate3d(0, 0, 0); opacity: 0; }
      65% { transform: scale3d(1.025, 1.025, 1) translate3d(0, 0, 0); opacity: 1; }
      85% { transform: scale3d(0.99, 0.99, 1) translate3d(0, 0, 0); }
      100% { transform: scale3d(1, 1, 1) translate3d(0, 0, 0); opacity: 1; }
    }
    .animate-popover {
      animation: popoverSpring 0.32s cubic-bezier(0.175, 0.885, 0.32, 1.25) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
      backface-visibility: hidden;
      -webkit-backface-visibility: hidden;
    }

    /* Apple SF Symbols Tap Bounce (iOS 17/18) */
    @keyframes iosIconBounce {
      0% { transform: scale3d(1, 1, 1); }
      30% { transform: scale3d(0.8, 0.8, 1); }
      60% { transform: scale3d(1.18, 1.18, 1); }
      85% { transform: scale3d(0.95, 0.95, 1); }
      100% { transform: scale3d(1, 1, 1); }
    }
    .animate-ios-icon-bounce {
      animation: iosIconBounce 0.42s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
      will-change: transform;
      transform: translateZ(0);
    }

    /* Shake animation */
    @keyframes shake {
      0%, 100% { transform: translate3d(0, 0, 0); }
      20%, 60% { transform: translate3d(-8px, 0, 0); }
      40%, 80% { transform: translate3d(8px, 0, 0); }
    }
    .animate-shake {
      animation: shake 0.35s cubic-bezier(0.36, 0.07, 0.19, 0.97);
      will-change: transform;
    }

    /* iOS PIN Pop and Spring Animations */
    @keyframes iosPinPop {
      0% {
        transform: scale3d(0.45, 0.45, 1);
        opacity: 0.4;
      }
      50% {
        transform: scale3d(1.3, 1.3, 1);
        opacity: 1;
      }
      75% {
        transform: scale3d(0.94, 0.94, 1);
      }
      100% {
        transform: scale3d(1, 1, 1);
        opacity: 1;
      }
    }
    .animate-ios-pin-pop {
      animation: iosPinPop 0.28s cubic-bezier(0.175, 0.885, 0.32, 1.25) forwards;
      will-change: transform, opacity;
      transform: translateZ(0);
    }

    @keyframes iosPinShake {
      0%, 100% { transform: translate3d(0, 0, 0); }
      15%, 45%, 75% { transform: translate3d(-10px, 0, 0); }
      30%, 60%, 90% { transform: translate3d(10px, 0, 0); }
    }
    .animate-ios-pin-shake {
      animation: iosPinShake 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
      will-change: transform;
    }

    .pin-keypad-screen {
      height: 100dvh;
      max-height: 100dvh;
      overflow: hidden;
      user-select: none;
      -webkit-user-select: none;
      touch-action: manipulation;
    }

    /* Print & PDF Media Rules */
    @media print {
      @page {
        size: A4 portrait;
        margin: 10mm 10mm 12mm 10mm;
      }
      body {
        background: #ffffff !important;
        color: #0f172a !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }
      body * {
        visibility: hidden;
      }
      #voralet-printable-report, #voralet-printable-report * {
        visibility: visible;
      }
      #voralet-printable-report {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        margin: 0;
        padding: 0;
        background: #ffffff !important;
        color: #0f172a !important;
      }
      .no-print {
        display: none !important;
      }
    }
  </style>
</head>
<body>
  <script>
    window.onerror = function(msg, url, line) {
      var r = document.getElementById('root');
      if (r) r.innerHTML = '<div style="padding:20px;color:#e11d48;background:#fff1f2;font-family:sans-serif;border-radius:12px;margin:16px;"><b>Runtime Error:</b><br>'+msg+'<br>Line: '+line+'</div>';
    };
  </script>
  <div id="root"></div>

  <script type="text/babel" data-presets="env,react" data-compact="false">
    const { useState, useEffect, useMemo, useCallback, useRef } = React;
"""
