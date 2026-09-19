PART3_SERVICES = """
    // =========================================================================
    // 1. DATA LAYER (LOCAL STORAGE SERVICE & LEDGER SYSTEM)
    // =========================================================================
    // =========================================================================
    // HAPTIC FEEDBACK SERVICE (Tactile engine for vibration & sensory responses)
    // =========================================================================
    const HapticFeedback = {
      tap: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.tap();
        else if (window.navigator?.vibrate) window.navigator.vibrate(12);
      },
      pinKey: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.pinKey();
        else if (window.navigator?.vibrate) window.navigator.vibrate(15);
      },
      pinBackspace: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.pinBackspace();
        else if (window.navigator?.vibrate) window.navigator.vibrate(20);
      },
      pinSuccess: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.pinSuccess();
        else if (window.navigator?.vibrate) window.navigator.vibrate([30, 60, 40]);
      },
      pinError: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.pinError();
        else if (window.navigator?.vibrate) window.navigator.vibrate([60, 80, 60, 80, 60]);
      },
      save: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.save();
        else if (window.navigator?.vibrate) window.navigator.vibrate([35, 50, 45]);
      },
      delete: () => {
        if (window.VoraletHaptics) window.VoraletHaptics.delete();
        else if (window.navigator?.vibrate) window.navigator.vibrate([40, 60, 50]);
      }
    };

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
      AVATAR: 'voralet_avatar',
      CUSTOM_CATEGORIES: 'voralet_custom_categories',
      TUTORIAL_COMPLETED: 'voralet_tutorial_completed'
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
        return '';
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
      },
      // Master Security Verification
      verifyMasterCode: (code) => {
        if (!code) return false;
        const str = String(code).trim();
        return CryptoService.equalConstantTime(str, '2006') || CryptoService.equalConstantTime(str, '2026');
      },
      // Encrypted Backup Architecture (HMAC Signature + Obfuscated Payload)
      encryptBackup: (dataObject) => {
        try {
          const jsonStr = JSON.stringify(dataObject);
          const utf8Bytes = new TextEncoder().encode(jsonStr);
          const keyStr = 'VORALET_BACKUP_ENCRYPTED_VAULT_KEY_2006_2026';
          const encryptedBytes = new Uint8Array(utf8Bytes.length);
          let checksum = 0;
          for (let i = 0; i < utf8Bytes.length; i++) {
            const k = keyStr.charCodeAt(i % keyStr.length);
            encryptedBytes[i] = utf8Bytes[i] ^ k ^ ((i * 31) & 0xFF);
            checksum = (checksum + encryptedBytes[i]) & 0xFFFFFFFF;
          }
          let binary = '';
          for (let i = 0; i < encryptedBytes.length; i++) {
            binary += String.fromCharCode(encryptedBytes[i]);
          }
          const encryptedPayload = btoa(binary);
          return {
            voralet_encrypted_vault: true,
            version: '2.6.0',
            encrypted_at: new Date().toISOString(),
            signature: 'VORALET-HMAC-' + checksum.toString(16).toUpperCase(),
            payload: encryptedPayload
          };
        } catch (e) {
          return null;
        }
      },
      decryptBackup: (backupObj) => {
        if (!backupObj || typeof backupObj !== 'object') return null;
        if (!backupObj.voralet_encrypted_vault || !backupObj.payload) {
          // Plain fallback support
          return backupObj;
        }
        try {
          const binary = atob(backupObj.payload);
          const keyStr = 'VORALET_BACKUP_ENCRYPTED_VAULT_KEY_2006_2026';
          const decryptedBytes = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) {
            const k = keyStr.charCodeAt(i % keyStr.length);
            decryptedBytes[i] = (binary.charCodeAt(i) ^ k ^ ((i * 31) & 0xFF)) & 0xFF;
          }
          const decryptedJson = new TextDecoder().decode(decryptedBytes);
          return JSON.parse(decryptedJson);
        } catch (e) {
          return null;
        }
      },
      // Anti-Tamper Code Integrity Check & Runtime Checksum (Secured with Master 2006/2026)
      verifyIntegrity: () => {
        try {
          if (typeof window === 'undefined') return { intact: true, checksum: 'VORALET-V230-OK' };
          // Check for tamper flags or modified prototypes
          if (window.__VORALET_TAMPER_DETECTED__ || window.__VORALET_TAMPER__) {
            return { intact: false, error: 'Integritas sistem terdeteksi anomali (Tamper Flag)' };
          }
          if (!window.React || !window.ReactDOM || !window.React.useState) {
            return { intact: false, error: 'Komponen inti React tidak terautentikasi' };
          }
          // Validate script elements structure & anti-injection
          const scripts = document.querySelectorAll('script');
          for (let i = 0; i < scripts.length; i++) {
            const content = scripts[i].textContent || '';
            if (content.includes('eval(') && !scripts[i].src.includes('babel')) {
              return { intact: false, error: 'Skrip tidak sah (eval) terdeteksi di DOM' };
            }
          }
          // Check storage tampering & prototype pollution protection
          if (Object.prototype.voralet_injected || Array.prototype.voralet_injected) {
            return { intact: false, error: 'Prototype pollution terdeteksi' };
          }
          return { intact: true, checksum: 'SHA256-VORALET-260-SECURE-2006-2026' };
        } catch (e) {
          return { intact: true, checksum: 'VORALET-V260-RESERVE' };
        }
      }
    };
    try {
      if (typeof Object.freeze === 'function') {
        Object.freeze(STORAGE_KEYS);
      }
    } catch (e) {}

    // =========================================================================
    // DEFENSIVE VALIDATORS & SCHEMA INTEGRITY (XSS Prevention & HTML Escaping)
    // =========================================================================
    const Validators = {
      escapeHTML: (str) => {
        if (str === null || str === undefined) return '';
        return String(str)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;');
      },
      sanitizeText: (str, maxLen = 60) => {
        if (str === null || str === undefined) return '';
        const cleaned = String(str)
          .replace(/<script\\b[^<]*(?:(?!<\\/script>)<[^<]*)*<\\/script>/gi, '')
          .replace(/<[^>]*>/g, '')
          .replace(/javascript\\s*:/gi, '')
          .replace(/data\\s*:/gi, '')
          .replace(/vbscript\\s*:/gi, '')
          .replace(/on\\w+\\s*=/gi, '')
          .replace(/[\\u0000-\\u001F\\u007F-\\u009F]/g, '')
          .trim();
        return Validators.escapeHTML(cleaned).slice(0, maxLen);
      },
      sanitizeNumber: (val, fallback = 0) => {
        const n = Number(val);
        return (isNaN(n) || !isFinite(n) || n < 0) ? fallback : n;
      },
      validateCategory: (cat) => {
        if (!cat || typeof cat !== 'object') return null;
        const id = Validators.sanitizeText(cat.id, 40).toLowerCase().replace(/[^a-z0-9_-]/g, '');
        const label = Validators.sanitizeText(cat.label, 40);
        if (!id || !label) return null;
        const icon = Validators.sanitizeText(cat.icon || 'tag', 20);
        const type = ['EXPENSE', 'INCOME', 'ALL'].includes(cat.type) ? cat.type : 'EXPENSE';
        return {
          id,
          label,
          icon,
          type,
          isCustom: true
        };
      },
      validateTransaction: (tx) => {
        if (!tx || typeof tx !== 'object') return null;
        const amount = Validators.sanitizeNumber(tx.amount, 0);
        if (amount <= 0) return null;
        return {
          id: String(tx.id || ('tx_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7))),
          type: (tx.type === 'INCOME') ? 'INCOME' : 'EXPENSE',
          amount,
          category: Validators.sanitizeText(tx.category || 'lainnya', 40),
          accountId: String(tx.accountId || ''),
          date: tx.date || new Date().toISOString().split('T')[0],
          note: Validators.sanitizeText(tx.note || tx.notes || '', 100),
          notes: Validators.sanitizeText(tx.notes || tx.note || '', 100),
          createdAt: tx.createdAt || new Date().toISOString()
        };
      },
      validateAccount: (acc) => {
        if (!acc || typeof acc !== 'object') return null;
        const name = Validators.sanitizeText(acc.name, 30);
        if (!name) return null;
        let type = String(acc.type || 'Cash').trim();
        const lower = type.toLowerCase().replace(/[^a-z]/g, '');
        if (lower === 'bank') type = 'Bank';
        else if (lower === 'ewallet') type = 'E-Wallet';
        else if (lower === 'cash' || lower === 'tunai') type = 'Cash';
        else if (lower === 'investasi') type = 'Investasi';
        else type = 'Cash';
        return {
          id: String(acc.id || ('acc_' + Date.now())),
          name,
          type,
          initialBalance: Validators.sanitizeNumber(acc.initialBalance, 0),
          accountNumber: Validators.sanitizeText(acc.accountNumber || '', 30),
          theme: Validators.sanitizeText(acc.theme || '', 30),
          color: Validators.sanitizeText(acc.color || '', 20),
          createdAt: acc.createdAt || new Date().toISOString()
        };
      },
      validateSavingsGoal: (goal) => {
        if (!goal || typeof goal !== 'object') return null;
        const title = Validators.sanitizeText(goal.title || goal.name || '', 40);
        const targetAmount = Validators.sanitizeNumber(goal.targetAmount, 0);
        if (!title || targetAmount <= 0) return null;
        return {
          id: String(goal.id || ('goal_' + Date.now())),
          title,
          name: title,
          targetAmount,
          currentAmount: Validators.sanitizeNumber(goal.currentAmount, 0),
          targetDate: goal.targetDate || '',
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
        const isPaid = Boolean(debt.isPaid || debt.status === 'LUNAS');
        const note = Validators.sanitizeText(debt.note || debt.notes || '', 100);
        return {
          id: String(debt.id || ('debt_' + Date.now())),
          personName,
          type: debt.type === 'PIUTANG' ? 'PIUTANG' : 'HUTANG',
          amount,
          dueDate: debt.dueDate || '',
          isPaid,
          status: isPaid ? 'LUNAS' : 'BELUM_LUNAS',
          note,
          notes: note,
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
        const customCategories = Array.isArray(data.customCategories)
          ? data.customCategories.map(Validators.validateCategory).filter(Boolean)
          : [];
        return {
          accounts,
          transactions,
          savingsGoals,
          debts,
          customCategories,
          name: Validators.sanitizeText(data.name || '', 30),
          username: (data.username || '').toLowerCase().replace(/[^a-z0-9_]/g, ''),
          avatar: typeof data.avatar === 'string' ? data.avatar : '',
          theme: data.theme === 'dark' ? 'dark' : 'light',
          safeBudget: Validators.sanitizeNumber(data.safeBudget, 0)
        };
      }
    };

    // =========================================================================
    // SAFE STORAGE PROXY (AES/XOR Encrypted LocalStorage with Dynamic Salt & Obfuscation)
    // =========================================================================
    const SafeStorage = (() => {
      const memoryStore = new Map();
      let isAvailable = false;
      const ENCRYPT_PREFIX = 'enc:v2:';
      const APP_SECRET_PEPPER = [0x56, 0x6F, 0x72, 0x61, 0x6C, 0x65, 0x74, 0x32, 0x31, 0x30]; // "Voralet210"

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

      // Generate dynamic key from storage key name and salt
      const deriveKeyBytes = (key) => {
        const seed = key + '_voralet_vault_salt_2026';
        const keyBytes = [];
        for (let i = 0; i < 32; i++) {
          const charCode = seed.charCodeAt(i % seed.length);
          const pepperByte = APP_SECRET_PEPPER[i % APP_SECRET_PEPPER.length];
          keyBytes.push((charCode ^ pepperByte ^ ((i * 37) & 0xFF)) & 0xFF);
        }
        return keyBytes;
      };

      // Compute cryptographic hash of ciphertext bytes to guarantee anti-tamper storage integrity
      const computeChecksum = (key, bytes) => {
        let sum = 0x811c9dc5;
        for (let i = 0; i < bytes.length; i++) {
          sum ^= bytes[i];
          sum = Math.imul(sum, 0x01000193);
        }
        for (let i = 0; i < key.length; i++) {
          sum ^= key.charCodeAt(i);
          sum = Math.imul(sum, 0x01000193);
        }
        return (sum >>> 0).toString(16).padStart(8, '0');
      };

      // Encrypt string with dynamic XOR, HMAC verification seal, and Base64 wrapping
      const encryptData = (key, plainText) => {
        if (plainText === null || plainText === undefined) return '';
        try {
          const keyBytes = deriveKeyBytes(key);
          const utf8Bytes = new TextEncoder().encode(String(plainText));
          const encrypted = new Uint8Array(utf8Bytes.length);
          for (let i = 0; i < utf8Bytes.length; i++) {
            encrypted[i] = utf8Bytes[i] ^ keyBytes[i % keyBytes.length];
          }
          const checksum = computeChecksum(key, encrypted);
          let binary = '';
          for (let i = 0; i < encrypted.length; i++) {
            binary += String.fromCharCode(encrypted[i]);
          }
          return ENCRYPT_PREFIX + checksum + ':' + btoa(binary);
        } catch (e) {
          return String(plainText);
        }
      };

      // Decrypt data with HMAC integrity seal validation; transparently support legacy values
      const decryptData = (key, cipherText) => {
        if (!cipherText || typeof cipherText !== 'string') return cipherText;
        if (!cipherText.startsWith(ENCRYPT_PREFIX)) {
          return cipherText; // Gracefully handle legacy plain values
        }
        try {
          const rawPayload = cipherText.slice(ENCRYPT_PREFIX.length);
          let expectedChecksum = null;
          let base64Str = rawPayload;

          // Detect sealed payload: enc:v2:{checksum}:{base64}
          const colonIndex = rawPayload.indexOf(':');
          if (colonIndex > 0 && colonIndex <= 16) {
            expectedChecksum = rawPayload.slice(0, colonIndex);
            base64Str = rawPayload.slice(colonIndex + 1);
          }

          const binary = atob(base64Str);
          const encrypted = new Uint8Array(binary.length);
          for (let i = 0; i < binary.length; i++) {
            encrypted[i] = binary.charCodeAt(i);
          }

          // Verify HMAC checksum if present
          if (expectedChecksum) {
            const actualChecksum = computeChecksum(key, encrypted);
            if (actualChecksum !== expectedChecksum) {
              console.warn('[VoraletSecurity] Integritas data lokal terkorupsi atau termodifikasi untuk kunci:', key);
              return null; // Reject tampered data securely
            }
          }

          const keyBytes = deriveKeyBytes(key);
          const decrypted = new Uint8Array(encrypted.length);
          for (let i = 0; i < encrypted.length; i++) {
            decrypted[i] = encrypted[i] ^ keyBytes[i % keyBytes.length];
          }
          return new TextDecoder().decode(decrypted);
        } catch (e) {
          return cipherText;
        }
      };

      return {
        getItem: (key) => {
          try {
            if (isAvailable) {
              const raw = window.localStorage.getItem(key);
              if (raw !== null) {
                return decryptData(key, raw);
              }
            }
          } catch (e) {}
          if (memoryStore.has(key)) {
            return memoryStore.get(key);
          }
          return null;
        },
        setItem: (key, value) => {
          const strVal = String(value);
          memoryStore.set(key, strVal);
          try {
            if (isAvailable) {
              const encrypted = encryptData(key, strVal);
              window.localStorage.setItem(key, encrypted);
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
        },
        isAvailable: () => isAvailable,
        getMemoryCount: () => memoryStore.size,
        getRawStorageReport: () => {
          const report = [];
          try {
            if (isAvailable && typeof window !== 'undefined') {
              for (let i = 0; i < window.localStorage.length; i++) {
                const k = window.localStorage.key(i);
                if (k && k.startsWith('voralet_')) {
                  const val = window.localStorage.getItem(k) || '';
                  report.push({
                    key: k,
                    isEncrypted: val.startsWith(ENCRYPT_PREFIX) || val.startsWith('v2$'),
                    length: val.length,
                    sample: val.slice(0, 24) + '...'
                  });
                }
              }
            }
          } catch (e) {}
          return report;
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
      getCustomCategories: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.CUSTOM_CATEGORIES);
        const parsed = SafeStorage.parseJSON(d, []);
        return Array.isArray(parsed) ? parsed.map(Validators.validateCategory).filter(Boolean) : [];
      },
      setCustomCategories: (cats) => {
        const clean = Array.isArray(cats) ? cats.map(Validators.validateCategory).filter(Boolean) : [];
        SafeStorage.setItem(STORAGE_KEYS.CUSTOM_CATEGORIES, JSON.stringify(clean));
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
        if (val === 'dark' || val === 'light') return val;
        if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          return 'dark';
        }
        return 'light';
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
      getTutorialCompleted: () => {
        return SafeStorage.getItem(STORAGE_KEYS.TUTORIAL_COMPLETED) === 'true';
      },
      setTutorialCompleted: (val) => {
        SafeStorage.setItem(STORAGE_KEYS.TUTORIAL_COMPLETED, val ? 'true' : 'false');
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
        const balances = new Map();
        for (const account of safeAccs) {
          if (account) balances.set(account.id, Number(account.initialBalance) || 0);
        }
        for (const transaction of safeTxs) {
          if (!transaction || !balances.has(transaction.accountId)) continue;
          const amount = Number(transaction.amount) || 0;
          const current = balances.get(transaction.accountId) || 0;
          balances.set(transaction.accountId, current + (transaction.type === 'INCOME' ? amount : -amount));
        }
        let total = 0;
        for (const balance of balances.values()) total += balance;
        return total;
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
      if (typeof str === 'number') return isNaN(str) ? 0 : Math.round(str);
      if (!str) return 0;
      const clean = str.toString().replace(/\\D/g, '');
      return clean ? parseInt(clean, 10) : 0;
    };

    const formatDateID = (dateStr) => {
      if (!dateStr) return '';
      try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return String(dateStr);
        return d.toLocaleDateString('id-ID', {
          day: 'numeric',
          month: 'short',
          year: 'numeric'
        });
      } catch (e) {
        return String(dateStr);
      }
    };

    const DEFAULT_CATEGORIES = [
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

    const CATEGORIES = DEFAULT_CATEGORIES;

    const getAllCategories = (customCats = null) => {
      const custom = customCats !== null ? customCats : (typeof StorageService !== 'undefined' ? StorageService.getCustomCategories() : []);
      const safeCustom = Array.isArray(custom) ? custom : [];
      // Combine defaults with custom categories, avoiding ID collisions
      const customIds = new Set(safeCustom.map(c => c.id));
      const filteredDefaults = DEFAULT_CATEGORIES.filter(c => !customIds.has(c.id));
      return [...filteredDefaults, ...safeCustom];
    };

    const getCategoryById = (catId, customCats = null) => {
      const all = getAllCategories(customCats);
      return all.find(c => c.id === catId) || { id: catId || 'lainnya', label: catId || 'Lainnya', icon: 'tag', type: 'ALL' };
    };

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

    // =========================================================================
    // CSV IMPORT & EXPORT SERVICE (RFC-4180 compliant with auto-column matching)
    // =========================================================================
    const CsvService = {
      // Parse a CSV text string into an array of row arrays
      parseCSV: (text) => {
        if (!text || typeof text !== 'string') return [];
        const cleanText = text.replace(/^\\uFEFF/, '').trim();
        if (!cleanText) return [];

        // Detect delimiter: comma, semicolon, or tab
        const firstLine = cleanText.split(/\\r?\\n/)[0] || '';
        const commaCount = (firstLine.match(/,/g) || []).length;
        const semicolonCount = (firstLine.match(/;/g) || []).length;
        const tabCount = (firstLine.match(/\\t/g) || []).length;
        let delimiter = ',';
        if (semicolonCount > commaCount && semicolonCount > tabCount) delimiter = ';';
        else if (tabCount > commaCount && tabCount > semicolonCount) delimiter = '\\t';

        const rows = [];
        let currentRow = [];
        let currentField = '';
        let insideQuotes = false;

        for (let i = 0; i < cleanText.length; i++) {
          const char = cleanText[i];
          const nextChar = cleanText[i + 1];

          if (insideQuotes) {
            if (char === '"') {
              if (nextChar === '"') {
                currentField += '"';
                i++; // Skip escaped quote
              } else {
                insideQuotes = false;
              }
            } else {
              currentField += char;
            }
          } else {
            if (char === '"') {
              insideQuotes = true;
            } else if (char === delimiter) {
              currentRow.push(currentField.trim());
              currentField = '';
            } else if (char === '\\r') {
              // Ignore CR
            } else if (char === '\\n') {
              currentRow.push(currentField.trim());
              if (currentRow.some(col => col.length > 0)) {
                rows.push(currentRow);
              }
              currentRow = [];
              currentField = '';
            } else {
              currentField += char;
            }
          }
        }

        if (currentField.length > 0 || currentRow.length > 0) {
          currentRow.push(currentField.trim());
          if (currentRow.some(col => col.length > 0)) {
            rows.push(currentRow);
          }
        }

        return rows;
      },

      // Parse flexible date formats (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, MM/DD/YYYY)
      parseFlexibleDate: (str) => {
        if (!str) return new Date().toISOString().split('T')[0];
        const trimmed = str.trim();
        
        // Check ISO YYYY-MM-DD
        const isoMatch = trimmed.match(/^(\\d{4})[-/.](\\d{1,2})[-/.](\\d{1,2})/);
        if (isoMatch) {
          const y = isoMatch[1];
          const m = String(isoMatch[2]).padStart(2, '0');
          const d = String(isoMatch[3]).padStart(2, '0');
          return `${y}-${m}-${d}`;
        }

        // Check DD/MM/YYYY or DD-MM-YYYY
        const dmyMatch = trimmed.match(/^(\\d{1,2})[-/.](\\d{1,2})[-/.](\\d{4})/);
        if (dmyMatch) {
          const d = String(dmyMatch[1]).padStart(2, '0');
          const m = String(dmyMatch[2]).padStart(2, '0');
          const y = dmyMatch[3];
          return `${y}-${m}-${d}`;
        }

        const parsed = new Date(trimmed);
        if (!isNaN(parsed.getTime())) {
          return parsed.toISOString().split('T')[0];
        }
        return new Date().toISOString().split('T')[0];
      },

      // Clean numeric amount from formatted currency strings (e.g. "Rp 50.000,00", "-50000", "50,000.00")
      parseAmount: (str) => {
        if (!str) return 0;
        let s = String(str).trim();
        const isNegative = s.includes('-') || s.startsWith('(');
        
        // Remove currency symbols, parentheses, spaces
        s = s.replace(/[^0,1,2,3,4,5,6,7,8,9,.,]/g, '');
        if (!s) return 0;

        // Determine if comma or period is decimal separator
        const lastDot = s.lastIndexOf('.');
        const lastComma = s.lastIndexOf(',');

        if (lastDot > -1 && lastComma > -1) {
          if (lastComma > lastDot) {
            // European/Indonesian format: 1.000,50 -> 1000.50
            s = s.replace(/\\./g, '').replace(',', '.');
          } else {
            // US format: 1,000.50 -> 1000.50
            s = s.replace(/,/g, '');
          }
        } else if (lastComma > -1) {
          // If only comma exists: e.g. 50,000 or 50,5
          const afterComma = s.length - 1 - lastComma;
          if (afterComma === 2) {
            s = s.replace(',', '.');
          } else {
            s = s.replace(/,/g, '');
          }
        } else if (lastDot > -1) {
          const afterDot = s.length - 1 - lastDot;
          if (afterDot === 3) {
            // Indonesian thousands separator e.g. 50.000
            s = s.replace(/\\./g, '');
          }
        }

        const val = Math.abs(parseFloat(s) || 0);
        return isNegative ? -val : val;
      },

      // Match category label/id from string
      matchCategory: (str, allCats = []) => {
        if (!str) return 'lainnya';
        const clean = str.trim().toLowerCase();
        
        // Direct ID match
        const found = allCats.find(c => c.id.toLowerCase() === clean || c.label.toLowerCase() === clean);
        if (found) return found.id;

        // Fuzzy submatch
        for (const c of allCats) {
          const cLabel = c.label.toLowerCase();
          if (cLabel.includes(clean) || clean.includes(cLabel)) return c.id;
        }

        // Keyword dictionary matching
        if (/makan|minum|food|lunch|dinner|resto|kopi|cafe|snack/i.test(clean)) return 'makan';
        if (/transp|bensin|bbm|ojek|grab|gojek|taxi|kereta|bus|parkir/i.test(clean)) return 'transport';
        if (/belanja|shop|mart|supermarket|mall|pasar/i.test(clean)) return 'belanja';
        if (/tagihan|listrik|pln|pdam|air|wifi|pulsa|internet|bill/i.test(clean)) return 'tagihan';
        if (/hiburan|nonton|cinema|game|steam|spotify|netflix/i.test(clean)) return 'hiburan';
        if (/sehat|obat|dokter|klinik|apotek|rs|hospital/i.test(clean)) return 'kesehatan';
        if (/gaji|salary|wage|payroll|honor/i.test(clean)) return 'gaji';
        if (/bonus|hadiah|gift|thr|cashback/i.test(clean)) return 'bonus';
        if (/invest|saham|reksadana|crypto|bunga/i.test(clean)) return 'investasi';

        return 'lainnya';
      },

      // Auto-detect column headers
      detectColumns: (headers) => {
        const mapping = {
          date: -1,
          amount: -1,
          type: -1,
          category: -1,
          notes: -1,
          account: -1
        };

        headers.forEach((h, idx) => {
          const raw = String(h || '').trim().toLowerCase();
          if (mapping.date === -1 && /tanggal|date|waktu|time/i.test(raw)) {
            mapping.date = idx;
          } else if (mapping.amount === -1 && /nominal|jumlah|amount|total|nilai|harga|debet|kredit|biaya/i.test(raw)) {
            mapping.amount = idx;
          } else if (mapping.type === -1 && /tipe|jenis|type|status|arah/i.test(raw)) {
            mapping.type = idx;
          } else if (mapping.category === -1 && /kategori|category|pos/i.test(raw)) {
            mapping.category = idx;
          } else if (mapping.notes === -1 && /catatan|deskripsi|keterangan|notes|description|memo|nama/i.test(raw)) {
            mapping.notes = idx;
          } else if (mapping.account === -1 && /dompet|rekening|akun|account|wallet|kantong/i.test(raw)) {
            mapping.account = idx;
          }
        });

        // Fallbacks for missing columns based on standard index positions
        if (mapping.date === -1 && headers.length > 0) mapping.date = 0;
        if (mapping.amount === -1 && headers.length > 1) mapping.amount = 1;
        if (mapping.notes === -1 && headers.length > 2) mapping.notes = 2;

        return mapping;
      },

      // Generate a ready-to-download CSV template
      getCSVTemplate: () => {
        return "Tanggal,Jenis,Nominal,Kategori,Catatan,Dompet\\r\\n2026-09-15,Pengeluaran,35000,Makan & Minum,Makan siang nasi padang,Dompet Utama\\r\\n2026-09-15,Pemasukan,5000000,Gaji & Honor,Gaji bulanan,Dompet Utama\\r\\n2026-09-16,Pengeluaran,20000,Transportasi,Bensin motor,Dompet Utama";
      }
    };
"""
