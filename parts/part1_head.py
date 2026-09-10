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
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    if (window.tailwind) {
      window.tailwind.config = window.tailwind.config || {};
      window.tailwind.config.darkMode = 'class';
    }
  </script>

  <!-- React 18 & ReactDOM & Babel Standalone -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script>window.React || document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"><\\/script>')</script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script>window.ReactDOM || document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"><\\/script>')</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.4/babel.min.js"></script>
  <script>window.Babel || document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.4/babel.min.js"><\\/script>')</script>

  <!-- Theme Synchronization Initialization -->
  <script>
    try {
      const savedTheme = localStorage.getItem('voralet_theme');
      if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
        if (document.body) document.body.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
        if (document.body) document.body.classList.remove('dark');
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
      background-color: #F8FAFC;
      color: #0F172A;
      transition: background-color 300ms ease-in-out, color 300ms ease-in-out;
    }
    html.dark #root {
      background-color: #0F172A !important;
      color: #F8FAFC !important;
    }

    /* iOS Inset Grouped Block */
    .ios-inset-group {
      border-radius: 22px;
      background-color: #FFFFFF;
      padding: 1rem;
      border: 1px solid #E2E8F0;
      box-shadow: 0 2px 10px -1px rgba(15, 23, 42, 0.07), 0 1px 3px -1px rgba(15, 23, 42, 0.04);
      transition: background-color 300ms ease-in-out, border-color 300ms ease-in-out, color 300ms ease-in-out, box-shadow 300ms ease-in-out;
    }
    .dark .ios-inset-group {
      background-color: #1E293B !important;
      border-color: #334155 !important;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45), 0 2px 8px -1px rgba(0, 0, 0, 0.3) !important;
      color: #F8FAFC !important;
    }

    /* iOS Floating & Capsule Shadows */
    .ios-drop-shadow {
      box-shadow: 0 6px 20px -3px rgba(15, 23, 42, 0.1), 0 2px 6px -2px rgba(15, 23, 42, 0.05);
    }
    .dark .ios-drop-shadow {
      box-shadow: 0 8px 24px -3px rgba(0, 0, 0, 0.55), 0 2px 8px -2px rgba(0, 0, 0, 0.4);
    }
    .ios-nav-shadow {
      box-shadow: 0 14px 36px -6px rgba(15, 23, 42, 0.22), 0 4px 14px -2px rgba(15, 23, 42, 0.1);
    }
    .dark .ios-nav-shadow {
      box-shadow: 0 18px 40px -6px rgba(0, 0, 0, 0.75), 0 4px 16px -2px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08);
    }

    /* Hairline Divider */
    .ios-hairline {
      border-bottom: 1px solid #E2E8F0;
      transition: border-color 300ms ease-in-out;
    }
    .dark .ios-hairline, html.dark .ios-hairline {
      border-bottom: 1px solid #334155 !important;
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

    /* Tactile Touch Animation (SwiftUI Bouncy Spring Compression) */
    .ios-btn-tap, .ios-touch-item {
      transition: transform 150ms ease-out, opacity 150ms ease-out;
      will-change: transform;
      user-select: none;
      -webkit-user-select: none;
    }
    .ios-btn-tap:active, .ios-touch-item:active {
      transform: scale3d(0.94, 0.94, 1) !important;
      opacity: 0.86;
    }
    .ios-card-tap {
      transition: transform 150ms ease-out, opacity 150ms ease-out;
      will-change: transform;
      user-select: none;
      -webkit-user-select: none;
    }
    .ios-card-tap:active {
      transform: scale3d(0.96, 0.96, 1) !important;
      opacity: 0.92;
    }

    /* Apple Wallet Dynamic Card Stack & Motion */
    .apple-wallet-card-collapsed {
      height: 74px;
      border-radius: 1.25rem;
      position: relative;
      overflow: hidden;
      background-color: #38bdf8;
      box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.28), 0 2px 8px -2px rgba(0, 0, 0, 0.16), inset 0 1px 1px rgba(255, 255, 255, 0.35);
      transition: all 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .apple-wallet-card-expanded {
      height: 195px;
      border-radius: 1.35rem;
      position: relative;
      overflow: hidden;
      background-color: #38bdf8;
      box-shadow: 0 24px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 2px rgba(255, 255, 255, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.4);
      transition: all 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @media (min-width: 640px) {
      .apple-wallet-card-expanded {
        height: 210px;
        border-radius: 1.5rem;
      }
    }
    .apple-atm-shimmer {
      position: absolute;
      inset: -50%;
      background: linear-gradient(
        115deg,
        transparent 35%,
        rgba(255, 255, 255, 0.06) 45%,
        rgba(255, 255, 255, 0.18) 50%,
        rgba(255, 255, 255, 0.06) 55%,
        transparent 65%
      );
      transform: rotate(20deg) translate3d(-100%, -100%, 0);
      pointer-events: none;
      animation: appleCardShine 7s infinite ease-in-out;
    }
    @keyframes appleCardShine {
      0%, 70% { transform: rotate(20deg) translate3d(-100%, -100%, 0); }
      85%, 100% { transform: rotate(20deg) translate3d(100%, 100%, 0); }
    }
    .apple-card-emboss {
      text-shadow: 0 1px 1px rgba(0, 0, 0, 0.4), 0 -1px 0 rgba(255, 255, 255, 0.2);
    }

    /* Keypad Button */
    .ios-keypad-btn {
      transition: transform 150ms ease-out, opacity 150ms ease-out, background-color 150ms ease;
      will-change: transform;
    }
    .ios-keypad-btn:active {
      transform: scale3d(0.92, 0.92, 1) !important;
      opacity: 0.76;
    }

    /* iOS Native Modal Sheet Depth Stacking Effect */
    .ios-modal-depth-layer {
      transition: transform 350ms cubic-bezier(0.32, 0.72, 0, 1), border-radius 350ms cubic-bezier(0.32, 0.72, 0, 1), filter 350ms ease-out;
      will-change: transform, border-radius;
      transform-origin: center top;
    }
    .ios-modal-depth-stacked {
      transform: scale(0.96) !important;
      border-radius: 28px !important;
      overflow: hidden !important;
      filter: brightness(0.95);
    }
    html.dark .ios-modal-depth-stacked, .dark .ios-modal-depth-stacked {
      filter: brightness(0.88);
    }

    /* SwiftUI Bouncy Elastic Curve for Dialogs, Popovers & Toasts */
    @keyframes iosSpringPop {
      0% {
        transform: scale(0.85);
        opacity: 0;
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
    }
    .animate-ios-spring-pop {
      animation: iosSpringPop 0.38s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
      will-change: transform, opacity;
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

    /* iOS Page View Transition Animation */
    @keyframes iosTabFadeIn {
      0% {
        opacity: 0;
        transform: translate3d(0, 10px, 0) scale(0.985);
      }
      100% {
        opacity: 1;
        transform: translate3d(0, 0, 0) scale(1);
      }
    }
    .animate-ios-tab-view {
      animation: iosTabFadeIn 0.28s cubic-bezier(0.25, 1, 0.5, 1) forwards;
      will-change: opacity, transform;
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
      transition: background-color 300ms ease-in-out, color 300ms ease-in-out;
    }
    .dark .ios-modal-card {
      background-color: #1E293B !important;
      color: #F8FAFC !important;
      border: 1px solid #334155 !important;
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

  <script type="text/babel" data-presets="env,react">
    const { useState, useEffect, useMemo, useCallback, useRef } = React;
"""
