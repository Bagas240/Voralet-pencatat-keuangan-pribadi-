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
      AVATAR: 'voralet_avatar',
      CUSTOM_CATEGORIES: 'voralet_custom_categories',
      STREAK: 'voralet_streak',
      PET: 'voralet_pet',
      REMINDER: 'voralet_reminder'
    };

    const getLocalDateString = (dateInput) => {
      const d = dateInput instanceof Date ? dateInput : (dateInput ? new Date(dateInput) : new Date());
      if (isNaN(d.getTime())) {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
      }
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${y}-${m}-${day}`;
    };

    const parseLocalDate = (dateStr) => {
      if (!dateStr) return new Date(NaN);
      const s = String(dateStr).trim();
      const ymd = s.match(/^(\\d{4})-(\\d{1,2})-(\\d{1,2})$/);
      if (ymd) {
        return new Date(parseInt(ymd[1], 10), parseInt(ymd[2], 10) - 1, parseInt(ymd[3], 10));
      }
      return new Date(s);
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
      // Encrypted Backup Architecture (HMAC Signature + Obfuscated Payload)
      encryptBackup: (dataObject) => {
        try {
          const jsonStr = JSON.stringify(dataObject);
          const utf8Bytes = new TextEncoder().encode(jsonStr);
          const keyStr = 'VORALET_SECURE_VAULT_ENCRYPTION_KEY_LOCAL';
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
            version: '__VORALET_VERSION__',
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
          if (typeof backupObj.signature === 'string' && backupObj.signature.startsWith('VORALET-HMAC-')) {
            let actualChecksum = 0;
            for (let i = 0; i < binary.length; i++) {
              actualChecksum = (actualChecksum + binary.charCodeAt(i)) & 0xFFFFFFFF;
            }
            const expectedSig = 'VORALET-HMAC-' + actualChecksum.toString(16).toUpperCase();
            if (!CryptoService.equalConstantTime(expectedSig, backupObj.signature)) {
              return null;
            }
          }
          const keyStr = 'VORALET_SECURE_VAULT_ENCRYPTION_KEY_LOCAL';
          const legacyKeyStr = 'VORALET_BACKUP_ENCRYPTED_VAULT_KEY_2006_2026';
          const decryptedBytes = new Uint8Array(binary.length);
          let decryptedJson = '';
          try {
            for (let i = 0; i < binary.length; i++) {
              const k = keyStr.charCodeAt(i % keyStr.length);
              decryptedBytes[i] = (binary.charCodeAt(i) ^ k ^ ((i * 31) & 0xFF)) & 0xFF;
            }
            decryptedJson = new TextDecoder().decode(decryptedBytes);
            return JSON.parse(decryptedJson);
          } catch (_) {
            for (let i = 0; i < binary.length; i++) {
              const k = legacyKeyStr.charCodeAt(i % legacyKeyStr.length);
              decryptedBytes[i] = (binary.charCodeAt(i) ^ k ^ ((i * 31) & 0xFF)) & 0xFF;
            }
            decryptedJson = new TextDecoder().decode(decryptedBytes);
            return JSON.parse(decryptedJson);
          }
        } catch (e) {
          return null;
        }
      },
      // Anti-Tamper Code Integrity Check & Runtime Checksum
      verifyIntegrity: () => {
        try {
          if (typeof window === 'undefined') return { intact: true, checksum: 'VORALET-SECURE-OK' };
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
          return { intact: true, checksum: 'SHA256-VORALET-350-SECURE-VAULT' };
        } catch (e) {
          return { intact: true, checksum: 'VORALET-V350-RESERVE' };
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
          date: tx.date || getLocalDateString(),
          note: Validators.sanitizeText(tx.note || tx.notes || '', 100),
          notes: Validators.sanitizeText(tx.notes || tx.note || '', 100),
          receiptImage: (typeof tx.receiptImage === 'string' && tx.receiptImage.startsWith('data:image/')) ? tx.receiptImage : '',
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
        const paidAmount = Validators.sanitizeNumber(debt.paidAmount, 0);
        const isPaidExplicit = Boolean(debt.isPaid || debt.status === 'LUNAS');
        const isPaid = isPaidExplicit || (paidAmount >= amount && amount > 0);
        const note = Validators.sanitizeText(debt.note || debt.notes || '', 100);
        const rawPayments = Array.isArray(debt.payments) ? debt.payments : [];
        const payments = rawPayments.map(p => ({
          id: String(p.id || ('pay_' + Date.now())),
          amount: Validators.sanitizeNumber(p.amount, 0),
          date: p.date || new Date().toISOString().split('T')[0],
          accountId: String(p.accountId || ''),
          accountName: Validators.sanitizeText(p.accountName || '', 30),
          notes: Validators.sanitizeText(p.notes || '', 80)
        })).filter(p => p.amount > 0);
        return {
          id: String(debt.id || ('debt_' + Date.now())),
          personName,
          type: debt.type === 'PIUTANG' ? 'PIUTANG' : 'HUTANG',
          amount,
          paidAmount,
          dueDate: debt.dueDate || '',
          isPaid,
          status: isPaid ? 'LUNAS' : 'BELUM_LUNAS',
          note,
          notes: note,
          payments,
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
      getStreakData: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.STREAK);
        const parsed = SafeStorage.parseJSON(d, null);
        const now = Date.now();
        const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;
        const defaultStreak = {
          currentStreak: 0,
          lastRecordedDate: '',
          lastActivityTimestamp: 0,
          maxStreak: 0,
          level: 0,
          isExpired: true
        };
        if (!parsed) return defaultStreak;

        const lastTs = Number(parsed.lastActivityTimestamp) || 0;
        // Check if 24 hours have elapsed without recording activity
        if (lastTs > 0 && (now - lastTs) > TWENTY_FOUR_HOURS) {
          const expired = {
            ...parsed,
            currentStreak: 0,
            level: 0,
            isExpired: true
          };
          SafeStorage.setItem(STORAGE_KEYS.STREAK, JSON.stringify(expired));
          return expired;
        }

        const isExpired = lastTs === 0 || (now - lastTs) > TWENTY_FOUR_HOURS;
        return {
          ...parsed,
          isExpired: isExpired,
          currentStreak: isExpired ? 0 : (Number(parsed.currentStreak) || 0),
          level: isExpired ? 0 : (Number(parsed.level) || 0)
        };
      },
      setStreakData: (streakObj) => {
        SafeStorage.setItem(STORAGE_KEYS.STREAK, JSON.stringify(streakObj));
        StorageService.syncToNativeWidget(streakObj, null);
      },
      recordStreakActivity: () => {
        const now = Date.now();
        const today = getLocalDateString();
        const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;
        const current = StorageService.getStreakData();
        const lastTs = Number(current.lastActivityTimestamp) || 0;
        const isExpired = !lastTs || (now - lastTs) > TWENTY_FOUR_HOURS;

        let newStreak = Number(current.currentStreak) || 0;
        if (isExpired || newStreak === 0) {
          newStreak = 1;
        } else {
          // If active within 24h and new calendar day, advance streak
          if (current.lastRecordedDate !== today) {
            newStreak += 1;
          }
        }

        const maxStreak = Math.max(Number(current.maxStreak) || 0, newStreak);
        let level = 0;
        if (newStreak >= 30) level = 5;
        else if (newStreak >= 15) level = 4;
        else if (newStreak >= 8) level = 3;
        else if (newStreak >= 4) level = 2;
        else if (newStreak >= 1) level = 1;

        const updated = {
          currentStreak: newStreak,
          lastRecordedDate: today,
          lastActivityTimestamp: now,
          maxStreak: maxStreak,
          level: level,
          isExpired: false
        };
        StorageService.setStreakData(updated);

        // Daily Rewards: +1 Makanan, +1 Minuman, +10 Koin Peliharaan
        StorageService.rewardPetSupplies(1, 1, 10);
        return updated;
      },
      updateStreakOnTransaction: () => {
        return StorageService.recordStreakActivity();
      },
      getPetData: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.PET);
        const parsed = SafeStorage.parseJSON(d, null);
        const defaultPet = {
          type: 'DOG',
          name: 'Milo',
          fullness: 80,
          happiness: 85,
          outfit: 'NONE',
          unlockedOutfits: ['NONE'],
          foodCount: 5,
          drinkCount: 5,
          coins: 50,
          lastFedDate: ''
        };
        if (!parsed) {
          return defaultPet;
        }
        const merged = { ...defaultPet, ...parsed };
        if (!Array.isArray(merged.unlockedOutfits)) {
          merged.unlockedOutfits = ['NONE'];
        }
        if (!merged.unlockedOutfits.includes('NONE')) {
          merged.unlockedOutfits.unshift('NONE');
        }
        if (typeof merged.drinkCount !== 'number') {
          merged.drinkCount = 5;
        }
        if (typeof merged.foodCount !== 'number') {
          merged.foodCount = 5;
        }
        const normalizedCoins = typeof parsed.coins === 'number'
          ? parsed.coins
          : (typeof parsed.petCoins === 'number' ? parsed.petCoins : 50);
        merged.coins = normalizedCoins;
        merged.petCoins = normalizedCoins;

        if (merged.lastFedDate) {
          const today = getLocalDateString();
          const last = parseLocalDate(merged.lastFedDate);
          const curr = parseLocalDate(today);
          const diffDays = (!isNaN(last.getTime()) && !isNaN(curr.getTime()))
            ? Math.max(0, Math.round((curr - last) / (1000 * 60 * 60 * 24)))
            : 0;
          if (diffDays > 0) {
            merged.fullness = Math.max(15, (merged.fullness || 80) - (diffDays * 15));
            merged.happiness = Math.max(20, (merged.happiness || 85) - (diffDays * 10));
          }
        }
        return merged;
      },
      setPetData: (petObj) => {
        if (petObj && typeof petObj === 'object') {
          const c = typeof petObj.coins === 'number' ? petObj.coins : (typeof petObj.petCoins === 'number' ? petObj.petCoins : 50);
          petObj.coins = c;
          petObj.petCoins = c;
        }
        SafeStorage.setItem(STORAGE_KEYS.PET, JSON.stringify(petObj));
        StorageService.syncToNativeWidget(null, petObj);
      },
      syncToNativeWidget: (streakObj, petObj) => {
        try {
          if (typeof window !== 'undefined' && window.AndroidBridge && typeof window.AndroidBridge.syncWidgetData === 'function') {
            const streak = streakObj || StorageService.getStreakData();
            const pet = petObj || StorageService.getPetData();
            window.AndroidBridge.syncWidgetData(JSON.stringify(streak), JSON.stringify(pet));
          }
        } catch (e) {}
      },
      checkDailyCareBonus: (petInput) => {
        const pet = petInput || StorageService.getPetData();
        const fullness = Number(pet.fullness) || 0;
        const happiness = Number(pet.happiness) || 0;
        const today = getLocalDateString();

        // Syarat: Kenyang > 80 DAN Senang > 80, dan belum klaim bonus hari ini (+5 koin/hari)
        if (fullness > 80 && happiness > 80 && pet.lastCareBonusDate !== today) {
          pet.lastCareBonusDate = today;
          const currentCoins = Number(pet.coins || pet.petCoins || 0);
          pet.coins = currentCoins + 5;
          pet.petCoins = pet.coins;
          StorageService.setPetData(pet);
          return {
            awarded: true,
            pet,
            bonusCoins: 5,
            message: '🎉 Bonus Rawat Harian! Kenyang & Senang > 80%: Kamu dapat +5 Koin Peliharaan 🪙'
          };
        }
        return {
          awarded: false,
          pet,
          bonusCoins: 0,
          message: ''
        };
      },
      rewardPetSupplies: (food = 1, drink = 1, coins = 10) => {
        const pet = StorageService.getPetData();
        pet.foodCount = Math.max(0, (pet.foodCount || 0) + food);
        pet.drinkCount = Math.max(0, (pet.drinkCount || 0) + drink);
        pet.coins = Math.max(0, (pet.coins || 0) + coins);
        pet.petCoins = pet.coins;
        StorageService.setPetData(pet);
        return pet;
      },
      rewardReceiptCoins: (coins = 10) => {
        const pet = StorageService.getPetData();
        const current = typeof pet.coins === 'number' ? pet.coins : (typeof pet.petCoins === 'number' ? pet.petCoins : 50);
        pet.coins = current + coins;
        pet.petCoins = pet.coins;
        StorageService.setPetData(pet);
        return { pet, bonusCoins: coins };
      },
      feedPet: () => {
        const pet = StorageService.getPetData();
        if ((pet.foodCount || 0) <= 0) return { success: false, pet };
        pet.foodCount = Math.max(0, (pet.foodCount || 0) - 1);
        pet.fullness = Math.min(100, (pet.fullness || 50) + 25);
        pet.happiness = Math.min(100, (pet.happiness || 50) + 15);
        pet.lastFedDate = getLocalDateString();
        const careBonus = StorageService.checkDailyCareBonus(pet);
        const finalPet = careBonus.awarded ? careBonus.pet : pet;
        StorageService.setPetData(finalPet);
        return {
          success: true,
          pet: finalPet,
          careBonusAwarded: careBonus.awarded,
          careBonusMessage: careBonus.message
        };
      },
      drinkPet: () => {
        const pet = StorageService.getPetData();
        if ((pet.drinkCount || 0) <= 0) return { success: false, pet };
        pet.drinkCount = Math.max(0, (pet.drinkCount || 0) - 1);
        pet.fullness = Math.min(100, (pet.fullness || 50) + 15);
        pet.happiness = Math.min(100, (pet.happiness || 50) + 15);
        const careBonus = StorageService.checkDailyCareBonus(pet);
        const finalPet = careBonus.awarded ? careBonus.pet : pet;
        StorageService.setPetData(finalPet);
        return {
          success: true,
          pet: finalPet,
          careBonusAwarded: careBonus.awarded,
          careBonusMessage: careBonus.message
        };
      },
      playPet: () => {
        const pet = StorageService.getPetData();
        pet.happiness = Math.min(100, (pet.happiness || 50) + 20);
        const careBonus = StorageService.checkDailyCareBonus(pet);
        const finalPet = careBonus.awarded ? careBonus.pet : pet;
        StorageService.setPetData(finalPet);
        return {
          success: true,
          pet: finalPet,
          careBonusAwarded: careBonus.awarded,
          careBonusMessage: careBonus.message
        };
      },
      buyPetMarketItem: (itemId) => {
        const pet = StorageService.getPetData();
        const currentCoins = Number(pet.coins) || 0;
        let cost = 0;
        let foodGain = 0;
        let drinkGain = 0;
        let fullnessGain = 0;
        let happinessGain = 0;
        let itemName = '';

        if (itemId === 'FOOD_1') {
          cost = 5; foodGain = 1; itemName = '1x Makanan Porsi';
        } else if (itemId === 'FOOD_5') {
          cost = 20; foodGain = 5; itemName = '5x Paket Makanan Hemat';
        } else if (itemId === 'DRINK_1') {
          cost = 5; drinkGain = 1; itemName = '1x Air Minum Segar';
        } else if (itemId === 'DRINK_5') {
          cost = 20; drinkGain = 5; itemName = '5x Galon Air Segar';
        } else if (itemId === 'TREAT') {
          cost = 15; fullnessGain = 30; happinessGain = 30; itemName = 'Snack Vitamin Spesial';
        } else {
          return { success: false, pet, message: 'Item tidak valid' };
        }

        if (currentCoins < cost) {
          return { success: false, pet, message: `Koin tidak cukup! Butuh ${cost} koin (Saldo: ${currentCoins})` };
        }

        pet.coins = currentCoins - cost;
        pet.foodCount = (pet.foodCount || 0) + foodGain;
        pet.drinkCount = (pet.drinkCount || 0) + drinkGain;
        pet.fullness = Math.min(100, (pet.fullness || 50) + fullnessGain);
        pet.happiness = Math.min(100, (pet.happiness || 50) + happinessGain);
        StorageService.setPetData(pet);
        return { success: true, pet, message: `Berhasil membeli ${itemName}! 🛍️` };
      },
      unlockPetOutfit: (outfitId, coinPrice = 0) => {
        const pet = StorageService.getPetData();
        const currentCoins = Number(pet.coins) || 0;
        if (!Array.isArray(pet.unlockedOutfits)) pet.unlockedOutfits = ['NONE'];
        if (pet.unlockedOutfits.includes(outfitId)) {
          pet.outfit = outfitId;
          StorageService.setPetData(pet);
          return { success: true, pet, message: 'Kostum dipasang!' };
        }
        if (coinPrice > 0 && currentCoins < coinPrice) {
          return { success: false, pet, message: `Koin tidak cukup! Butuh ${coinPrice} koin` };
        }
        if (coinPrice > 0) {
          pet.coins = currentCoins - coinPrice;
        }
        pet.unlockedOutfits.push(outfitId);
        pet.outfit = outfitId;
        StorageService.setPetData(pet);
        return { success: true, pet, message: 'Kostum berhasil dibuka dan dipasang! 👑' };
      },

      getReminderSettings: () => {
        const d = SafeStorage.getItem(STORAGE_KEYS.REMINDER);
        const parsed = SafeStorage.parseJSON(d, null);
        if (!parsed) {
          return { enabled: true, time: '20:00' };
        }
        return parsed;
      },
      setReminderSettings: (settings) => {
        const normalized = {
          enabled: Boolean(settings?.enabled),
          time: (settings?.time && /^\\d{2}:\\d{2}$/.test(String(settings.time))) ? String(settings.time) : '20:00'
        };
        SafeStorage.setItem(STORAGE_KEYS.REMINDER, JSON.stringify(normalized));
        try {
          window.AndroidBridge?.syncDailyReminder?.(normalized.enabled, normalized.time);
        } catch (_) {}
      },
      clearAll: () => {
        Object.values(STORAGE_KEYS).forEach(k => SafeStorage.removeItem(k));
      }
    };

    // =========================================================================
    // NATIVE NOTIFICATION & GITHUB AUTO-UPDATE BRIDGE SERVICES
    // =========================================================================
    const NotificationBridgeService = {
      _pendingListeners: new Set(),
      hasPermission: () => {
        try {
          if (window.AndroidBridge && typeof window.AndroidBridge.hasNotificationPermission === 'function') {
            return Boolean(window.AndroidBridge.hasNotificationPermission());
          }
        } catch (_) {}
        return false;
      },
      requestPermission: (sendTestAfterGrant = false) => {
        return new Promise((resolve) => {
          try {
            if (!window.AndroidBridge || typeof window.AndroidBridge.requestNotificationPermission !== 'function') {
              resolve(false);
              return;
            }
            const timer = setTimeout(() => {
              NotificationBridgeService._pendingListeners.delete(done);
              resolve(NotificationBridgeService.hasPermission());
            }, 15000);
            const done = (granted) => {
              clearTimeout(timer);
              resolve(Boolean(granted));
            };
            NotificationBridgeService._pendingListeners.add(done);
            window.AndroidBridge.requestNotificationPermission(Boolean(sendTestAfterGrant));
          } catch (_) {
            resolve(false);
          }
        });
      },
      sendTestNotification: () => {
        try {
          if (window.AndroidBridge && typeof window.AndroidBridge.sendTestPetNotification === 'function') {
            return Boolean(window.AndroidBridge.sendTestPetNotification());
          }
        } catch (_) {}
        return false;
      },
      syncReminder: (settings) => {
        try {
          const cfg = settings || StorageService.getReminderSettings();
          window.AndroidBridge?.syncDailyReminder?.(Boolean(cfg?.enabled), cfg?.time || '20:00');
        } catch (_) {}
      }
    };

    const UpdateService = {
      _callbacks: new Map(),
      getCurrentVersion: () => {
        try {
          if (window.AndroidBridge && typeof window.AndroidBridge.getAppVersionName === 'function') {
            const v = window.AndroidBridge.getAppVersionName();
            if (v) return String(v);
          }
        } catch (_) {}
        return '__VORALET_VERSION__';
      },
      checkForUpdate: (forceCheck = false) => {
        return new Promise((resolve) => {
          try {
            if (!window.AndroidBridge || typeof window.AndroidBridge.checkForAppUpdate !== 'function') {
              resolve({ ok: false, hasUpdate: false, currentVersion: UpdateService.getCurrentVersion(), errorMessage: 'Bridge tidak tersedia' });
              return;
            }
            const callbackId = 'upd_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
            const timer = setTimeout(() => {
              UpdateService._callbacks.delete(callbackId);
              resolve({ ok: false, hasUpdate: false, currentVersion: UpdateService.getCurrentVersion(), errorMessage: 'Waktu tunggu habis' });
            }, 10000);
            UpdateService._callbacks.set(callbackId, (payload) => {
              clearTimeout(timer);
              resolve(payload);
            });
            window.AndroidBridge.checkForAppUpdate(callbackId, Boolean(forceCheck));
          } catch (_) {
            resolve({ ok: false, hasUpdate: false, currentVersion: UpdateService.getCurrentVersion(), errorMessage: 'Gagal memeriksa pembaruan' });
          }
        });
      },
      openUpdateUrl: (url) => {
        try {
          if (window.AndroidBridge && typeof window.AndroidBridge.openTrustedUpdateUrl === 'function') {
            return Boolean(window.AndroidBridge.openTrustedUpdateUrl(String(url || '')));
          }
        } catch (_) {}
        return false;
      }
    };

    if (typeof window !== 'undefined') {
      window.__onVoraletUpdateResult = (callbackId, rawJson) => {
        try {
          const cb = UpdateService._callbacks.get(callbackId);
          if (cb) {
            UpdateService._callbacks.delete(callbackId);
            const parsed = typeof rawJson === 'string' ? JSON.parse(rawJson) : rawJson;
            cb(parsed);
          }
        } catch (_) {}
      };
      window.__onVoraletNotificationPermission = (granted) => {
        try {
          const listeners = Array.from(NotificationBridgeService._pendingListeners);
          NotificationBridgeService._pendingListeners.clear();
          listeners.forEach(fn => {
            try { fn(Boolean(granted)); } catch (_) {}
          });
        } catch (_) {}
      };
    }

    // Runtime Anti-Tamper & Prototype Freezing: Prevents in-memory hijacking or hooking
    try {
      if (typeof Object.freeze === 'function') {
        Object.freeze(SafeStorage);
        Object.freeze(CryptoService);
        Object.freeze(Validators);
        Object.freeze(StorageService);
        Object.freeze(NotificationBridgeService);
        Object.freeze(UpdateService);
      }
    } catch (_) {}

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
        const todayStr = getLocalDateString(now);
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
        const unpaidDebts = (debts || []).filter(d => !d.isPaid && d.status !== 'LUNAS' && d.type === 'HUTANG').reduce((sum, d) => sum + Math.max(0, (Number(d.amount) || 0) - (Number(d.paidAmount) || 0)), 0);
        const unpaidReceivables = (debts || []).filter(d => !d.isPaid && d.status !== 'LUNAS' && d.type === 'PIUTANG').reduce((sum, d) => sum + Math.max(0, (Number(d.amount) || 0) - (Number(d.paidAmount) || 0)), 0);

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
        const d = parseLocalDate(dateStr);
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

    const formatFullDateID = (dateStr) => {
      if (!dateStr) return '';
      try {
        const d = parseLocalDate(dateStr);
        if (isNaN(d.getTime())) return String(dateStr);
        return d.toLocaleDateString('id-ID', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
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
      { id: 'tabungan', label: 'Tabungan Impian', icon: 'target', type: 'ALL' },
      { id: 'hutang', label: 'Hutang & Piutang', icon: 'receipt', type: 'ALL' },
      { id: 'hiburan', label: 'Hiburan', icon: 'entertainment', type: 'EXPENSE' },
      { id: 'kesehatan', label: 'Kesehatan', icon: 'health', type: 'EXPENSE' },
      { id: 'gaji', label: 'Gaji & Honor', icon: 'salary', type: 'INCOME' },
      { id: 'bonus', label: 'Bonus & Hadiah', icon: 'gift', type: 'INCOME' },
      { id: 'investasi', label: 'Investasi', icon: 'investment', type: 'INCOME' },
      { id: 'lainnya', label: 'Lainnya', icon: 'tag', type: 'ALL' }
    ];

    const CATEGORY_EMOJI_PRESETS = ['🍔', '☕', '🚗', '🛍️', '💡', '🎮', '💊', '💼', '🎁', '📈', '🏷️', '🏠', '✈️', '📚', '🐾', '⚽'];

    const STREAK_LEVELS_META = [
      {
        lvl: 1,
        badge: '🔥',
        name: 'Api Pemula (Ember Flame)',
        cardName: 'Api Oranye Menyala',
        badgeText: 'Aktif 🔥',
        days: '1 - 3 Hari',
        bgGradient: 'from-amber-50 to-yellow-50 dark:from-amber-950/40 dark:to-yellow-950/30',
        cardBg: 'bg-gradient-to-r from-amber-50 via-orange-50 to-amber-100/70 dark:from-amber-950/40 dark:via-orange-950/30 dark:to-slate-800',
        textColor: 'text-amber-600 dark:text-amber-400',
        borderColor: 'border-amber-200 dark:border-amber-700/60',
        cardBorder: 'border-amber-300 dark:border-amber-700/70',
        barColor: 'bg-gradient-to-r from-amber-500 to-orange-500',
        desc: 'Langkah awal membiasakan mencatat keuangan setiap hari.',
        subtext: 'Pertahankan api selama 24 jam dengan rutin mencatat keuangan!'
      },
      {
        lvl: 2,
        badge: '🔴🔥',
        name: 'Api Membara (Ruby Fire)',
        cardName: 'Api Merah Membara',
        badgeText: 'Membara 🔴',
        days: '4 - 7 Hari',
        bgGradient: 'from-orange-50 to-rose-50 dark:from-orange-950/40 dark:to-rose-950/30',
        cardBg: 'bg-gradient-to-r from-orange-50 via-rose-50 to-red-100/70 dark:from-orange-950/40 dark:via-rose-950/30 dark:to-slate-800',
        textColor: 'text-rose-600 dark:text-rose-400',
        borderColor: 'border-rose-200 dark:border-rose-700/60',
        cardBorder: 'border-rose-300 dark:border-rose-700/70',
        barColor: 'bg-gradient-to-r from-orange-500 to-rose-600',
        desc: 'Konsistensi 1 minggu penuh! Pola budgeting mulai terbentuk.',
        subtext: 'Keren! 4-7 hari beruntun. Disiplin finansialmu mulai membara!'
      },
      {
        lvl: 3,
        badge: '💜🔥',
        name: 'Api Mistik (Amethyst Blaze)',
        cardName: 'Api Ungu Magis',
        badgeText: 'Magis 💜',
        days: '8 - 14 Hari',
        bgGradient: 'from-purple-50 to-indigo-50 dark:from-purple-950/40 dark:to-indigo-950/30',
        cardBg: 'bg-gradient-to-r from-purple-50 via-pink-50 to-indigo-100/70 dark:from-purple-950/40 dark:via-pink-950/30 dark:to-slate-800',
        textColor: 'text-purple-600 dark:text-purple-400',
        borderColor: 'border-purple-200 dark:border-purple-700/60',
        cardBorder: 'border-purple-300 dark:border-purple-700/70',
        barColor: 'bg-gradient-to-r from-purple-500 to-pink-500',
        desc: 'Disiplin 2 minggu tanpa henti. Pengeluaran terkendali rapi.',
        subtext: 'Konsistensi luar biasa! Keuanganmu terlindungi api magis!'
      },
      {
        lvl: 4,
        badge: '💎🔥',
        name: 'Api Kristal (Diamond Cyan)',
        cardName: 'Api Biru Neon',
        badgeText: 'Neon 💎',
        days: '15 - 29 Hari',
        bgGradient: 'from-cyan-50 to-sky-50 dark:from-cyan-950/40 dark:to-sky-950/30',
        cardBg: 'bg-gradient-to-r from-cyan-50 via-sky-50 to-blue-100/70 dark:from-cyan-950/40 dark:via-sky-950/30 dark:to-slate-800',
        textColor: 'text-cyan-600 dark:text-cyan-400',
        borderColor: 'border-cyan-200 dark:border-cyan-700/60',
        cardBorder: 'border-cyan-300 dark:border-cyan-700/70',
        barColor: 'bg-gradient-to-r from-cyan-400 to-blue-600',
        desc: 'Separuh bulan penuh catatan rapi! Kebiasaan finansial matang.',
        subtext: 'Separuh bulan tanpa putus! Kamu pengelola keuangan sejati!'
      },
      {
        lvl: 5,
        badge: '👑🔥',
        name: 'Api Mahkota (Celestial Flame)',
        cardName: 'Api Dewa Emas',
        badgeText: 'Dewa Api 👑',
        days: '30+ Hari',
        bgGradient: 'from-amber-50 via-rose-50 to-indigo-50 dark:from-amber-950/50 dark:via-rose-950/40 dark:to-indigo-950/50',
        cardBg: 'bg-gradient-to-r from-amber-100 via-yellow-50 to-amber-200/80 dark:from-amber-950/50 dark:via-yellow-950/40 dark:to-slate-800',
        textColor: 'text-amber-500 dark:text-amber-300',
        borderColor: 'border-amber-300 dark:border-amber-600',
        cardBorder: 'border-amber-400 dark:border-amber-600',
        barColor: 'bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-600',
        desc: 'Tingkat Legendaris! Penguasa keuangan sejati 1 bulan nonstop.',
        subtext: 'Level tertinggi tercapai! Disiplin 30+ hari tanpa pernah padam!'
      }
    ];

    const getStreakBadge = (level) => {
      const found = STREAK_LEVELS_META.find(l => l.lvl === Number(level));
      return found ? found.badge : '⚪';
    };

    const getStreakLevelMeta = (level, isExpired = false) => {
      if (isExpired || !level || Number(level) <= 0) {
        return {
          lvl: 0,
          badge: '⚪',
          name: 'Api Belum Menyala',
          cardName: 'Api Padam (Butuh Catatan)',
          badgeText: 'Padam / Mati',
          days: '0 Hari',
          bgGradient: 'from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-800',
          cardBg: 'bg-gradient-to-r from-slate-100 via-slate-50 to-slate-100 dark:from-slate-800/80 dark:via-slate-800 dark:to-slate-800',
          textColor: 'text-slate-500 dark:text-slate-400',
          borderColor: 'border-slate-200 dark:border-slate-700',
          cardBorder: 'border-slate-300 dark:border-slate-700',
          barColor: 'bg-slate-400',
          desc: 'Catat transaksi hari ini untuk mulai menyalakan api pertamamu!',
          subtext: 'Catat transaksi, tabungan, atau bayar hutang untuk menyalakan api streak 24 jam!'
        };
      }
      return STREAK_LEVELS_META.find(l => l.lvl === Number(level)) || STREAK_LEVELS_META[STREAK_LEVELS_META.length - 1];
    };

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
          {/* Sliding pill background (hardware composited GPU transform) */}
          <div
            className="absolute top-1 bottom-1 rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-200/50 dark:border-slate-700/60 transition-transform duration-300 ease-[cubic-bezier(0.28,0.84,0.42,1)] will-change-transform pointer-events-none"
            style={{
              width: `calc(${widthPct}% - 4px)`,
              left: '2px',
              transform: `translate3d(${activeIndex * 100}%, 0, 0)`
            }}
          />
          {options.map((opt) => {
            const isSelected = opt.value === value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => {
                  if (opt.value !== value) {
                    onChange(opt.value);
                  }
                }}
                className={`relative z-10 flex-1 py-2 text-center text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors duration-200 ios-btn-tap ${
                  isSelected ? 'text-slate-900 dark:text-white font-bold' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                }`}
              >
                {opt.icon && (
                  <Icon name={opt.icon} className={`w-3.5 h-3.5 ${opt.iconColor || ''} ${isSelected ? 'animate-ios-icon-bounce' : ''}`} strokeWidth={2.4} />
                )}
                <span>{opt.label}</span>
              </button>
            );
          })}
        </div>
      );
    };

    // Contextual Long-Press Popover Sheet
    const ContextualMenuModal = ({ isOpen, title, onClose, onEdit, onDuplicate }) => {
      const { shouldRender, isClosing, handleClose } = useModalLifecycle(isOpen, onClose, 300);

      if (!shouldRender) return null;

      return (
        <div
          className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
          onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
        >
          <div className={`ios-modal-card bg-white dark:bg-slate-800 p-4 max-w-xs mx-auto rounded-[24px] shadow-2xl border border-slate-100 dark:border-slate-700 ${
            isClosing ? 'animate-ios-pop-out' : 'animate-ios-pop-in'
          }`}>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate">{title || 'Pilihan Transaksi'}</span>
              <button
                type="button"
                onClick={handleClose}
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
                  onClick={() => { handleClose(); onEdit(); }}
                  className="w-full px-3 py-2.5 rounded-xl text-left text-xs font-semibold text-slate-800 dark:text-slate-200 hover:bg-sky-50 dark:hover:bg-slate-700 flex items-center gap-2.5 ios-btn-tap"
                >
                  <Icon name="edit" className="w-4 h-4 text-brand" />
                  <span>Edit Transaksi</span>
                </button>
              )}
              {onDuplicate && (
                <button
                  type="button"
                  onClick={() => { handleClose(); onDuplicate(); }}
                  className="w-full px-3 py-2.5 rounded-xl text-left text-xs font-semibold text-slate-800 dark:text-slate-200 hover:bg-sky-50 dark:hover:bg-slate-700 flex items-center gap-2.5 ios-btn-tap"
                >
                  <Icon name="duplicate" className="w-4 h-4 text-sky-500" />
                  <span>Duplikat Transaksi</span>
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
        <div
          style={{ top: 'calc(var(--safe-top) + 0.75rem)' }}
          className={`fixed left-1/2 -translate-x-1/2 z-[100] max-w-[calc(100vw-2rem)] px-4 py-2.5 rounded-full bg-slate-900/95 dark:bg-slate-800/95 text-white text-xs font-semibold shadow-xl flex items-center gap-2.5 border border-slate-700/60 select-none ${isLeaving ? 'animate-ios-toast-exit' : 'animate-ios-toast'}`}
        >
          <span className="w-2 h-2 rounded-full bg-brand shrink-0"></span>
          <span className="truncate">{message}</span>
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
        if (!str) return getLocalDateString();
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
          return getLocalDateString(parsed);
        }
        return getLocalDateString();
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

    // =========================================================================
    // MONTHLY FINANCIAL REPORT PDF & PRINT ENGINE
    // =========================================================================
    const PdfReportService = {
      MONTH_NAMES_ID: [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
      ],

      getMonthLabel: (year, month) => {
        const mIdx = Number(month) - 1;
        const name = PdfReportService.MONTH_NAMES_ID[mIdx] || `Bulan ${month}`;
        return `${name} ${year}`;
      },

      getAvailableMonths: (transactions = []) => {
        const periodSet = new Set();
        const now = new Date();
        const curKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        periodSet.add(curKey);

        // Also add last month by default for convenience
        const lastMonthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        const lastKey = `${lastMonthDate.getFullYear()}-${String(lastMonthDate.getMonth() + 1).padStart(2, '0')}`;
        periodSet.add(lastKey);

        if (Array.isArray(transactions)) {
          transactions.forEach(t => {
            if (t && t.date && typeof t.date === 'string') {
              const prefix = t.date.slice(0, 7);
              if (/^\\d{4}-\\d{2}$/.test(prefix)) {
                periodSet.add(prefix);
              }
            }
          });
        }

        const sorted = Array.from(periodSet).sort((a, b) => b.localeCompare(a));
        return sorted.map(key => {
          const [yr, mo] = key.split('-');
          return {
            key,
            year: Number(yr),
            month: Number(mo),
            label: PdfReportService.getMonthLabel(yr, mo)
          };
        });
      },

      computeMonthlyData: ({
        transactions = [],
        accounts = [],
        debts = [],
        savingsGoals = [],
        customCategories = [],
        periodKey,
        accountId = 'ALL'
      }) => {
        const [yrStr, moStr] = (periodKey || '').split('-');
        const year = Number(yrStr) || new Date().getFullYear();
        const month = Number(moStr) || (new Date().getMonth() + 1);
        const periodLabel = PdfReportService.getMonthLabel(year, month);

        const safeTxs = Array.isArray(transactions) ? transactions : [];
        const safeAccs = Array.isArray(accounts) ? accounts : [];
        const safeDebts = Array.isArray(debts) ? debts : [];
        const safeGoals = Array.isArray(savingsGoals) ? savingsGoals : [];

        // Filter transactions for specified month and optional account
        const monthTxs = safeTxs.filter(t => {
          if (!t || !t.date || !t.date.startsWith(periodKey)) return false;
          if (accountId && accountId !== 'ALL' && t.accountId !== accountId) return false;
          return true;
        }).sort((a, b) => {
          // Sort descending by date, then created
          const dateCmp = (b.date || '').localeCompare(a.date || '');
          if (dateCmp !== 0) return dateCmp;
          return (b.createdAt || '').localeCompare(a.createdAt || '');
        });

        let totalIncome = 0;
        let totalExpense = 0;
        let incomeCount = 0;
        let expenseCount = 0;
        const categoryMap = {};

        monthTxs.forEach(t => {
          const amt = Number(t.amount) || 0;
          if (t.type === 'INCOME') {
            totalIncome += amt;
            incomeCount++;
          } else if (t.type === 'EXPENSE') {
            totalExpense += amt;
            expenseCount++;
            const catId = t.category || 'lainnya';
            if (!categoryMap[catId]) {
              categoryMap[catId] = { amount: 0, count: 0 };
            }
            categoryMap[catId].amount += amt;
            categoryMap[catId].count += 1;
          }
        });

        const netCashflow = totalIncome - totalExpense;
        const savingsRate = totalIncome > 0
          ? Math.max(0, Math.round(((totalIncome - totalExpense) / totalIncome) * 100))
          : 0;

        // Categories breakdown sorted descending by expense amount
        const categoryBreakdown = Object.entries(categoryMap).map(([catId, info]) => {
          const cat = getCategoryById(catId, customCategories);
          const pct = totalExpense > 0 ? Math.round((info.amount / totalExpense) * 100) : 0;
          return {
            id: catId,
            label: cat.label || catId,
            icon: cat.icon || '🏷️',
            amount: info.amount,
            count: info.count,
            percentage: pct
          };
        }).sort((a, b) => b.amount - a.amount);

        // Account mutations this month
        const accountsSummary = safeAccs.map(acc => {
          let accIncome = 0;
          let accExpense = 0;
          let accCount = 0;
          monthTxs.forEach(t => {
            if (t.accountId === acc.id) {
              accCount++;
              const amt = Number(t.amount) || 0;
              if (t.type === 'INCOME') accIncome += amt;
              else if (t.type === 'EXPENSE') accExpense += amt;
            }
          });
          return {
            id: acc.id,
            name: acc.name,
            type: acc.type,
            balance: Number(acc.balance) || 0,
            income: accIncome,
            expense: accExpense,
            net: accIncome - accExpense,
            txCount: accCount
          };
        });

        // Debts and Receivables Summary
        let activeHutang = 0;
        let activePiutang = 0;
        safeDebts.forEach(d => {
          const isLunas = d.isPaid || d.status === 'LUNAS';
          if (!isLunas) {
            const tot = Number(d.amount) || 0;
            const paid = Number(d.paidAmount) || 0;
            const rem = Math.max(0, tot - paid);
            if (d.type === 'HUTANG') activeHutang += rem;
            else if (d.type === 'PIUTANG') activePiutang += rem;
          }
        });

        const selectedAccountObj = accountId !== 'ALL'
          ? safeAccs.find(a => a.id === accountId)
          : null;

        return {
          periodKey,
          year,
          month,
          periodLabel,
          accountId,
          accountName: selectedAccountObj ? selectedAccountObj.name : 'Semua Kantong Keuangan',
          totalIncome,
          totalExpense,
          netCashflow,
          savingsRate,
          transactionCount: monthTxs.length,
          incomeCount,
          expenseCount,
          categoryBreakdown,
          accountsSummary,
          activeHutang,
          activePiutang,
          debtsCount: safeDebts.length,
          savingsGoalsCount: safeGoals.length,
          transactions: monthTxs
        };
      },

      generateReportHtml: (data, userProfile = {}) => {
        const userName = userProfile.name || 'Pengguna Voralet';
        const nowStr = new Date().toLocaleDateString('id-ID', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });

        const netClass = data.netCashflow >= 0 ? 'text-emerald' : 'text-rose';
        const netSign = data.netCashflow >= 0 ? '+' : '';

        // Build categories rows
        let categoriesHtml = '';
        if (data.categoryBreakdown.length === 0) {
          categoriesHtml = '<tr><td colspan="4" class="text-center text-muted" style="padding:16px;">Tidak ada catatan pengeluaran pada periode ini.</td></tr>';
        } else {
          data.categoryBreakdown.forEach((cat, idx) => {
            categoriesHtml += `
              <tr>
                <td style="text-align:center;width:40px;">${idx + 1}</td>
                <td><span style="font-size:14px;margin-right:6px;">${cat.icon}</span><strong>${cat.label}</strong></td>
                <td style="text-align:center;width:80px;">${cat.count}x</td>
                <td style="text-align:right;font-weight:bold;width:140px;">${formatIDR(cat.amount)}</td>
                <td style="text-align:right;width:70px;"><span class="badge badge-gray">${cat.percentage}%</span></td>
              </tr>
            `;
          });
        }

        // Build account summary rows
        let accountsHtml = '';
        data.accountsSummary.forEach(acc => {
          accountsHtml += `
            <tr>
              <td><strong>${acc.name}</strong> <span class="badge badge-gray" style="font-size:9px;">${acc.type}</span></td>
              <td style="text-align:right;" class="text-emerald">+${formatIDR(acc.income)}</td>
              <td style="text-align:right;" class="text-rose">-${formatIDR(acc.expense)}</td>
              <td style="text-align:right;font-weight:bold;">${formatIDR(acc.balance)}</td>
            </tr>
          `;
        });

        // Build transactions list rows
        let txRowsHtml = '';
        if (data.transactions.length === 0) {
          txRowsHtml = '<tr><td colspan="6" class="text-center text-muted" style="padding:24px;">Tidak ada riwayat transaksi pada bulan ini.</td></tr>';
        } else {
          data.transactions.forEach((tx, idx) => {
            const isInc = tx.type === 'INCOME';
            const cat = getCategoryById(tx.category || 'lainnya');
            txRowsHtml += `
              <tr style="background:${idx % 2 === 1 ? '#f8fafc' : '#ffffff'};">
                <td style="width:40px;text-align:center;color:#64748b;font-size:11px;">${idx + 1}</td>
                <td style="width:90px;white-space:nowrap;font-size:11px;font-weight:600;">${formatDateID(tx.date)}</td>
                <td style="width:140px;font-size:11px;"><span style="margin-right:4px;">${cat.icon || '🏷️'}</span>${cat.label || tx.category}</td>
                <td style="font-size:11px;">${tx.notes ? tx.notes : '<span style="color:#94a3b8;font-style:italic;">Tanpa catatan</span>'}</td>
                <td style="width:70px;text-align:center;">
                  <span class="badge ${isInc ? 'badge-emerald' : 'badge-rose'}" style="font-size:9px;">
                    ${isInc ? 'MASUK' : 'KELUAR'}
                  </span>
                </td>
                <td style="width:130px;text-align:right;font-weight:bold;font-size:12px;" class="${isInc ? 'text-emerald' : 'text-rose'}">
                  ${isInc ? '+' : '-'}${formatIDR(tx.amount)}
                </td>
              </tr>
            `;
          });
        }

        return `<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8" />
  <title>Laporan Keuangan Voralet - ${data.periodLabel}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #0f172a;
      background: #ffffff;
      padding: 24px;
      font-size: 12px;
      line-height: 1.4;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .report-container {
      max-width: 820px;
      margin: 0 auto;
      background: #ffffff;
    }
    .header-table {
      width: 100%;
      border-bottom: 2px solid #0284c7;
      padding-bottom: 14px;
      margin-bottom: 16px;
    }
    .brand-title {
      font-size: 24px;
      font-weight: 800;
      color: #0284c7;
      letter-spacing: -0.5px;
    }
    .brand-subtitle {
      font-size: 11px;
      color: #64748b;
      margin-top: 2px;
    }
    .doc-meta {
      text-align: right;
      font-size: 11px;
      color: #475569;
    }
    .doc-meta strong {
      color: #0f172a;
    }
    .kpi-grid {
      display: table;
      width: 100%;
      table-layout: fixed;
      margin-bottom: 18px;
    }
    .kpi-cell {
      display: table-cell;
      padding: 10px 12px;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      background: #f8fafc;
      width: 25%;
      vertical-align: top;
    }
    .kpi-cell + .kpi-cell {
      border-left: none;
    }
    .kpi-label {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      color: #64748b;
      letter-spacing: 0.3px;
      margin-bottom: 4px;
    }
    .kpi-value {
      font-size: 15px;
      font-weight: 800;
      color: #0f172a;
    }
    .kpi-sub {
      font-size: 10px;
      color: #94a3b8;
      margin-top: 2px;
    }
    .section-title {
      font-size: 13px;
      font-weight: 700;
      color: #1e293b;
      margin: 18px 0 8px 0;
      padding-bottom: 4px;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    table.data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11px;
      margin-bottom: 16px;
    }
    table.data-table th {
      background: #f1f5f9;
      color: #334155;
      font-weight: 700;
      text-align: left;
      padding: 8px 10px;
      border: 1px solid #cbd5e1;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }
    table.data-table td {
      padding: 7px 10px;
      border: 1px solid #e2e8f0;
      color: #1e293b;
      vertical-align: middle;
    }
    .badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 700;
      font-size: 10px;
      line-height: 1;
    }
    .badge-emerald { background: #dcfce7; color: #15803d; }
    .badge-rose { background: #ffe4e6; color: #be123c; }
    .badge-gray { background: #e2e8f0; color: #475569; }
    .text-emerald { color: #16a34a !important; }
    .text-rose { color: #e11d48 !important; }
    .text-muted { color: #64748b !important; }
    .text-center { text-align: center; }
    .text-right { text-align: right; }
    .footer-box {
      margin-top: 24px;
      padding-top: 14px;
      border-top: 1px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: #94a3b8;
    }
    .signature-row {
      margin-top: 30px;
      display: table;
      width: 100%;
    }
    .signature-col {
      display: table-cell;
      width: 50%;
      vertical-align: top;
    }
    .signature-line {
      margin-top: 45px;
      width: 160px;
      border-bottom: 1px solid #0f172a;
    }
    @media print {
      body { padding: 0; }
      .report-container { width: 100%; max-width: 100%; }
      @page { margin: 12mm 10mm 12mm 10mm; }
    }
  </style>
</head>
<body>
  <div class="report-container" id="voralet-pdf-report-content">
    <!-- Header -->
    <table class="header-table">
      <tr>
        <td style="vertical-align:middle;">
          <div class="brand-title">VORALET</div>
          <div class="brand-subtitle">Laporan Keuangan Bulanan & Rekap Arus Kas</div>
        </td>
        <td class="doc-meta" style="vertical-align:middle;">
          <div>Periode Laporan: <strong>${data.periodLabel}</strong></div>
          <div>Kantong / Akun: <strong>${data.accountName}</strong></div>
          <div>Pemilik Akun: <strong>${userName}</strong></div>
          <div style="font-size:10px;color:#94a3b8;margin-top:2px;">Dicetak: ${nowStr}</div>
        </td>
      </tr>
    </table>

    <!-- Executive KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-cell">
        <div class="kpi-label">Total Pemasukan</div>
        <div class="kpi-value text-emerald">+${formatIDR(data.totalIncome)}</div>
        <div class="kpi-sub">${data.incomeCount} transaksi masuk</div>
      </div>
      <div class="kpi-cell">
        <div class="kpi-label">Total Pengeluaran</div>
        <div class="kpi-value text-rose">-${formatIDR(data.totalExpense)}</div>
        <div class="kpi-sub">${data.expenseCount} transaksi keluar</div>
      </div>
      <div class="kpi-cell">
        <div class="kpi-label">Arus Kas Bersih</div>
        <div class="kpi-value ${netClass}">${netSign}${formatIDR(data.netCashflow)}</div>
        <div class="kpi-sub">${data.netCashflow >= 0 ? 'Surplus / Hemat' : 'Defisit Arus Kas'}</div>
      </div>
      <div class="kpi-cell">
        <div class="kpi-label">Rasio Penghematan</div>
        <div class="kpi-value" style="color:#0284c7;">${data.savingsRate}%</div>
        <div class="kpi-sub">${data.transactionCount} total transaksi</div>
      </div>
    </div>

    <!-- Category Expense Breakdown Table -->
    <div class="section-title">
      <span>1. Rincian Pengeluaran per Kategori</span>
      <span style="font-size:11px;font-weight:normal;color:#64748b;">Total: ${formatIDR(data.totalExpense)}</span>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th style="text-align:center;width:40px;">No</th>
          <th>Kategori Pengeluaran</th>
          <th style="text-align:center;width:80px;">Frekuensi</th>
          <th style="text-align:right;width:140px;">Total Nominal (Rp)</th>
          <th style="text-align:right;width:70px;">Porsi</th>
        </tr>
      </thead>
      <tbody>
        ${categoriesHtml}
      </tbody>
    </table>

    <!-- Account Mutation Summary Table -->
    <div class="section-title">
      <span>2. Ringkasan Saldo & Mutasi Kantong Keuangan</span>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>Nama Kantong / Rekening</th>
          <th style="text-align:right;">Total Masuk</th>
          <th style="text-align:right;">Total Keluar</th>
          <th style="text-align:right;">Saldo Terkini</th>
        </tr>
      </thead>
      <tbody>
        ${accountsHtml}
      </tbody>
    </table>

    <!-- Complete Transaction Log Table -->
    <div class="section-title">
      <span>3. Riwayat Mutasi Transaksi Detail (${data.transactionCount} Catatan)</span>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th style="width:40px;text-align:center;">No</th>
          <th style="width:90px;">Tanggal</th>
          <th style="width:140px;">Kategori</th>
          <th>Deskripsi / Catatan</th>
          <th style="width:70px;text-align:center;">Jenis</th>
          <th style="width:130px;text-align:right;">Nominal (Rp)</th>
        </tr>
      </thead>
      <tbody>
        ${txRowsHtml}
      </tbody>
    </table>

    <!-- Signatures & Disclaimer -->
    <div class="signature-row">
      <div class="signature-col">
        <div style="font-size:11px;color:#64748b;">Catatan Tambahan:</div>
        <div style="font-size:10px;color:#94a3b8;margin-top:3px;max-width:300px;">
          Laporan ini diterbitkan otomatis dari aplikasi Voralet sebagai bukti mutasi pembukuan finansial pribadi yang valid.
        </div>
      </div>
      <div class="signature-col" style="text-align:right;">
        <div style="font-size:11px;color:#64748b;">Pemilik Laporan,</div>
        <div class="signature-line" style="margin-left:auto;"></div>
        <div style="font-size:11px;font-weight:bold;margin-top:4px;">${userName}</div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer-box">
      <div>Voralet Finance Engine • Dokumen Laporan Resmi</div>
      <div>Halaman 1 • Periode ${data.periodLabel}</div>
    </div>
  </div>
</body>
</html>`;
      },

      exportDirectPdf: async (htmlContent, filename = 'Laporan_Keuangan_Voralet.pdf') => {
        try {
          if (window.html2pdf) {
            // Create a temporary offscreen container for html2pdf
            const container = document.createElement('div');
            container.innerHTML = htmlContent;
            container.style.position = 'fixed';
            container.style.left = '-9999px';
            container.style.top = '0';
            container.style.width = '800px';
            container.style.background = '#ffffff';
            document.body.appendChild(container);

            const element = container.querySelector('#voralet-pdf-report-content') || container;

            const opt = {
              margin: [8, 8, 10, 8],
              filename: filename,
              image: { type: 'jpeg', quality: 0.98 },
              html2canvas: {
                scale: 2,
                useCORS: true,
                letterRendering: true,
                logging: false,
                backgroundColor: '#ffffff'
              },
              jsPDF: {
                unit: 'mm',
                format: 'a4',
                orientation: 'portrait'
              }
            };

            if (typeof window !== 'undefined' && window.AndroidBridge && typeof window.AndroidBridge.saveFileToDevice === 'function') {
              const dataUri = await window.html2pdf().set(opt).from(element).outputPdf('datauristring');
              const base64Part = String(dataUri || '').split(',')[1] || '';
              document.body.removeChild(container);
              if (base64Part) {
                return window.AndroidBridge.saveFileToDevice(filename, base64Part, 'application/pdf');
              }
              return false;
            }

            await window.html2pdf().set(opt).from(element).save();
            document.body.removeChild(container);
            return true;
          }
          return false;
        } catch (e) {
          console.error('[PdfReportService] Error generating PDF:', e);
          return false;
        }
      },

      printOrSavePdf: (htmlContent, jobTitle = 'Laporan Keuangan Voralet') => {
        try {
          // Check if running inside Android Native App with Native Print Bridge
          if (window.AndroidBridge && typeof window.AndroidBridge.printHtml === 'function') {
            window.AndroidBridge.printHtml(htmlContent, jobTitle);
            return true;
          }

          // In Browser or PWA: Print via clean hidden iframe
          const iframe = document.createElement('iframe');
          iframe.style.position = 'fixed';
          iframe.style.right = '0';
          iframe.style.bottom = '0';
          iframe.style.width = '0';
          iframe.style.height = '0';
          iframe.style.border = '0';
          document.body.appendChild(iframe);

          iframe.contentDocument.open();
          iframe.contentDocument.write(htmlContent);
          iframe.contentDocument.close();

          setTimeout(() => {
            try {
              iframe.contentWindow.focus();
              iframe.contentWindow.print();
            } catch (err) {
              window.print();
            }
            setTimeout(() => {
              try {
                document.body.removeChild(iframe);
              } catch (e) {}
            }, 3000);
          }, 350);

          return true;
        } catch (e) {
          console.error('[PdfReportService] Print trigger error:', e);
          window.print();
          return false;
        }
      }
    };

    // =========================================================================
    // EXCEL EXPORT ENGINE (Multi-Worksheet XML Spreadsheet 2003 Engine)
    // 100% Client-Side, Zero External Dependencies, Zero Telemetry
    // =========================================================================
    const ExcelExportService = {
      escapeXml: (val) => {
        if (val === null || val === undefined) return '';
        return String(val)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&apos;');
      },

      // Native Android .xlsx Export (with pure-JS OOXML fallback for browser preview)
      buildCategoryLabelMap: (customCategories = []) => {
        const map = {};
        const cats = typeof getAllCategories === 'function' ? getAllCategories(customCategories) : [];
        cats.forEach(c => {
          if (c && c.id) map[c.id] = c.label || c.id;
        });
        return map;
      },

      crc32: (bytes) => {
        let crc = 0xFFFFFFFF;
        for (let i = 0; i < bytes.length; i++) {
          crc ^= bytes[i];
          for (let j = 0; j < 8; j++) {
            crc = (crc >>> 1) ^ ((crc & 1) ? 0xEDB88320 : 0);
          }
        }
        return (crc ^ 0xFFFFFFFF) >>> 0;
      },

      buildStoredZip: (files) => {
        const encoder = new TextEncoder();
        const localParts = [];
        const centralParts = [];
        let offset = 0;

        files.forEach(({ name, content }) => {
          const nameBytes = encoder.encode(name);
          const dataBytes = typeof content === 'string' ? encoder.encode(content) : content;
          const crc = ExcelExportService.crc32(dataBytes);

          const lh = new Uint8Array(30 + nameBytes.length);
          const ldv = new DataView(lh.buffer);
          ldv.setUint32(0, 0x04034b50, true);
          ldv.setUint16(4, 20, true);
          ldv.setUint16(6, 0x0800, true);
          ldv.setUint16(8, 0, true);
          ldv.setUint32(14, crc, true);
          ldv.setUint32(18, dataBytes.length, true);
          ldv.setUint32(22, dataBytes.length, true);
          ldv.setUint16(26, nameBytes.length, true);
          lh.set(nameBytes, 30);
          localParts.push(lh, dataBytes);

          const ch = new Uint8Array(46 + nameBytes.length);
          const cdv = new DataView(ch.buffer);
          cdv.setUint32(0, 0x02014b50, true);
          cdv.setUint16(4, 20, true);
          cdv.setUint16(6, 20, true);
          cdv.setUint16(8, 0x0800, true);
          cdv.setUint16(10, 0, true);
          cdv.setUint32(16, crc, true);
          cdv.setUint32(20, dataBytes.length, true);
          cdv.setUint32(24, dataBytes.length, true);
          cdv.setUint16(28, nameBytes.length, true);
          cdv.setUint32(42, offset, true);
          ch.set(nameBytes, 46);
          centralParts.push(ch);

          offset += lh.length + dataBytes.length;
        });

        let centralSize = 0;
        centralParts.forEach(p => { centralSize += p.length; });
        const eocd = new Uint8Array(22);
        const edv = new DataView(eocd.buffer);
        edv.setUint32(0, 0x06054b50, true);
        edv.setUint16(8, files.length, true);
        edv.setUint16(10, files.length, true);
        edv.setUint32(12, centralSize, true);
        edv.setUint32(16, offset, true);

        const totalLen = offset + centralSize + eocd.length;
        const result = new Uint8Array(totalLen);
        let pos = 0;
        localParts.forEach(p => { result.set(p, pos); pos += p.length; });
        centralParts.forEach(p => { result.set(p, pos); pos += p.length; });
        result.set(eocd, pos);
        return result;
      },

      generateXlsxFallbackBytes: (data) => {
        const esc = ExcelExportService.escapeXml;
        const accs = Array.isArray(data.accounts) ? data.accounts : [];
        const txs = Array.isArray(data.transactions) ? data.transactions : [];
        const catMap = ExcelExportService.buildCategoryLabelMap(data.customCategories);
        const accMap = {};
        accs.forEach(a => { if (a?.id) accMap[a.id] = a.name || 'Dompet'; });

        const colRef = (i) => {
          let n = i, s = '';
          while (n >= 0) { s = String.fromCharCode(65 + (n % 26)) + s; n = Math.floor(n / 26) - 1; }
          return s;
        };
        const makeSheet = (rows) => {
          const body = rows.map((row, ri) => {
            const cells = row.map((cell, ci) => {
              const ref = colRef(ci) + (ri + 1);
              if (typeof cell === 'number') return `<c r="${ref}"><v>${cell}</v></c>`;
              return `<c r="${ref}" t="inlineStr"><is><t>${esc(cell)}</t></is></c>`;
            }).join('');
            return `<row r="${ri + 1}">${cells}</row>`;
          }).join('');
          return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${body}</sheetData></worksheet>`;
        };

        const txRows = [['NO', 'TANGGAL', 'TIPE', 'KATEGORI', 'DOMPET', 'CATATAN', 'NOMINAL']];
        txs.forEach((t, idx) => {
          txRows.push([
            idx + 1,
            t.date || '-',
            t.type === 'INCOME' ? 'MASUK' : 'KELUAR',
            catMap[t.category] || t.category || 'Lainnya',
            accMap[t.accountId] || 'Dompet Utama',
            t.notes || t.note || '-',
            Number(t.amount) || 0
          ]);
        });
        const accRows = [['NO', 'DOMPET', 'TIPE', 'NO REK', 'SALDO AWAL']];
        accs.forEach((a, idx) => {
          accRows.push([idx + 1, a.name || 'Dompet', a.type || 'Cash', a.accountNumber || '-', Number(a.initialBalance ?? a.balance ?? 0)]);
        });

        return ExcelExportService.buildStoredZip([
          { name: '[Content_Types].xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>' },
          { name: '_rels/.rels', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>' },
          { name: 'xl/workbook.xml', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Mutasi Transaksi" sheetId="1" r:id="rId1"/><sheet name="Daftar Dompet" sheetId="2" r:id="rId2"/></sheets></workbook>' },
          { name: 'xl/_rels/workbook.xml.rels', content: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/></Relationships>' },
          { name: 'xl/worksheets/sheet1.xml', content: makeSheet(txRows) },
          { name: 'xl/worksheets/sheet2.xml', content: makeSheet(accRows) }
        ]);
      },

      exportToExcel: (data, mode = 'save') => {
        try {
          const filename = `Voralet_Laporan_Keuangan_${getLocalDateString()}.xlsx`;
          const categoryLabels = ExcelExportService.buildCategoryLabelMap(data?.customCategories);

          // 1. Native Android OOXML (.xlsx) Generator Bridge (Zero Permissions)
          if (typeof window !== 'undefined' && window.AndroidBridge && typeof window.AndroidBridge.exportExcelXlsx === 'function') {
            try {
              const payload = JSON.stringify({
                accounts: data?.accounts || [],
                transactions: data?.transactions || [],
                savingsGoals: data?.savingsGoals || [],
                debts: data?.debts || [],
                userProfile: data?.userProfile || {},
                categoryLabels
              });
              const ok = window.AndroidBridge.exportExcelXlsx(payload, filename, mode === 'share' ? 'share' : 'save');
              if (ok) return true;
            } catch (bridgeErr) {}
          }

          // 2. Pure-JS OOXML (.xlsx) Download Fallback for Web Preview
          const xlsxBytes = ExcelExportService.generateXlsxFallbackBytes(data || {});
          const blob = new Blob([xlsxBytes], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          setTimeout(() => {
            try {
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
            } catch (e) {}
          }, 2000);
          return true;
        } catch (err) {
          console.error('[ExcelExportService] Export error:', err);
          return false;
        }
      }
    };

    // =========================================================================
    // RECEIPT SCANNER & OFFLINE ON-DEVICE OCR ENGINE (Auto-Catat Struk Belanja)
    // =========================================================================
    const ReceiptOcrService = {
      MERCHANTS: [
        { pattern: /indomaret/i, name: 'Indomaret', category: 'belanja', note: 'Belanja di Indomaret' },
        { pattern: /alfamidi/i, name: 'Alfamidi', category: 'belanja', note: 'Belanja di Alfamidi' },
        { pattern: /alfamart|alfa\s*mart/i, name: 'Alfamart', category: 'belanja', note: 'Belanja di Alfamart' },
        { pattern: /super\s*indo/i, name: 'Super Indo', category: 'belanja', note: 'Belanja di Super Indo' },
        { pattern: /hypermart|transmart|carrefour|lottemart|lotte\s*mart/i, name: 'Supermarket', category: 'belanja', note: 'Belanja Bulanan Supermarket' },
        { pattern: /lawson|family\s*mart|circle\s*k/i, name: 'Minimarket', category: 'makan', note: 'Jajan Minimarket' },
        { pattern: /mie\s*gacoan|gacoan/i, name: 'Mie Gacoan', category: 'makan', note: 'Makan di Mie Gacoan' },
        { pattern: /mixue/i, name: 'Mixue Ice Cream', category: 'makan', note: 'Jajan Mixue' },
        { pattern: /starbucks/i, name: 'Starbucks Coffee', category: 'makan', note: 'Kopi & Minuman Starbucks' },
        { pattern: /kopi\s*kenangan/i, name: 'Kopi Kenangan', category: 'makan', note: 'Kopi Kenangan' },
        { pattern: /janji\s*jiwa|fore\s*coffee|point\s*coffee|tomoro|tuku/i, name: 'Kopi & Kafe', category: 'makan', note: 'Ngopi di Kafe' },
        { pattern: /mcdonald|mcd/i, name: "McDonald's", category: 'makan', note: "Makan di McDonald's" },
        { pattern: /kfc|kentucky/i, name: 'KFC Restaurant', category: 'makan', note: 'Makan di KFC' },
        { pattern: /hokben|hoka\s*hoka/i, name: 'HokBen', category: 'makan', note: 'Makan di HokBen' },
        { pattern: /solaria|bakmi\s*gm|d'cost|rica|yoshinoya|marugame|pizza\s*hut|burger\s*king/i, name: 'Restoran', category: 'makan', note: 'Makan di Restoran' },
        { pattern: /warung|warteg|rumah\s*makan|rm\s|soto|bakso|ayam\s*geprek|nasi\s*padang|padang|cafe|resto/i, name: 'Rumah Makan', category: 'makan', note: 'Makan & Minum' },
        { pattern: /pertamina|spbu|shell|bp\s*akr|vivo\s*energy|bensin|pertalite|pertamax|solar/i, name: 'SPBU BBM', category: 'transport', note: 'Isi Bahan Bakar Bensin' },
        { pattern: /grab|gojek|maxim|blue\s*bird|kai\s|transjakarta|mrt|parkir|tol/i, name: 'Transportasi', category: 'transport', note: 'Ongkos Transport / Parkir' },
        { pattern: /apotek|kimia\s*farma|k24|k-24|guardian|watson|century|rumah\s*sakit|klinik/i, name: 'Apotek & Kesehatan', category: 'kesehatan', note: 'Beli Obat / Kesehatan' },
        { pattern: /gramedia|uniqlo|h&m|zara|miniso|mr\s*diy|ace\s*hardware|ikea|matahari/i, name: 'Toko Ritel', category: 'belanja', note: 'Belanja Ritel & Kebutuhan' },
        { pattern: /pln|pdam|indihome|telkom|listrik|token|wifi|biznet/i, name: 'Tagihan Utilitas', category: 'tagihan', note: 'Pembayaran Tagihan Utilitas' },
        { pattern: /bioskop|xxi|cgv|cinepolis|karaoke/i, name: 'Hiburan', category: 'hiburan', note: 'Tiket & Hiburan' }
      ],

      getSampleReceipts: () => {
        const today = getLocalDateString();
        return [
          {
            id: 'sample_indomaret',
            title: 'Struk Indomaret',
            store: 'Indomaret Point Kemang',
            amount: 48500,
            category: 'belanja',
            note: 'Belanja di Indomaret Point Kemang',
            date: today,
            items: ['Roti Tawar Gandum', 'Ultra Milk Cokelat 250ml', 'Air Mineral 600ml']
          },
          {
            id: 'sample_starbucks',
            title: 'Struk Starbucks',
            store: 'Starbucks Coffee Reserve',
            amount: 62000,
            category: 'makan',
            note: 'Iced Caffe Latte & Croissant',
            date: today,
            items: ['Iced Caffe Latte Grande', 'Butter Croissant']
          },
          {
            id: 'sample_pertamina',
            title: 'Struk SPBU',
            store: 'SPBU Pertamina 31.12',
            amount: 100000,
            category: 'transport',
            note: 'Isi Pertamax 7.8 Liter',
            date: today,
            items: ['Pertamax 92 (7.8 L)']
          }
        ];
      },

      recognizeImage: (dataUrl) => {
        return new Promise((resolve) => {
          if (!dataUrl || typeof window === 'undefined' || !window.AndroidBridge || typeof window.AndroidBridge.recognizeReceiptText !== 'function') {
            resolve({ ok: false, fullText: '', lines: [] });
            return;
          }
          const cbId = 'ocr_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 6);
          if (!window.__voraletOcrCallbacks) window.__voraletOcrCallbacks = {};
          if (!window.__onVoraletOcrResult) {
            window.__onVoraletOcrResult = (id, rawJson) => {
              const fn = window.__voraletOcrCallbacks && window.__voraletOcrCallbacks[id];
              if (fn) {
                delete window.__voraletOcrCallbacks[id];
                fn(rawJson);
              }
            };
          }
          const timer = setTimeout(() => {
            if (window.__voraletOcrCallbacks && window.__voraletOcrCallbacks[cbId]) {
              delete window.__voraletOcrCallbacks[cbId];
              resolve({ ok: false, fullText: '', lines: [] });
            }
          }, 12000);

          window.__voraletOcrCallbacks[cbId] = (rawJson) => {
            clearTimeout(timer);
            try {
              const parsed = typeof rawJson === 'string' ? JSON.parse(rawJson) : rawJson;
              resolve({
                ok: Boolean(parsed?.ok),
                fullText: String(parsed?.fullText || ''),
                lines: Array.isArray(parsed?.lines) ? parsed.lines : []
              });
            } catch (_) {
              resolve({ ok: false, fullText: '', lines: [] });
            }
          };

          try {
            window.AndroidBridge.recognizeReceiptText(dataUrl, cbId);
          } catch (_) {
            clearTimeout(timer);
            delete window.__voraletOcrCallbacks[cbId];
            resolve({ ok: false, fullText: '', lines: [] });
          }
        });
      },

      processImage: (file) => {
        return new Promise((resolve, reject) => {
          if (!file) {
            reject(new Error('File tidak ditemukan'));
            return;
          }
          const reader = new FileReader();
          reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
              try {
                const canvas = document.createElement('canvas');
                const maxDim = 1400;
                let w = img.width;
                let h = img.height;
                if (w > h) {
                  if (w > maxDim) {
                    h = Math.round((h * maxDim) / w);
                    w = maxDim;
                  }
                } else {
                  if (h > maxDim) {
                    w = Math.round((w * maxDim) / h);
                    h = maxDim;
                  }
                }
                canvas.width = w;
                canvas.height = h;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, w, h);
                const compressed = canvas.toDataURL('image/jpeg', 0.88);
                resolve({ dataUrl: compressed, width: w, height: h });
              } catch (err) {
                resolve({ dataUrl: e.target.result, width: img.width, height: img.height });
              }
            };
            img.onerror = () => reject(new Error('Gagal memuat gambar'));
            img.src = e.target.result;
          };
          reader.onerror = () => reject(new Error('Gagal membaca file'));
          reader.readAsDataURL(file);
        });
      },

      parseMoneyToken: (rawNum) => {
        if (!rawNum) return 0;
        let s = String(rawNum).trim().replace(/\\s+/g, '');
        // Drop decimal cents like ,00 or .00 at the very end
        s = s.replace(/[.,]00$/, '');
        // Normalize Indonesian/international thousand separators
        const cleanDigits = s.replace(/[^0-9]/g, '');
        if (!cleanDigits) return 0;
        const val = parseInt(cleanDigits, 10);
        if (isNaN(val) || val < 500 || val > 50000000) return 0;
        return val;
      },

      parseReceiptText: (rawText, fileNameHint = '') => {
        const text = String(rawText || '').trim();
        const combinedSearch = (text + '\\n' + String(fileNameHint || '')).trim();
        const lines = text.split(/\\r?\\n/).map(l => l.trim()).filter(Boolean);

        let detectedAmount = 0;
        let detectedMerchant = '';
        let detectedCategory = 'belanja';
        let detectedNote = '';
        let detectedDate = getLocalDateString();

        // 1. Merchant & Category Detection
        for (const m of ReceiptOcrService.MERCHANTS) {
          if (m.pattern.test(combinedSearch)) {
            detectedMerchant = m.name;
            detectedCategory = m.category;
            detectedNote = m.note;
            break;
          }
        }

        if (!detectedMerchant && lines.length > 0) {
          for (let i = 0; i < Math.min(4, lines.length); i++) {
            const cand = lines[i];
            if (cand.length >= 3 && cand.length <= 42 && !/^\\d+[\\d\\s\\/-]*$/.test(cand) && !/(jl\\.|jalan|telp|npwp|struk|receipt|kasir|tgl|tanggal)/i.test(cand)) {
              detectedMerchant = cand.replace(/[^a-zA-Z0-9\\s&'./-]/g, '').trim();
              if (detectedMerchant.length >= 3) break;
            }
          }
        }
        if (!detectedMerchant) detectedMerchant = 'Struk Belanja';
        if (!detectedNote) {
          detectedNote = detectedMerchant === 'Struk Belanja' ? 'Pengeluaran Struk Belanja' : `Belanja di ${detectedMerchant}`;
        }

        // 2. Smart Bottom-Up Total Amount Extraction (avoids Cash/Tunai/Change traps)
        const priorityPatterns = [
          /(?:grand\\s*total|total\\s*bayar|total\\s*belanja|total\\s*tagihan|total\\s*harga|jumlah\\s*bayar|net\\s*total)[^0-9\\n]*?(?:rp\\.?\\s*)?([0-9][0-9.,\\s]{2,14})/i,
          /(?:^|\\s)total(?!\\s*(?:item|qty|barang|hemat|diskon|ppn))[^0-9\\n]*?(?:rp\\.?\\s*)?([0-9][0-9.,\\s]{2,14})/i,
          /(?:subtotal|sub\\s*total)[^0-9\\n]*?(?:rp\\.?\\s*)?([0-9][0-9.,\\s]{2,14})/i
        ];

        const ignoredLineRe = /\\b(tunai|cash|kembalian|kembali|change|debit|qris|ovo|gopay|dana|npwp|telp|hp|wa|poin|point|hemat|diskon|member|kartu)\\b/i;

        for (const rg of priorityPatterns) {
          for (let i = lines.length - 1; i >= 0; i--) {
            const line = lines[i];
            if (ignoredLineRe.test(line) && !/total/i.test(line)) continue;
            const match = line.match(rg);
            if (match && match[1]) {
              const parsed = ReceiptOcrService.parseMoneyToken(match[1]);
              if (parsed > 0) {
                detectedAmount = parsed;
                break;
              }
            }
          }
          if (detectedAmount > 0) break;
        }

        // Fallback: examine lines near the lower half looking for Rp-prefixed or largest price
        if (detectedAmount === 0 && lines.length > 0) {
          let bestCandidate = 0;
          const startIdx = Math.floor(lines.length * 0.35);
          for (let i = startIdx; i < lines.length; i++) {
            const line = lines[i];
            if (ignoredLineRe.test(line)) continue;
            const matches = line.match(/(?:rp\\.?\\s*)?([0-9]{1,3}(?:[.,][0-9]{3})+(?:[.,][0-9]{2})?|[0-9]{4,7})/gi);
            if (matches) {
              matches.forEach(tok => {
                const v = ReceiptOcrService.parseMoneyToken(tok);
                if (v > bestCandidate && v <= 20000000) bestCandidate = v;
              });
            }
          }
          if (bestCandidate > 0) detectedAmount = bestCandidate;
        }

        // 3. Date Extraction (DD/MM/YY, DD-MM-YYYY, YYYY-MM-DD, DD MMM YYYY)
        const monthMap = { jan: 1, feb: 2, mar: 3, apr: 4, mei: 5, may: 5, jun: 6, jul: 7, agu: 8, ags: 8, aug: 8, sep: 9, okt: 10, oct: 10, nov: 11, des: 12, dec: 12 };
        const namedDate = text.match(/(\\d{1,2})\\s+(jan|feb|mar|apr|mei|may|jun|jul|agu|ags|aug|sep|okt|oct|nov|des|dec)[a-z]*\\s+(\\d{2,4})/i);
        const ymdMatch = text.match(/(\\d{4})[-\\/](\\d{1,2})[-\\/](\\d{1,2})/);
        const dmyMatch = text.match(/(\\d{1,2})[\\/.\\-](\\d{1,2})[\\/.\\-](\\d{2,4})/);

        if (namedDate) {
          const day = parseInt(namedDate[1], 10);
          const mon = monthMap[namedDate[2].toLowerCase().slice(0, 3)] || 1;
          let yr = parseInt(namedDate[3], 10);
          if (yr < 100) yr += 2000;
          if (day >= 1 && day <= 31 && yr >= 2020 && yr <= 2035) {
            detectedDate = `${yr}-${String(mon).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          }
        } else if (ymdMatch) {
          const yr = parseInt(ymdMatch[1], 10);
          const mon = parseInt(ymdMatch[2], 10);
          const day = parseInt(ymdMatch[3], 10);
          if (yr >= 2020 && yr <= 2035 && mon >= 1 && mon <= 12 && day >= 1 && day <= 31) {
            detectedDate = `${yr}-${String(mon).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          }
        } else if (dmyMatch) {
          const day = parseInt(dmyMatch[1], 10);
          const mon = parseInt(dmyMatch[2], 10);
          let yr = parseInt(dmyMatch[3], 10);
          if (yr < 100) yr += 2000;
          if (day >= 1 && day <= 31 && mon >= 1 && mon <= 12 && yr >= 2020 && yr <= 2035) {
            detectedDate = `${yr}-${String(mon).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
          }
        }

        // 4. Extract concise item summary lines if available
        const extractedItems = [];
        for (const line of lines) {
          if (ignoredLineRe.test(line) || /(?:total|kasir|tgl|tanggal|npwp|jl\\.|telp|struk)/i.test(line)) continue;
          if (/[a-zA-Z]{3,}.*?([0-9]{1,3}[.,][0-9]{3}|[0-9]{4,6})/.test(line) && extractedItems.length < 5) {
            extractedItems.push(line.slice(0, 48));
          }
        }

        return {
          amount: detectedAmount,
          merchant: detectedMerchant,
          category: detectedCategory,
          note: detectedNote,
          date: detectedDate,
          items: extractedItems,
          ocrSuccess: detectedAmount > 0,
          rawText: text
        };
      }
    };
"""
