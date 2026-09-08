HTML_HEAD = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>Voralet - Authentic iOS Personal Finance</title>
  <meta name="description" content="Aplikasi pencatat keuangan pribadi modern ala iOS dengan brankas PIN lokal dan pelacak hutang piutang." />
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
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
            // Map dark slate to true OLED black and sleek dark surfaces
            slate: {
              950: '#000000',
              900: '#000000', // Pure black for dark mode canvas
              850: '#0A0A0C',
              800: '#121212', // Pure deep dark surface for cards
              750: '#18181B',
              700: '#27272A', // Crisp border in dark mode
              600: '#52525B',
              500: '#71717A',
              400: '#A1A1AA',
              300: '#CBD5E1',
              200: '#E2E8F0',
              100: '#F1F5F9',
              50: '#F8FAFC'
            }
          },
          fontFamily: {
            sans: ['Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', 'Roboto', 'sans-serif']
          }
        }
      }
    }
  </script>

  <!-- React 18 & ReactDOM & Babel Standalone -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script>window.React || document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"><\\/script>')</script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script>window.ReactDOM || document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"><\\/script>')</script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script>window.Babel || document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.4/babel.min.js"><\\/script>')</script>

  <!-- Enforce Light Mode as strict default on first launch with Blue & White theme -->
  <script>
    try {
      const savedTheme = localStorage.getItem('voralet_theme');
      if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
        if (!savedTheme) {
          localStorage.setItem('voralet_theme', 'light');
        }
      }
    } catch (e) {
      document.documentElement.classList.remove('dark');
    }
  </script>

  <style>
    :root {
      --ios-ease: cubic-bezier(0.32, 0.72, 0, 1);
      --ios-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
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
      overscroll-behavior: none;
      -webkit-overflow-scrolling: touch;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
      background-color: #FFFFFF;
      color: #0F172A;
      transition: background-color 350ms cubic-bezier(0.32, 0.72, 0, 1), color 350ms cubic-bezier(0.32, 0.72, 0, 1);
    }
    html.dark body, body.dark {
      background-color: #000000 !important;
      color: #FFFFFF !important;
    }
    #root {
      height: 100%;
      width: 100%;
      overflow: hidden;
      background-color: #FFFFFF;
      color: #0F172A;
      transition: background-color 350ms cubic-bezier(0.32, 0.72, 0, 1), color 350ms cubic-bezier(0.32, 0.72, 0, 1);
    }
    html.dark #root {
      background-color: #000000 !important;
      color: #FFFFFF !important;
    }

    /* iOS Inset Grouped Block */
    .ios-inset-group {
      border-radius: 22px;
      background-color: #F8FAFC;
      padding: 1rem;
      border: 1px solid #E2E8F0;
      transition: background-color 350ms cubic-bezier(0.32, 0.72, 0, 1), border-color 350ms cubic-bezier(0.32, 0.72, 0, 1), color 350ms cubic-bezier(0.32, 0.72, 0, 1);
    }
    .dark .ios-inset-group {
      background-color: #121212 !important;
      border-color: #27272A !important;
      color: #FFFFFF !important;
    }

    /* Hairline Divider */
    .ios-hairline {
      border-bottom: 1px solid #E2E8F0;
      transition: border-color 350ms cubic-bezier(0.32, 0.72, 0, 1);
    }
    .dark .ios-hairline {
      border-bottom: 1px solid #27272A !important;
    }

    /* Scrollbar hide */
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }

    /* Tactile Touch Animation */
    .ios-btn-tap, .ios-touch-item, .ios-card-tap {
      transition: transform 0.15s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.15s ease-out;
      will-change: transform;
      user-select: none;
      -webkit-user-select: none;
    }
    .ios-btn-tap:active, .ios-touch-item:active {
      transform: scale3d(0.96, 0.96, 1);
      opacity: 0.86;
    }
    .ios-card-tap:active {
      transform: scale3d(0.98, 0.98, 1);
      opacity: 0.92;
    }

    /* Keypad Button */
    .ios-keypad-btn {
      transition: transform 0.12s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.12s ease-out, background-color 0.15s ease;
      will-change: transform;
    }
    .ios-keypad-btn:active {
      transform: scale3d(0.92, 0.92, 1);
      opacity: 0.78;
    }

    /* iOS Bottom Sheet Animations */
    @keyframes iosSheetEnter {
      0% { transform: translate3d(0, 100%, 0); }
      100% { transform: translate3d(0, 0, 0); }
    }
    @keyframes iosSheetExit {
      0% { transform: translate3d(0, 0, 0); }
      100% { transform: translate3d(0, 100%, 0); }
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
      animation: iosSheetEnter 0.35s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: transform;
    }
    .animate-ios-sheet-exit {
      animation: iosSheetExit 0.25s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: transform;
    }
    .animate-ios-backdrop {
      animation: iosBackdropFadeIn 0.3s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: opacity;
    }
    .animate-ios-backdrop-exit {
      animation: iosBackdropFadeOut 0.22s cubic-bezier(0.32, 0.72, 0, 1) forwards;
      will-change: opacity;
    }

    /* iOS Spring Banner Toast */
    @keyframes iosToastSpringDown {
      0% { transform: translate3d(-50%, -100%, 0) scale(0.9); opacity: 0; }
      70% { transform: translate3d(-50%, 8px, 0) scale(1.02); opacity: 1; }
      100% { transform: translate3d(-50%, 0, 0) scale(1); opacity: 1; }
    }
    @keyframes iosToastSpringUp {
      0% { transform: translate3d(-50%, 0, 0) scale(1); opacity: 1; }
      100% { transform: translate3d(-50%, -100%, 0) scale(0.9); opacity: 0; }
    }
    .animate-ios-toast {
      animation: iosToastSpringDown 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .animate-ios-toast-exit {
      animation: iosToastSpringUp 0.25s cubic-bezier(0.32, 0.72, 0, 1) forwards;
    }

    /* Modal Backdrop & Card */
    .ios-modal-backdrop {
      position: fixed;
      inset: 0;
      z-index: 50;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      background-color: rgba(15, 23, 42, 0.65);
      overscroll-behavior: contain;
      padding: 0;
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
      border-top-left-radius: 1.5rem;
      border-top-right-radius: 1.5rem;
      overflow: hidden;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
      background-color: #FFFFFF;
      color: #0F172A;
      transition: background-color 350ms cubic-bezier(0.32, 0.72, 0, 1), color 350ms cubic-bezier(0.32, 0.72, 0, 1);
    }
    .dark .ios-modal-card {
      background-color: #121212 !important;
      color: #FFFFFF !important;
      border-color: #27272A !important;
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
      0% { transform: scale(0.8); opacity: 0; }
      60% { transform: scale(1.03); opacity: 1; }
      100% { transform: scale(1); opacity: 1; }
    }
    .animate-popover {
      animation: popoverSpring 0.28s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
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
        transform: scale(0.45);
        opacity: 0.4;
      }
      50% {
        transform: scale(1.35);
        opacity: 1;
      }
      75% {
        transform: scale(0.92);
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
    }
    .animate-ios-pin-pop {
      animation: iosPinPop 0.28s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
      will-change: transform, opacity;
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
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useEffect, useMemo, useCallback, useRef } = React;
"""
