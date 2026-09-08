PART3_SERVICES = """
    // =========================================================================
    // 1. DATA LAYER (LOCAL STORAGE SERVICE & LEDGER SYSTEM)
    // =========================================================================
    const STORAGE_KEYS = {
      PIN: 'voralet_pin',
      NAME: 'voralet_name',
      USERNAME: 'voralet_username',
      ACCOUNTS: 'voralet_accounts',
      TRANSACTIONS: 'voralet_transactions',
      SAVINGS_GOALS: 'voralet_savings_goals',
      DEBTS: 'voralet_debts',
      SAFE_BUDGET: 'voralet_safe_budget',
      HIDE_BALANCE: 'voralet_hide_balance',
      THEME: 'voralet_theme',
      AVATAR: 'voralet_avatar'
    };

    const StorageService = {
      getPin: () => {
        try { return localStorage.getItem(STORAGE_KEYS.PIN); } catch (e) { return null; }
      },
      setPin: (pin) => {
        try { localStorage.setItem(STORAGE_KEYS.PIN, pin); } catch (e) {}
      },
      getName: () => {
        try { return localStorage.getItem(STORAGE_KEYS.NAME) || ''; } catch (e) { return ''; }
      },
      setName: (name) => {
        try { localStorage.setItem(STORAGE_KEYS.NAME, name); } catch (e) {}
      },
      getUsername: () => {
        try { return localStorage.getItem(STORAGE_KEYS.USERNAME) || ''; } catch (e) { return ''; }
      },
      setUsername: (username) => {
        try {
          const clean = (username || '').toLowerCase().replace(/[^a-z0-9_]/g, '');
          localStorage.setItem(STORAGE_KEYS.USERNAME, clean);
        } catch (e) {}
      },
      getAccounts: () => {
        try {
          const d = localStorage.getItem(STORAGE_KEYS.ACCOUNTS);
          return d ? JSON.parse(d) : [];
        } catch (e) { return []; }
      },
      setAccounts: (accs) => {
        try { localStorage.setItem(STORAGE_KEYS.ACCOUNTS, JSON.stringify(accs)); } catch (e) {}
      },
      getTransactions: () => {
        try {
          const d = localStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
          return d ? JSON.parse(d) : [];
        } catch (e) { return []; }
      },
      setTransactions: (txs) => {
        try { localStorage.setItem(STORAGE_KEYS.TRANSACTIONS, JSON.stringify(txs)); } catch (e) {}
      },
      getSavingsGoals: () => {
        try {
          const d = localStorage.getItem(STORAGE_KEYS.SAVINGS_GOALS);
          return d ? JSON.parse(d) : [];
        } catch (e) { return []; }
      },
      setSavingsGoals: (goals) => {
        try { localStorage.setItem(STORAGE_KEYS.SAVINGS_GOALS, JSON.stringify(goals)); } catch (e) {}
      },
      getDebts: () => {
        try {
          const d = localStorage.getItem(STORAGE_KEYS.DEBTS);
          return d ? JSON.parse(d) : [];
        } catch (e) { return []; }
      },
      setDebts: (debts) => {
        try { localStorage.setItem(STORAGE_KEYS.DEBTS, JSON.stringify(debts)); } catch (e) {}
      },
      getSafeBudget: () => {
        try {
          const v = localStorage.getItem(STORAGE_KEYS.SAFE_BUDGET);
          return v ? Number(v) : 0;
        } catch (e) { return 0; }
      },
      setSafeBudget: (val) => {
        try { localStorage.setItem(STORAGE_KEYS.SAFE_BUDGET, String(val || 0)); } catch (e) {}
      },
      getHideBalance: () => {
        try { return localStorage.getItem(STORAGE_KEYS.HIDE_BALANCE) === 'true'; } catch (e) { return false; }
      },
      setHideBalance: (val) => {
        try { localStorage.setItem(STORAGE_KEYS.HIDE_BALANCE, val ? 'true' : 'false'); } catch (e) {}
      },
      getTheme: () => {
        try {
          const val = localStorage.getItem(STORAGE_KEYS.THEME);
          return val === 'dark' ? 'dark' : 'light';
        } catch (e) { return 'light'; }
      },
      setTheme: (theme) => {
        try { localStorage.setItem(STORAGE_KEYS.THEME, theme); } catch (e) {}
      },
      getAvatar: () => {
        try { return localStorage.getItem(STORAGE_KEYS.AVATAR) || ''; } catch (e) { return ''; }
      },
      setAvatar: (avatar) => {
        try {
          if (avatar) localStorage.setItem(STORAGE_KEYS.AVATAR, avatar);
          else localStorage.removeItem(STORAGE_KEYS.AVATAR);
        } catch (e) {}
      },
      clearAll: () => {
        try {
          Object.values(STORAGE_KEYS).forEach(k => localStorage.removeItem(k));
        } catch (e) {}
      }
    };

    // LEDGER ENGINE: Single Source of Truth
    const Ledger = {
      getAccountBalance: (accountId, accounts, transactions) => {
        if (!accountId) return 0;
        const safeAccs = Array.isArray(accounts) ? accounts : [];
        const safeTxs = Array.isArray(transactions) ? transactions : [];
        const acc = safeAccs.find(a => a && a.id === accountId);
        if (!acc) return 0;
        const initial = Number(acc.initialBalance) || 0;
        const sumTx = safeTxs
          .filter(t => t && t.accountId === accountId)
          .reduce((sum, t) => {
            const amt = Number(t.amount) || 0;
            return t.type === 'INCOME' ? sum + amt : sum - amt;
          }, 0);
        return initial + sumTx;
      },
      getTotalBalance: (accounts, transactions) => {
        const safeAccs = Array.isArray(accounts) ? accounts : [];
        const safeTxs = Array.isArray(transactions) ? transactions : [];
        return safeAccs.reduce((tot, a) => {
          if (!a) return tot;
          return tot + Ledger.getAccountBalance(a.id, safeAccs, safeTxs);
        }, 0);
      },
      getSummaryTotals: (transactions, filterAccountId = null) => {
        const safeTxs = Array.isArray(transactions) ? transactions : [];
        const filtered = filterAccountId
          ? safeTxs.filter(t => t && t.accountId === filterAccountId)
          : safeTxs;
        let income = 0;
        let expense = 0;
        for (const t of filtered) {
          if (!t) continue;
          const amt = Number(t.amount) || 0;
          if (t.type === 'INCOME') income += amt;
          else if (t.type === 'EXPENSE') expense += amt;
        }
        return { income, expense, net: income - expense };
      }
    };

    // Formatters
    const formatIDR = (amount) => {
      const num = Number(amount) || 0;
      return 'Rp ' + new Intl.NumberFormat('id-ID').format(num);
    };

    const parseRawNumber = (str) => {
      if (typeof str === 'number') return str;
      if (!str) return 0;
      const clean = str.toString().replace(/\\D/g, '');
      return clean ? parseInt(clean, 10) : 0;
    };

    const formatDateID = (dateStr) => {
      try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('id-ID', {
          day: 'numeric',
          month: 'short',
          year: 'numeric'
        });
      } catch (e) {
        return dateStr;
      }
    };

    const CATEGORIES = [
      { id: 'makan', label: 'Makan & Minum', icon: 'food', type: 'EXPENSE' },
      { id: 'transport', label: 'Transportasi', icon: 'transport', type: 'EXPENSE' },
      { id: 'belanja', label: 'Belanja', icon: 'shopping', type: 'EXPENSE' },
      { id: 'tagihan', label: 'Tagihan & Utilitas', icon: 'bill', type: 'EXPENSE' },
      { id: 'hiburan', label: 'Hiburan', icon: 'entertainment', type: 'EXPENSE' },
      { id: 'kesehatan', label: 'Kesehatan', icon: 'health', type: 'EXPENSE' },
      { id: 'gaji', label: 'Gaji & Honor', icon: 'salary', type: 'INCOME' },
      { id: 'bonus', label: 'Bonus & Hadiah', icon: 'gift', type: 'INCOME' },
      { id: 'investasi', label: 'Investasi', icon: 'investment', type: 'INCOME' },
      { id: 'lainnya', label: 'Lainnya', icon: 'tag', type: 'ALL' }
    ];

    // Mobile Virtual Keyboard Management
    const handleGlobalInputFocus = (e) => {
      const target = e.target;
      if (!target) return;
      const tag = target.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') {
        if (target.closest('.pin-keypad-screen')) return;
        setTimeout(() => {
          if (target && typeof target.scrollIntoView === 'function') {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }, 220);
      }
    };

    const handleGlobalInputBlur = () => {
      setTimeout(() => {
        const active = document.activeElement;
        const isInput = active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT');
        if (!isInput) {
          window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
        }
      }, 120);
    };

    // Client-side image compression
    const compressImage = (file, callback, onError) => {
      if (!file || !file.type.startsWith('image/')) {
        if (onError) onError('File harus berupa gambar');
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          try {
            const canvas = document.createElement('canvas');
            const maxDim = 200;
            let width = img.width;
            let height = img.height;
            if (width > height) {
              if (width > maxDim) {
                height = Math.round((height * maxDim) / width);
                width = maxDim;
              }
            } else {
              if (height > maxDim) {
                width = Math.round((width * maxDim) / height);
                height = maxDim;
              }
            }
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
            callback(dataUrl);
          } catch (err) {
            if (onError) onError('Gagal memproses gambar');
          }
        };
        img.onerror = () => { if (onError) onError('Gagal memuat gambar'); };
        img.src = e.target.result;
      };
      reader.onerror = () => { if (onError) onError('Gagal membaca file gambar'); };
      reader.readAsDataURL(file);
    };

    // Reusable Avatar
    const Avatar = ({ avatar, name, size = "w-9 h-9", textSize = "text-xs", className = "" }) => {
      if (avatar) {
        return (
          <img
            src={avatar}
            alt={name || "Profil"}
            className={`${size} rounded-full object-cover border border-slate-200 dark:border-slate-700 shrink-0 ${className}`}
          />
        );
      }
      const initial = (name ? name.trim().charAt(0) : 'V').toUpperCase();
      return (
        <div className={`${size} rounded-full bg-brand text-white flex items-center justify-center font-bold ${textSize} shrink-0 ${className}`}>
          {initial}
        </div>
      );
    };

    // iOS Sliding Segmented Control with animated sliding pill background
    const SegmentedControl = ({ options, value, onChange, className = "" }) => {
      const activeIndex = Math.max(0, options.findIndex(o => o.value === value));
      const widthPct = options.length > 0 ? 100 / options.length : 100;
      return (
        <div className={`relative p-1 bg-slate-100 dark:bg-slate-900 rounded-2xl flex items-center select-none ${className}`}>
          {/* Sliding pill background */}
          <div
            className="absolute top-1 bottom-1 rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-200/50 dark:border-slate-700/60 transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
            style={{
              width: `calc(${widthPct}% - 4px)`,
              left: `calc(${activeIndex * widthPct}% + 2px)`
            }}
          />
          {options.map((opt) => {
            const isSelected = opt.value === value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange(opt.value)}
                className={`relative z-10 flex-1 py-2 text-center text-xs font-semibold transition-colors duration-200 ios-btn-tap ${
                  isSelected ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      );
    };

    // Contextual Long-Press Popover Sheet
    const ContextualMenuModal = ({ isOpen, title, onClose, onEdit, onDelete, onDuplicate }) => {
      if (!isOpen) return null;
      return (
        <div className="ios-modal-backdrop animate-ios-backdrop" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
          <div className="ios-modal-card bg-white dark:bg-slate-800 p-4 animate-popover max-w-xs mx-auto rounded-[24px] shadow-2xl border border-slate-100 dark:border-slate-700">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate">{title || 'Tindakan'}</span>
              <button
                type="button"
                onClick={onClose}
                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                aria-label="Tutup"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <div className="pt-2 space-y-1">
              {onEdit && (
                <button
                  type="button"
                  onClick={() => { onClose(); onEdit(); }}
                  className="w-full px-3 py-2.5 rounded-xl text-left text-xs font-semibold text-slate-800 dark:text-slate-200 hover:bg-sky-50 dark:hover:bg-slate-700 flex items-center gap-2.5 ios-btn-tap"
                >
                  <Icon name="edit" className="w-4 h-4 text-brand" />
                  <span>Edit</span>
                </button>
              )}
              {onDuplicate && (
                <button
                  type="button"
                  onClick={() => { onClose(); onDuplicate(); }}
                  className="w-full px-3 py-2.5 rounded-xl text-left text-xs font-semibold text-slate-800 dark:text-slate-200 hover:bg-sky-50 dark:hover:bg-slate-700 flex items-center gap-2.5 ios-btn-tap"
                >
                  <Icon name="duplicate" className="w-4 h-4 text-sky-500" />
                  <span>Duplikat</span>
                </button>
              )}
              {onDelete && (
                <button
                  type="button"
                  onClick={() => { onClose(); onDelete(); }}
                  className="w-full px-3 py-2.5 rounded-xl text-left text-xs font-semibold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 flex items-center gap-2.5 ios-btn-tap"
                >
                  <Icon name="trash" className="w-4 h-4" />
                  <span>Hapus</span>
                </button>
              )}
            </div>
          </div>
        </div>
      );
    };

    // iOS Banner Toast Notification with Spring Rebound
    const Toast = ({ message, onClose }) => {
      const [isLeaving, setIsLeaving] = useState(false);

      useEffect(() => {
        const timer1 = setTimeout(() => setIsLeaving(true), 2400);
        const timer2 = setTimeout(() => onClose(), 2700);
        return () => {
          clearTimeout(timer1);
          clearTimeout(timer2);
        };
      }, [onClose]);

      return (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-[100] px-4 py-2.5 rounded-full bg-slate-900/95 dark:bg-slate-800/95 text-white text-xs font-semibold shadow-xl flex items-center gap-2.5 border border-slate-700/60 select-none ${isLeaving ? 'animate-ios-toast-exit' : 'animate-ios-toast'}`}>
          <span className="w-2 h-2 rounded-full bg-brand shrink-0"></span>
          <span>{message}</span>
        </div>
      );
    };
"""
