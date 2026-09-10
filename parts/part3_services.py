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

    // =========================================================================
    // CRYPTOGRAPHY SERVICE (PBKDF2 PIN hashing with legacy migration)
    // =========================================================================
    const CryptoService = {
      SALT: 'voralet_secure_salt_v1_',
      ITERATIONS: 120000,
      bytesToBase64: (bytes) => {
        let binary = '';
        bytes.forEach(byte => { binary += String.fromCharCode(byte); });
        return btoa(binary);
      },
      base64ToBytes: (value) => Uint8Array.from(atob(value), char => char.charCodeAt(0)),
      legacyHashPin: async (pin) => {
        try {
          if (window.crypto && window.crypto.subtle && window.crypto.subtle.digest) {
            const encoder = new TextEncoder();
            const data = encoder.encode(CryptoService.SALT + String(pin));
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
          }
        } catch (e) {}
        // Deterministic fallback if subtle is unavailable
        let hash = 0x811c9dc5;
        const str = CryptoService.SALT + String(pin);
        for (let i = 0; i < str.length; i++) {
          hash ^= str.charCodeAt(i);
          hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
        }
        return 'voralet_hash_' + (hash >>> 0).toString(16);
      },
      deriveHash: async (pin, salt, iterations) => {
        const encoder = new TextEncoder();
        const key = await window.crypto.subtle.importKey(
          'raw',
          encoder.encode(String(pin)),
          { name: 'PBKDF2' },
          false,
          ['deriveBits']
        );
        const bits = await window.crypto.subtle.deriveBits(
          { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
          key,
          256
        );
        return new Uint8Array(bits);
      },
      equalConstantTime: (left, right) => {
        if (typeof left !== 'string' || typeof right !== 'string' || left.length !== right.length) return false;
        let difference = 0;
        for (let index = 0; index < left.length; index++) {
          difference |= left.charCodeAt(index) ^ right.charCodeAt(index);
        }
        return difference === 0;
      },
      hashPin: async (pin) => {
        if (!pin) return '';
        try {
          if (window.crypto?.subtle && window.crypto?.getRandomValues) {
            const salt = window.crypto.getRandomValues(new Uint8Array(16));
            const hash = await CryptoService.deriveHash(pin, salt, CryptoService.ITERATIONS);
            return `v2$${CryptoService.ITERATIONS}$${CryptoService.bytesToBase64(salt)}$${CryptoService.bytesToBase64(hash)}`;
          }
        } catch (e) {}
        return CryptoService.legacyHashPin(pin);
      },
      verifyPin: async (inputPin, storedPin) => {
        if (!storedPin || !inputPin) return false;
        // Legacy plaintext migration: if storedPin is 6 raw digits, check and upgrade
        if (storedPin.length === 6 && /^\\d{6}$/.test(storedPin)) {
          if (inputPin === storedPin) {
            CryptoService.hashPin(inputPin).then(hashed => {
              if (hashed) StorageService.setPin(hashed);
            });
            return true;
          }
          return false;
        }
        if (storedPin.startsWith('v2$')) {
          try {
            const [, iterations, saltValue, expectedHash] = storedPin.split('$');
            const actualHash = await CryptoService.deriveHash(
              inputPin,
              CryptoService.base64ToBytes(saltValue),
              Number(iterations)
            );
            return CryptoService.equalConstantTime(
              CryptoService.bytesToBase64(actualHash),
              expectedHash
            );
          } catch (e) {
            return false;
          }
        }
        const hashedInput = await CryptoService.legacyHashPin(inputPin);
        if (!CryptoService.equalConstantTime(hashedInput, storedPin)) return false;
        CryptoService.hashPin(inputPin).then(hashed => StorageService.setPin(hashed));
        return true;
      }
    };

    // =========================================================================
    // DEFENSIVE VALIDATORS & SCHEMA INTEGRITY
    // =========================================================================
    const Validators = {
      sanitizeText: (str, maxLen = 60) => {
        if (str === null || str === undefined) return '';
        return String(str)
          .replace(/[<>]/g, '')
          .replace(/javascript:/gi, '')
          .replace(/on[a-z]+=/gi, '')
          .trim()
          .slice(0, maxLen);
      },
      sanitizeNumber: (val, fallback = 0) => {
        const n = Number(val);
        return (isNaN(n) || !isFinite(n) || n < 0) ? fallback : n;
      },
      validateTransaction: (tx) => {
        if (!tx || typeof tx !== 'object') return null;
        const amount = Validators.sanitizeNumber(tx.amount, 0);
        if (amount <= 0) return null;
        return {
          id: String(tx.id || ('tx_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7))),
          type: (tx.type === 'INCOME') ? 'INCOME' : 'EXPENSE',
          amount,
          category: Validators.sanitizeText(tx.category || 'lainnya', 30),
          accountId: String(tx.accountId || ''),
          date: tx.date || new Date().toISOString().split('T')[0],
          note: Validators.sanitizeText(tx.note || '', 100),
          createdAt: tx.createdAt || new Date().toISOString()
        };
      },
      validateAccount: (acc) => {
        if (!acc || typeof acc !== 'object') return null;
        const name = Validators.sanitizeText(acc.name, 30);
        if (!name) return null;
        return {
          id: String(acc.id || ('acc_' + Date.now())),
          name,
          type: ['Bank', 'Cash', 'E-Wallet'].includes(acc.type) ? acc.type : 'Cash',
          initialBalance: Validators.sanitizeNumber(acc.initialBalance, 0),
          accountNumber: Validators.sanitizeText(acc.accountNumber || '', 30),
          theme: Validators.sanitizeText(acc.theme || '', 30),
          createdAt: acc.createdAt || new Date().toISOString()
        };
      },
      validateSavingsGoal: (goal) => {
        if (!goal || typeof goal !== 'object') return null;
        const name = Validators.sanitizeText(goal.name, 40);
        const targetAmount = Validators.sanitizeNumber(goal.targetAmount, 0);
        if (!name || targetAmount <= 0) return null;
        return {
          id: String(goal.id || ('goal_' + Date.now())),
          name,
          targetAmount,
          currentAmount: Validators.sanitizeNumber(goal.currentAmount, 0),
          category: Validators.sanitizeText(goal.category || 'Tabungan', 30),
          icon: Validators.sanitizeText(goal.icon || 'target', 20),
          createdAt: goal.createdAt || new Date().toISOString()
        };
      },
      validateDebt: (debt) => {
        if (!debt || typeof debt !== 'object') return null;
        const personName = Validators.sanitizeText(debt.personName, 40);
        const amount = Validators.sanitizeNumber(debt.amount, 0);
        if (!personName || amount <= 0) return null;
        return {
          id: String(debt.id || ('debt_' + Date.now())),
          personName,
          type: debt.type === 'PIUTANG' ? 'PIUTANG' : 'HUTANG',
          amount,
          dueDate: debt.dueDate || '',
          isPaid: Boolean(debt.isPaid),
          note: Validators.sanitizeText(debt.note || '', 100),
          createdAt: debt.createdAt || new Date().toISOString()
        };
      },
      validateBackupSchema: (data) => {
        if (!data || typeof data !== 'object') return null;
        const accounts = Array.isArray(data.accounts)
          ? data.accounts.map(Validators.validateAccount).filter(Boolean)
          : [];
        const transactions = Array.isArray(data.transactions)
          ? data.transactions.map(Validators.validateTransaction).filter(Boolean)
          : [];
        const savingsGoals = Array.isArray(data.savingsGoals)
          ? data.savingsGoals.map(Validators.validateSavingsGoal).filter(Boolean)
          : [];
        const debts = Array.isArray(data.debts)
          ? data.debts.map(Validators.validateDebt).filter(Boolean)
          : [];
        return {
          accounts,
          transactions,
          savingsGoals,
          debts,
          name: Validators.sanitizeText(data.name || '', 30),
          username: (data.username || '').toLowerCase().replace(/[^a-z0-9_]/g, ''),
          avatar: typeof data.avatar === 'string' ? data.avatar : '',
          theme: data.theme === 'dark' ? 'dark' : 'light',
          safeBudget: Validators.sanitizeNumber(data.safeBudget, 0)
        };
      }
    };

    // =========================================================================
    // SAFE STORAGE PROXY (Bulletproof LocalStorage wrapper with memory fallback)
    // =========================================================================
    const SafeStorage = (() => {
      const memoryStore = new Map();
      let isAvailable = false;
      try {
        if (typeof window !== 'undefined' && 'localStorage' in window && window.localStorage) {
          const testKey = '__voralet_test__';
          window.localStorage.setItem(testKey, '1');
          window.localStorage.removeItem(testKey);
          isAvailable = true;
        }
      } catch (e) {
        isAvailable = false;
      }

      return {
        getItem: (key) => {
          try {
            if (isAvailable) {
              const val = window.localStorage.getItem(key);
              if (val !== null) return val;
            }
          } catch (e) {}
          return memoryStore.has(key) ? memoryStore.get(key) : null;
        },
        setItem: (key, value) => {
          const strVal = String(value);
          memoryStore.set(key, strVal);
          try {
            if (isAvailable) {
              window.localStorage.setItem(key, strVal);
            }
          } catch (e) {}
        },
        removeItem: (key) => {
          memoryStore.delete(key);
          try {
            if (isAvailable) {
              window.localStorage.removeItem(key);
            }
          } catch (e) {}
        },
        parseJSON: (raw, fallback = null) => {
          if (!raw || typeof raw !== 'string') return fallback;
          try {
            return JSON.parse(raw);
          } catch (e) {
            return fallback;
          }
        }
      };
    })();

    const StorageService = {
      getPin: () => {
        return SafeStorage.getItem(STORAGE_KEYS.PIN);
      },
      setPin: (pin) => {
        SafeStorage.setItem(STORAGE_KEYS.PIN, pin);
      },
      getName: () => {
        return SafeStorage.getItem(STORAGE_KEYS.NAME) || '';
      },
      setName: (name) => {
        SafeStorage.setItem(STORAGE_KEYS.NAME, name);
      },
      getUsername: () => {
        return SafeStorage.getItem(STORAGE_KEYS.USERNAME) || '';
      },
      setUsername: (username) => {
        const clean = (username || '').toLowerCase().replace(/[^a-z0-9_]/g, '');
        SafeStorage.setItem(STORAGE_KEYS.USERNAME, clean);
      },
      getAccounts: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.ACCOUNTS);
        const parsed = SafeStorage.parseJSON(d, []);
        return Array.isArray(parsed) ? parsed.map(Validators.validateAccount).filter(Boolean) : [];
      },
      setAccounts: (accs) => {
        const clean = Array.isArray(accs) ? accs.map(Validators.validateAccount).filter(Boolean) : [];
        SafeStorage.setItem(STORAGE_KEYS.ACCOUNTS, JSON.stringify(clean));
      },
      getTransactions: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.TRANSACTIONS);
        const parsed = SafeStorage.parseJSON(d, []);
        return Array.isArray(parsed) ? parsed.map(Validators.validateTransaction).filter(Boolean) : [];
      },
      setTransactions: (txs) => {
        const clean = Array.isArray(txs) ? txs.map(Validators.validateTransaction).filter(Boolean) : [];
        SafeStorage.setItem(STORAGE_KEYS.TRANSACTIONS, JSON.stringify(clean));
      },
      getSavingsGoals: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.SAVINGS_GOALS);
        const parsed = SafeStorage.parseJSON(d, []);
        return Array.isArray(parsed) ? parsed.map(Validators.validateSavingsGoal).filter(Boolean) : [];
      },
      setSavingsGoals: (goals) => {
        const clean = Array.isArray(goals) ? goals.map(Validators.validateSavingsGoal).filter(Boolean) : [];
        SafeStorage.setItem(STORAGE_KEYS.SAVINGS_GOALS, JSON.stringify(clean));
      },
      getDebts: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.DEBTS);
        const parsed = SafeStorage.parseJSON(d, []);
        return Array.isArray(parsed) ? parsed.map(Validators.validateDebt).filter(Boolean) : [];
      },
      setDebts: (debts) => {
        const clean = Array.isArray(debts) ? debts.map(Validators.validateDebt).filter(Boolean) : [];
        SafeStorage.setItem(STORAGE_KEYS.DEBTS, JSON.stringify(clean));
      },
      getSafeBudget: () => {
        const v = SafeStorage.getItem(STORAGE_KEYS.SAFE_BUDGET);
        return v ? Number(v) : 0;
      },
      setSafeBudget: (val) => {
        SafeStorage.setItem(STORAGE_KEYS.SAFE_BUDGET, String(val || 0));
      },
      getHideBalance: () => {
        return SafeStorage.getItem(STORAGE_KEYS.HIDE_BALANCE) === 'true';
      },
      setHideBalance: (val) => {
        SafeStorage.setItem(STORAGE_KEYS.HIDE_BALANCE, val ? 'true' : 'false');
      },
      getTheme: () => {
        const val = SafeStorage.getItem(STORAGE_KEYS.THEME);
        return val === 'dark' ? 'dark' : 'light';
      },
      setTheme: (theme) => {
        SafeStorage.setItem(STORAGE_KEYS.THEME, theme);
      },
      getAvatar: () => {
        return SafeStorage.getItem(STORAGE_KEYS.AVATAR) || '';
      },
      setAvatar: (avatar) => {
        if (avatar) SafeStorage.setItem(STORAGE_KEYS.AVATAR, avatar);
        else SafeStorage.removeItem(STORAGE_KEYS.AVATAR);
      },
      clearAll: () => {
        Object.values(STORAGE_KEYS).forEach(k => SafeStorage.removeItem(k));
      }
    };

    // LEDGER ENGINE: Single Source of Truth for Deterministic Calculations
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
      },
      // Deterministic calculation for Safe-to-Spend Daily Limit
      calculateSafeToSpend: (accounts, transactions, customDailyBudget = 0) => {
        const now = new Date();
        const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
        const currentDay = now.getDate();
        const daysRemaining = Math.max(1, daysInMonth - currentDay + 1);

        const totalBalance = Ledger.getTotalBalance(accounts, transactions);

        // This month's total expenses
        const currentMonthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        const monthlyTxs = (transactions || []).filter(t => t && t.date && t.date.startsWith(currentMonthStr));
        const spentThisMonth = monthlyTxs
          .filter(t => t.type === 'EXPENSE')
          .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);

        // Today's total expenses
        const todayStr = now.toISOString().split('T')[0];
        const spentToday = (transactions || [])
          .filter(t => t && t.date === todayStr && t.type === 'EXPENSE')
          .reduce((acc, t) => acc + (Number(t.amount) || 0), 0);

        // Calculate daily allowance
        let dailyLimit = customDailyBudget > 0
          ? customDailyBudget
          : Math.max(0, Math.floor(totalBalance / daysRemaining));

        const remainingToday = Math.max(0, dailyLimit - spentToday);
        const percentUsed = dailyLimit > 0 ? Math.min(100, Math.round((spentToday / dailyLimit) * 100)) : 0;

        return {
          dailyLimit,
          spentToday,
          remainingToday,
          percentUsed,
          daysRemaining,
          spentThisMonth
        };
      },
      // Deterministic Financial Milestones & Health
      calculateMilestones: (accounts, transactions, savingsGoals, debts) => {
        const totalBalance = Ledger.getTotalBalance(accounts, transactions);
        const totalSavings = (savingsGoals || []).reduce((sum, g) => sum + (Number(g.currentAmount) || 0), 0);
        const unpaidDebts = (debts || []).filter(d => !d.isPaid && d.type === 'HUTANG').reduce((sum, d) => sum + (Number(d.amount) || 0), 0);
        const unpaidReceivables = (debts || []).filter(d => !d.isPaid && d.type === 'PIUTANG').reduce((sum, d) => sum + (Number(d.amount) || 0), 0);

        const milestones = [
          {
            id: 'm1',
            title: 'Langkah Awal',
            desc: 'Mencatat transaksi pertama di Voralet',
            isCompleted: (transactions || []).length > 0,
            icon: 'check-circle'
          },
          {
            id: 'm2',
            title: 'Dana Darurat Siaga',
            desc: 'Saldo total mencapai minimal Rp 1.000.000',
            isCompleted: totalBalance >= 1000000,
            icon: 'shield'
          },
          {
            id: 'm3',
            title: 'Penabung Cerdas',
            desc: 'Memiliki minimal satu Kantong Impian aktif',
            isCompleted: (savingsGoals || []).length > 0,
            icon: 'target'
          },
          {
            id: 'm4',
            title: 'Bebas Hutang',
            desc: 'Tidak ada tanggungan hutang yang belum lunas',
            isCompleted: unpaidDebts === 0,
            icon: 'check'
          }
        ];

        const completedCount = milestones.filter(m => m.isCompleted).length;
        const progressPct = Math.round((completedCount / milestones.length) * 100);

        return {
          milestones,
          completedCount,
          totalMilestones: milestones.length,
          progressPct,
          totalSavings,
          unpaidDebts,
          unpaidReceivables
        };
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
                className={`relative z-10 flex-1 py-2 text-center text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors duration-200 ios-btn-tap ${
                  isSelected ? 'text-slate-900 dark:text-white font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                }`}
              >
                {opt.icon && (
                  <Icon name={opt.icon} className={`w-3.5 h-3.5 ${opt.iconColor || ''}`} strokeWidth={2.4} />
                )}
                <span>{opt.label}</span>
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
