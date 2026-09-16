PART6_MODALS = """
    // =========================================================================
    // 6. CORE MODALS (TRANSACTION, ACCOUNTS, SAVINGS, SETTINGS)
    // =========================================================================
    const TransactionModal = ({ isOpen, onClose, initialData, accounts, onAddTransaction, customCategories = [], onSaveCustomCategory }) => {
      const [type, setType] = useState('EXPENSE');
      const [amountStr, setAmountStr] = useState('');
      const [accountId, setAccountId] = useState(accounts[0]?.id || '');
      const [category, setCategory] = useState('makan');
      const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
      const [notes, setNotes] = useState('');
      const [error, setError] = useState('');
      const [isClosing, setIsClosing] = useState(false);

      // Inline Custom Category Creation State
      const [showAddCategory, setShowAddCategory] = useState(false);
      const [newCatName, setNewCatName] = useState('');
      const [newCatEmoji, setNewCatEmoji] = useState('🏷️');
      const [newCatError, setNewCatError] = useState('');

      const emojiPresets = ['🍔', '☕', '🚗', '🛍️', '💡', '🎮', '💊', '💼', '🎁', '📈', '🏷️', '🏠', '✈️', '📚', '🐾', '⚽'];

      const allCategories = useMemo(() => {
        return getAllCategories(customCategories);
      }, [customCategories]);

      const filteredCategories = useMemo(() => {
        return allCategories.filter(c => c.type === 'ALL' || c.type === type);
      }, [allCategories, type]);

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          setShowAddCategory(false);
          setNewCatName('');
          onClose();
        }, 220);
      };

      useEffect(() => {
        if (initialData) {
          setType(initialData.type || 'EXPENSE');
          setAmountStr(initialData.amount ? String(initialData.amount) : '');
          setCategory(initialData.category || 'makan');
          setNotes(initialData.notes || '');
          if (initialData.accountId) setAccountId(initialData.accountId);
        } else {
          setType('EXPENSE');
          setAmountStr('');
          setCategory('makan');
          setNotes('');
        }
        if (accounts.length > 0 && !accounts.some(a => a.id === accountId)) {
          setAccountId(accounts[0].id);
        }
      }, [initialData, accounts, isOpen]);

      if (!isOpen) return null;

      const handleQuickAdd = (value) => {
        const current = parseRawNumber(amountStr);
        setAmountStr((current + value).toString());
      };

      const handleCreateCategory = (e) => {
        e.preventDefault();
        const trimmed = newCatName.trim();
        if (!trimmed) {
          setNewCatError('Nama kategori wajib diisi');
          return;
        }
        const newCatId = 'custom_' + Date.now().toString(36);
        const newCat = {
          id: newCatId,
          label: Validators.sanitizeText(trimmed, 40),
          icon: newCatEmoji || '🏷️',
          type: type,
          isCustom: true
        };
        if (typeof onSaveCustomCategory === 'function') {
          onSaveCustomCategory(newCat);
        }
        setCategory(newCatId);
        setNewCatName('');
        setShowAddCategory(false);
        setNewCatError('');
      };

      const handleSubmit = (e) => {
        e.preventDefault();
        const rawAmount = parseRawNumber(amountStr);
        if (rawAmount <= 0) {
          setError('Nominal harus lebih dari 0');
          return;
        }
        if (!accountId) {
          setError('Pilih dompet terlebih dahulu');
          return;
        }

        const newTx = {
          id: 'tx_' + Date.now(),
          accountId,
          type,
          amount: rawAmount,
          category,
          date,
          notes: notes.trim(),
          createdAt: new Date().toISOString()
        };

        HapticFeedback.save();
        onAddTransaction(newTx);
        handleClose();
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-slate-800 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'}`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="ios-modal-header px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-white dark:bg-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Catat Transaksi</h2>
              <button
                type="button"
                onClick={handleClose}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                aria-label="Tutup"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="ios-modal-body flex-1 overflow-y-auto pb-28 p-4 sm:p-5 space-y-4 no-scrollbar">
              <SegmentedControl
                options={[
                  { value: 'EXPENSE', label: 'Pengeluaran', icon: 'arrow-up-right', iconColor: 'text-rose-500' },
                  { value: 'INCOME', label: 'Pemasukan', icon: 'arrow-down-left', iconColor: 'text-emerald-500' }
                ]}
                value={type}
                onChange={(newType) => {
                  setType(newType);
                  const newCats = allCategories.filter(c => c.type === 'ALL' || c.type === newType);
                  if (!newCats.some(c => c.id === category)) {
                    setCategory(newCats[0]?.id || 'makan');
                  }
                }}
                className="w-full shadow-sm"
              />

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nominal (Rp)</label>
                <input
                  type="text"
                  inputMode="numeric"
                  required
                  value={amountStr ? formatIDR(parseRawNumber(amountStr)) : ''}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => {
                    const num = parseRawNumber(e.target.value);
                    setAmountStr(num ? num.toString() : '');
                    setError('');
                  }}
                  placeholder="0"
                  className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-lg font-bold text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                />
                {error && <p className="text-xs text-rose-500 mt-1">{error}</p>}

                <div className="flex flex-wrap gap-1.5 mt-2">
                  {[20000, 50000, 100000, 250000, 500000].map(val => (
                    <button
                      key={val}
                      type="button"
                      onClick={() => handleQuickAdd(val)}
                      className="px-2.5 py-1 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 text-slate-700 dark:text-slate-300 rounded-lg text-[11px] font-medium ios-btn-tap"
                    >
                      +{val >= 1000 ? `${val / 1000}rb` : val}
                    </button>
                  ))}
                  {amountStr && (
                    <button
                      type="button"
                      onClick={() => setAmountStr('')}
                      className="px-2.5 py-1 bg-rose-50 dark:bg-rose-950/40 text-rose-600 rounded-lg text-[11px] font-medium ml-auto ios-btn-tap"
                    >
                      Reset
                    </button>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Dompet / Rekening</label>
                {accounts.length === 0 ? (
                  <p className="text-xs text-amber-600 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
                    Belum ada dompet. Tambahkan di menu Kelola Dompet.
                  </p>
                ) : (
                  <select
                    value={accountId}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => setAccountId(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                  >
                    {accounts.map(acc => (
                      <option key={acc.id} value={acc.id}>
                        {acc.name} ({acc.type})
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Kategori</label>
                  <button
                    type="button"
                    onClick={() => setShowAddCategory(!showAddCategory)}
                    className="text-[11px] font-semibold text-brand dark:text-sky-400 hover:underline flex items-center gap-1 ios-btn-tap"
                  >
                    <Icon name="plus" className="w-3 h-3" />
                    <span>{showAddCategory ? 'Batal Tambah' : '+ Kategori Baru'}</span>
                  </button>
                </div>

                {/* Inline Category Creator */}
                {showAddCategory && (
                  <div className="p-3 mb-2.5 bg-sky-50/60 dark:bg-slate-900 border border-sky-200 dark:border-slate-700 rounded-xl space-y-2.5 animate-ios-sheet">
                    <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 block">
                      Tambah Kategori Kustom
                    </span>
                    <div className="space-y-1">
                      <label className="text-[10px] font-medium text-slate-500">Pilih Emoji:</label>
                      <div className="flex flex-wrap gap-1.5 p-1.5 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 max-h-24 overflow-y-auto">
                        {emojiPresets.map(emoji => (
                          <button
                            key={emoji}
                            type="button"
                            onClick={() => setNewCatEmoji(emoji)}
                            className={`w-7 h-7 flex items-center justify-center rounded text-sm transition-all ios-btn-tap ${
                              newCatEmoji === emoji ? 'bg-sky-100 dark:bg-slate-700 scale-110 shadow-sm' : 'hover:bg-slate-100'
                            }`}
                          >
                            {emoji}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] font-medium text-slate-500 block mb-0.5">Nama Kategori:</label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          maxLength={30}
                          value={newCatName}
                          onChange={(e) => {
                            setNewCatName(e.target.value);
                            setNewCatError('');
                          }}
                          placeholder="cth: Kucing, Skincare, Pajak"
                          className="flex-1 px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                        />
                        <button
                          type="button"
                          onClick={handleCreateCategory}
                          className="px-3 py-1.5 bg-brand text-white rounded-lg text-xs font-semibold hover:bg-brand-hover ios-btn-tap flex items-center gap-1"
                        >
                          <Icon name="check" className="w-3.5 h-3.5" />
                          <span>Simpan</span>
                        </button>
                      </div>
                      {newCatError && <p className="text-[10px] text-rose-500 mt-1">{newCatError}</p>}
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-3 gap-2">
                  {filteredCategories.map(cat => {
                    const isEmoji = cat.icon && cat.icon.length <= 4 && !/^[a-z0-9-]+$/.test(cat.icon);
                    return (
                      <button
                        key={cat.id}
                        type="button"
                        onClick={() => setCategory(cat.id)}
                        className={`p-2 rounded-xl border text-center flex flex-col items-center gap-1 transition-all ios-btn-tap ${
                          category === cat.id
                            ? 'border-brand bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400 font-bold'
                            : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400'
                        }`}
                      >
                        {isEmoji ? (
                          <span className="text-lg leading-none">{cat.icon}</span>
                        ) : (
                          <Icon name={cat.icon} className="w-5 h-5" />
                        )}
                        <span className="text-[11px] leading-tight line-clamp-1">{cat.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Tanggal</label>
                  <input
                    type="date"
                    value={date}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Catatan</label>
                  <input
                    type="text"
                    maxLength={60}
                    value={notes}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Contoh: Makan siang"
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={accounts.length === 0}
                  className={`w-full py-3 text-white font-semibold text-sm rounded-xl transition-colors shadow-sm ios-btn-tap ${
                    type === 'EXPENSE' ? 'bg-rose-600 hover:bg-rose-700' : 'bg-emerald-600 hover:bg-emerald-700'
                  }`}
                >
                  Simpan {type === 'EXPENSE' ? 'Pengeluaran' : 'Pemasukan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    // =========================================================================
    // 3. APPLE WALLET / APPLE PAY STYLE "KELOLA KANTONG" & ACCOUNTS MANAGER
    // =========================================================================

    const POCKET_THEMES = {
      bca: {
        id: 'bca',
        label: 'BCA Blue',
        network: 'Mastercard',
        networkType: 'mastercard',
        gradient: 'from-[#002b66] via-[#0047BA] to-[#001D47]',
        cardPattern: 'radial-gradient(circle at 85% 15%, rgba(255,255,255,0.18) 0%, transparent 60%)',
        textColor: 'text-white',
        subtextColor: 'text-blue-200/90',
        chipColor: 'bg-amber-300/90 border-amber-400 shadow-amber-500/30',
        accentBorder: 'border-blue-400/40',
        badgeBg: 'bg-blue-400/25 border-blue-300/40',
        badgeText: 'text-blue-100',
        swatch: 'bg-blue-600'
      },
      gopay: {
        id: 'gopay',
        label: 'GoPay Cyan',
        network: 'GPN / E-Money',
        networkType: 'gpn',
        gradient: 'from-[#00607A] via-[#008DA5] to-[#003B46]',
        cardPattern: 'radial-gradient(circle at 80% 20%, rgba(255,255,255,0.2) 0%, transparent 55%)',
        textColor: 'text-white',
        subtextColor: 'text-cyan-200/90',
        chipColor: 'bg-emerald-300/90 border-emerald-400 shadow-emerald-500/30',
        accentBorder: 'border-cyan-300/40',
        badgeBg: 'bg-cyan-400/25 border-cyan-300/40',
        badgeText: 'text-cyan-100',
        swatch: 'bg-cyan-500'
      },
      dana: {
        id: 'dana',
        label: 'DANA Blue',
        network: 'Visa Debit',
        networkType: 'visa',
        gradient: 'from-[#0A5A9C] via-[#118EEA] to-[#073D6B]',
        cardPattern: 'radial-gradient(circle at 85% 15%, rgba(255,255,255,0.22) 0%, transparent 60%)',
        textColor: 'text-white',
        subtextColor: 'text-sky-200/90',
        chipColor: 'bg-amber-300/90 border-amber-400 shadow-amber-500/30',
        accentBorder: 'border-sky-300/40',
        badgeBg: 'bg-white/20 border-white/35',
        badgeText: 'text-white',
        swatch: 'bg-sky-500'
      },
      mandiri: {
        id: 'mandiri',
        label: 'Mandiri Gold',
        network: 'Visa Platinum',
        networkType: 'visa',
        gradient: 'from-[#0A2540] via-[#003B73] to-[#001737]',
        cardPattern: 'radial-gradient(circle at 90% 10%, rgba(245,158,11,0.25) 0%, transparent 55%)',
        textColor: 'text-white',
        subtextColor: 'text-amber-200/90',
        chipColor: 'bg-amber-400 border-amber-500 shadow-amber-500/40',
        accentBorder: 'border-amber-400/40',
        badgeBg: 'bg-amber-400/25 border-amber-300/40',
        badgeText: 'text-amber-200',
        swatch: 'bg-blue-900'
      },
      bri: {
        id: 'bri',
        label: 'BRI BritAma',
        network: 'Mastercard Debit',
        networkType: 'mastercard',
        gradient: 'from-[#052957] via-[#08479A] to-[#031B3B]',
        cardPattern: 'radial-gradient(circle at 80% 20%, rgba(255,255,255,0.18) 0%, transparent 60%)',
        textColor: 'text-white',
        subtextColor: 'text-blue-200/90',
        chipColor: 'bg-amber-300/90 border-amber-400 shadow-amber-500/30',
        accentBorder: 'border-blue-300/40',
        badgeBg: 'bg-blue-400/25 border-blue-300/40',
        badgeText: 'text-blue-100',
        swatch: 'bg-blue-700'
      },
      jago: {
        id: 'jago',
        label: 'Jago Violet',
        network: 'Visa Platinum',
        networkType: 'visa',
        gradient: 'from-[#312E81] via-[#4F46E5] to-[#1E1B4B]',
        cardPattern: 'radial-gradient(circle at 85% 15%, rgba(199,210,254,0.25) 0%, transparent 55%)',
        textColor: 'text-white',
        subtextColor: 'text-indigo-200/90',
        chipColor: 'bg-amber-300/90 border-amber-400 shadow-amber-500/30',
        accentBorder: 'border-indigo-300/40',
        badgeBg: 'bg-indigo-400/25 border-indigo-300/40',
        badgeText: 'text-indigo-100',
        swatch: 'bg-indigo-600'
      },
      shopee: {
        id: 'shopee',
        label: 'ShopeePay',
        network: 'GPN Debit',
        networkType: 'gpn',
        gradient: 'from-[#B82B14] via-[#EE4D2D] to-[#8C1808]',
        cardPattern: 'radial-gradient(circle at 80% 20%, rgba(255,255,255,0.22) 0%, transparent 60%)',
        textColor: 'text-white',
        subtextColor: 'text-orange-200/90',
        chipColor: 'bg-amber-300/90 border-amber-400 shadow-amber-500/30',
        accentBorder: 'border-orange-300/40',
        badgeBg: 'bg-white/25 border-white/35',
        badgeText: 'text-white',
        swatch: 'bg-orange-500'
      },
      ovo: {
        id: 'ovo',
        label: 'OVO Premier',
        network: 'Mastercard Debit',
        networkType: 'mastercard',
        gradient: 'from-[#321C61] via-[#522785] to-[#1E0F3B]',
        cardPattern: 'radial-gradient(circle at 85% 15%, rgba(216,180,254,0.22) 0%, transparent 60%)',
        textColor: 'text-white',
        subtextColor: 'text-purple-200/90',
        chipColor: 'bg-amber-300/90 border-amber-400 shadow-amber-500/30',
        accentBorder: 'border-purple-300/40',
        badgeBg: 'bg-purple-400/25 border-purple-300/40',
        badgeText: 'text-purple-100',
        swatch: 'bg-purple-600'
      },
      cash: {
        id: 'cash',
        label: 'Dompet Fisik (Cash)',
        network: 'Cash / Tunai',
        networkType: 'cash',
        gradient: 'from-[#1E293B] via-[#0F172A] to-[#020617]',
        cardPattern: 'radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 55%)',
        textColor: 'text-slate-100',
        subtextColor: 'text-slate-400',
        chipColor: 'bg-amber-200/80 border-amber-300/80 shadow-amber-500/20',
        accentBorder: 'border-slate-600/50',
        badgeBg: 'bg-slate-700/50 border-slate-600/50',
        badgeText: 'text-slate-200',
        swatch: 'bg-slate-800'
      },
    };

    const getPocketTheme = (acc) => {
      if (!acc) return POCKET_THEMES.bca;
      if (acc.theme && POCKET_THEMES[acc.theme]) {
        return POCKET_THEMES[acc.theme];
      }
      const n = (acc.name || '').toLowerCase();
      if (n.includes('bca')) return POCKET_THEMES.bca;
      if (n.includes('gopay') || n.includes('go-pay')) return POCKET_THEMES.gopay;
      if (n.includes('dana')) return POCKET_THEMES.dana;
      if (n.includes('mandiri')) return POCKET_THEMES.mandiri;
      if (n.includes('bri')) return POCKET_THEMES.bri;
      if (n.includes('jago') || n.includes('tabungan') || n.includes('savings')) return POCKET_THEMES.jago;
      if (n.includes('shopee') || n.includes('spay')) return POCKET_THEMES.shopee;
      if (n.includes('ovo')) return POCKET_THEMES.ovo;
      if (acc.type === 'Cash' || n.includes('tunai') || n.includes('cash') || n.includes('dompet')) return POCKET_THEMES.cash;
      if (acc.type === 'E-Wallet') return POCKET_THEMES.gopay;
      return POCKET_THEMES.bca;
    };

    // Apple Wallet Dynamic Clean Pocket Card (No chip, no card brand logo, dynamic collapsed/expanded)
    const AppleWalletCard = ({
      acc,
      index,
      totalCards,
      isSelected,
      hideBalance,
      balance,
      onSelect,
      onEdit,
      onDelete,
      onAddTx
    }) => {
      const isPrimary = index === 0;

      // Card Icon based on Type
      const renderCardIcon = () => {
        if (acc.type === 'Bank' || acc.type === 'BANK') return <Icon name="bank" className="w-4 h-4 text-[#0284C7] dark:text-[#38BDF8]" />;
        if (acc.type === 'E-Wallet' || acc.type === 'EWALLET') return <Icon name="smartphone" className="w-4 h-4 text-[#0284C7] dark:text-[#38BDF8]" />;
        return <Icon name="cash" className="w-4 h-4 text-[#0284C7] dark:text-[#38BDF8]" />;
      };

      const typeLabel = (acc.type === 'Bank' || acc.type === 'BANK') ? 'Rekening Bank' : (acc.type === 'E-Wallet' || acc.type === 'EWALLET') ? 'E-Wallet' : 'Kas Tunai';

      const maskedNumber = (acc.accountNumber && String(acc.accountNumber).trim())
        ? `•••• ${String(acc.accountNumber).replace(/\s/g, '').slice(-4)}`
        : `•••• ${String(acc.id || '8829').replace(/\D/g, '').slice(-4) || '8829'}`;

      return (
        <div
          onClick={onSelect}
          className="w-full relative select-none mb-3"
        >
          {/* Main Flat Card Container - Solid Blue (#0284C7), No Gradient */}
          <div
            className={`w-full rounded-2xl bg-[#0284C7] dark:bg-[#0369A1] text-white border ${
              isSelected ? 'border-sky-300 ring-2 ring-sky-400/50 shadow-md' : 'border-transparent shadow-xs'
            } transition-all duration-300 ease-out cursor-pointer p-4 ios-card-tap`}
          >
            {/* TOP BAR / ALWAYS VISIBLE HEADER */}
            <div className="relative z-10 flex items-center justify-between gap-3 mb-3">
              <div className="flex items-center gap-2.5 min-w-0 pr-1">
                <div className="w-8 h-8 rounded-xl bg-white/20 border border-white/25 flex items-center justify-center shrink-0 text-white">
                  {renderCardIcon()}
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="font-extrabold text-xs sm:text-sm text-white truncate">
                      {acc.name}
                    </span>
                    {isPrimary && (
                      <span className="px-1.5 py-0.2 rounded-md text-[9px] font-bold uppercase bg-white/25 text-white border border-white/30">
                        Utama
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-sky-100 block">
                    {typeLabel}
                  </span>
                </div>
              </div>

              {/* Masked Card Number */}
              <div className="px-2 py-0.5 rounded-md bg-white/15 border border-white/20 text-[9px] font-mono font-bold text-sky-100 shrink-0">
                {maskedNumber}
              </div>
            </div>

            {/* Bottom Row: Saldo */}
            <div className="relative z-10 pt-2 border-t border-white/15 flex items-end justify-between">
              <div>
                <span className="text-[9px] font-medium uppercase tracking-wider text-sky-200 block mb-0.5">Saldo</span>
                <div className="font-black text-sm sm:text-base text-white">
                  {hideBalance ? 'Rp ••••••••' : formatIDR(balance)}
                </div>
              </div>
              <span className="text-[10px] text-sky-100 font-semibold bg-white/15 px-2 py-0.5 rounded-lg">
                {isSelected ? 'Terpilih' : 'Ketuk opsi'}
              </span>
            </div>

            {/* EXPANDED CONTENT: Revealed smoothly when clicked */}
            {isSelected && (
              <div className="relative z-10 mt-3 pt-3 border-t border-white/20 flex items-center justify-between animate-ios-spring-pop text-xs text-sky-100">
                <div className="flex items-center gap-1.5">
                  <Icon name="check-circle" className="w-3.5 h-3.5 text-white" strokeWidth={2.2} />
                  <span className="text-[11px] font-bold">Kantong Terpilih</span>
                </div>
                <span className="text-[10px] font-mono text-sky-200">ID: {acc.id}</span>
              </div>
            )}
          </div>

          {/* EXPANDED ACTION DOCK (Catat Mutasi, Edit Kartu, Hapus) */}
          {isSelected && (
            <div className="mt-3 p-3 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-slate-700 shadow-lg animate-ios-spring-pop">
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onAddTx) onAddTx(acc.id);
                  }}
                  className="py-2.5 px-2 rounded-xl bg-sky-50 dark:bg-slate-700 hover:bg-sky-100 dark:hover:bg-slate-600 text-brand dark:text-sky-300 font-bold text-xs flex flex-col items-center justify-center gap-1 border border-sky-200/60 dark:border-slate-600 transition-colors ios-btn-tap"
                >
                  <Icon name="arrow-up-right" className="w-4 h-4" strokeWidth={2.5} />
                  <span className="text-[11px]">Catat Mutasi</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onEdit) onEdit(acc);
                  }}
                  className="py-2.5 px-2 rounded-xl bg-slate-100 dark:bg-slate-700/60 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold text-xs flex flex-col items-center justify-center gap-1 border border-slate-200 dark:border-slate-600 transition-colors ios-btn-tap"
                >
                  <Icon name="edit" className="w-4 h-4" strokeWidth={2.2} />
                  <span className="text-[11px]">Edit Kantong</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onDelete) onDelete(acc.id);
                  }}
                  className="py-2.5 px-2 rounded-xl bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-900/50 text-rose-600 dark:text-rose-300 font-bold text-xs flex flex-col items-center justify-center gap-1 border border-rose-200 dark:border-rose-900/60 transition-colors ios-btn-tap"
                >
                  <Icon name="trash" className="w-4 h-4 text-rose-500" strokeWidth={2.2} />
                  <span className="text-[11px]">Hapus</span>
                </button>
              </div>
            </div>
          )}
        </div>
      );
    };

    // Full Apple Wallet Accounts Manager Modal
    const AccountsManagerModal = ({
      isOpen,
      onClose,
      accounts,
      transactions,
      onAddAccount,
      onDeleteAccount,
      onEditAccount,
      hideBalance = false,
      onToggleHideBalance,
      onOpenAddTx
    }) => {
      const [isAdding, setIsAdding] = useState(false);
      const [selectedId, setSelectedId] = useState(null);
      const [name, setName] = useState('');
      const [type, setType] = useState('Bank');
      const [accountNumber, setAccountNumber] = useState('');
      const [selectedTheme, setSelectedTheme] = useState('bca');
      const [initialBalance, setInitialBalance] = useState('');
      const [editingAcc, setEditingAcc] = useState(null);
      const [isClosing, setIsClosing] = useState(false);
      const [localHideBalance, setLocalHideBalance] = useState(hideBalance);

      const safeAccounts = Array.isArray(accounts) ? accounts.filter(Boolean) : [];
      const safeTransactions = Array.isArray(transactions) ? transactions.filter(Boolean) : [];

      useEffect(() => {
        setLocalHideBalance(hideBalance);
      }, [hideBalance]);

      useEffect(() => {
        if (!isOpen) {
          setIsAdding(false);
          setEditingAcc(null);
          setSelectedId(null);
          setName('');
          setAccountNumber('');
          setSelectedTheme('bca');
          setInitialBalance('');
          setType('Bank');
        }
      }, [isOpen]);

      const totalBalance = useMemo(() => {
        return Ledger.getTotalBalance(safeAccounts, safeTransactions);
      }, [safeAccounts, safeTransactions]);

      if (!isOpen) return null;

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          onClose();
        }, 220);
      };

      const handleCardSelect = (accId) => {
        setSelectedId(prev => (prev === accId ? null : accId));
      };

      const handleStartAdd = () => {
        setEditingAcc(null);
        setName('');
        setAccountNumber('');
        setSelectedTheme('bca');
        setInitialBalance('');
        setType('Bank');
        setIsAdding(true);
      };

      const startEdit = (acc) => {
        setEditingAcc(acc);
        setName(acc.name || '');
        setType(acc.type || 'Bank');
        setAccountNumber(acc.accountNumber || '');
        setSelectedTheme(acc.theme || 'bca');
        setInitialBalance(acc.initialBalance ? String(acc.initialBalance) : '0');
        setIsAdding(true);
      };

      const handleSave = (e) => {
        e.preventDefault();
        const trimmed = (name || '').trim();
        if (!trimmed) return;
        const bal = parseRawNumber(initialBalance);
        const accNum = (accountNumber || '').trim();

        if (editingAcc && editingAcc.id) {
          onEditAccount(editingAcc.id, {
            name: trimmed,
            type,
            accountNumber: accNum,
            theme: selectedTheme,
            initialBalance: bal
          });
          setEditingAcc(null);
        } else {
          const newAcc = {
            id: 'acc_' + Date.now(),
            name: trimmed,
            type,
            accountNumber: accNum || ('•••• ' + Math.floor(1000 + Math.random() * 9000)),
            theme: selectedTheme,
            initialBalance: bal,
            createdAt: new Date().toISOString()
          };
          onAddAccount(newAcc);
          setSelectedId(newAcc.id);
        }

        HapticFeedback.save();
        setName('');
        setAccountNumber('');
        setSelectedTheme('bca');
        setInitialBalance('');
        setType('Bank');
        setIsAdding(false);
      };

      // Stack container dynamic height for smooth Apple Wallet layout
      const selectedIndex = safeAccounts.findIndex(a => a.id === selectedId);
      const isAnySelected = selectedIndex !== -1;
      const stackHeight = isAnySelected
        ? 290 + Math.max(0, safeAccounts.length - 1) * 60 + 50
        : Math.max(0, safeAccounts.length - 1) * 62 + 95;

      return (
        <div
          className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
          onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}
        >
          <div className={`ios-modal-card bg-white dark:bg-slate-900 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'} flex flex-col max-h-[92dvh]`}>
            <ModalDragHandle onDismiss={handleClose} />

            {/* Apple Wallet Header */}
            <div className="ios-modal-header px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-900 shrink-0">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-sky-100 dark:bg-slate-800 border border-sky-200/60 dark:border-slate-700 text-brand dark:text-sky-300 flex items-center justify-center shadow-sm">
                  <Icon name="layers" className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-slate-900 dark:text-white leading-tight">Kelola Kantong</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Dompet & Sumber Dana</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {selectedId && !isAdding && (
                  <button
                    type="button"
                    onClick={() => setSelectedId(null)}
                    className="px-2.5 py-1 text-xs font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors ios-btn-tap"
                  >
                    Lipat Kartu
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleClose}
                  className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors ios-btn-tap"
                  aria-label="Tutup"
                >
                  <Icon name="x" className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="ios-modal-body flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 no-scrollbar">
              {!isAdding ? (
                <>
                  {/* Total Balance Across All Pockets Summary Card (Solid No Gradient) */}
                  <div className="p-4 rounded-2xl bg-slate-900 text-white border border-slate-800 shadow-sm flex items-center justify-between">
                    <div>
                      <span className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                        <span>Total Saldo Seluruh Kantong</span>
                        <Icon name="sparkles" className="w-3.5 h-3.5 text-amber-400" />
                      </span>
                      <div className="text-xl sm:text-2xl font-extrabold tracking-tight text-white mt-1">
                        {localHideBalance ? 'Rp ••••••••' : formatIDR(totalBalance)}
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => {
                        if (onToggleHideBalance) onToggleHideBalance();
                        setLocalHideBalance(!localHideBalance);
                      }}
                      className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/15 transition-colors ios-btn-tap"
                      aria-label="Sensor Saldo"
                    >
                      <Icon name={localHideBalance ? 'eye-off' : 'eye'} className="w-4 h-4 text-white" />
                    </button>
                  </div>

                  {/* Add New Pocket Button (Sleek Dash-Border Style) */}
                  <button
                    type="button"
                    onClick={handleStartAdd}
                    className="w-full flex items-center justify-center gap-2 py-3.5 px-4 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand dark:hover:border-sky-400 bg-slate-50/70 dark:bg-slate-800/30 hover:bg-sky-50/50 dark:hover:bg-slate-800/60 text-slate-700 dark:text-slate-200 hover:text-brand dark:hover:text-sky-300 text-xs sm:text-sm font-bold transition-all group ios-btn-tap"
                  >
                    <div className="w-6 h-6 rounded-full bg-slate-200 dark:bg-slate-700 group-hover:bg-brand/20 dark:group-hover:bg-sky-400/20 flex items-center justify-center text-slate-500 group-hover:text-brand dark:group-hover:text-sky-300 transition-colors">
                      <Icon name="plus" className="w-4 h-4" strokeWidth={2.5} />
                    </div>
                    <span>+ Tambah Kantong Baru</span>
                  </button>

                  {/* Interactive Card Deck Section */}
                  <div className="pt-1">
                    <div className="flex items-center justify-between mb-3 px-1">
                      <span className="text-xs font-bold text-slate-500 dark:text-slate-400 tracking-wider uppercase">
                        Kartu Tersedia ({safeAccounts.length})
                      </span>
                      <span className="text-[11px] text-slate-400 dark:text-slate-500 flex items-center gap-1">
                        <span>{selectedId ? 'Ketuk kartu untuk melipat' : 'Ketuk kartu untuk membuka rincian'}</span>
                        <Icon name={selectedId ? 'chevron-up' : 'chevron-down'} className="w-3 h-3" />
                      </span>
                    </div>

                    {safeAccounts.length === 0 ? (
                      <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700">
                        <Icon name="wallet" className="w-10 h-10 text-slate-400 mx-auto mb-2" />
                        <p className="text-xs font-semibold text-slate-600 dark:text-slate-300">Belum ada kantong aktif</p>
                        <p className="text-[11px] text-slate-400 mt-1">Buat kantong baru untuk memisahkan rekening dan e-wallet kamu.</p>
                      </div>
                    ) : (
                      <div
                        style={{ minHeight: `${stackHeight}px` }}
                        className="relative w-full transition-all duration-300"
                      >
                        {safeAccounts.map((acc, idx) => {
                          const bal = Ledger.getAccountBalance(acc.id, safeAccounts, safeTransactions);
                          const isSelected = selectedId === acc.id;

                          // Non-selected cards positioning when a card is opened
                          let shiftY = idx * 62;
                          let shiftScale = 1 - (safeAccounts.length - 1 - idx) * 0.015;
                          let shiftOpacity = 1;
                          let shiftZ = 10 + idx;

                          if (selectedId) {
                            if (isSelected) {
                              shiftY = 0;
                              shiftScale = 1;
                              shiftZ = 60;
                            } else {
                              const posBelow = idx > selectedIndex ? idx - 1 : idx;
                              shiftY = 270 + posBelow * 58;
                              shiftScale = 0.96;
                              shiftOpacity = 0.88;
                            }
                          }

                          return (
                            <div
                              key={acc.id}
                              onClick={() => handleCardSelect(acc.id)}
                              style={{
                                transform: `translate3d(0, ${shiftY}px, 0) scale(${shiftScale})`,
                                zIndex: shiftZ,
                                opacity: shiftOpacity,
                                transition: 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.15), opacity 0.35s ease, box-shadow 0.35s ease',
                                transformOrigin: 'top center',
                              }}
                              className="absolute top-0 inset-x-0 cursor-pointer select-none"
                            >
                              <AppleWalletCard
                                acc={acc}
                                index={idx}
                                totalCards={safeAccounts.length}
                                isSelected={isSelected}
                                hideBalance={localHideBalance}
                                balance={bal}
                                onSelect={() => handleCardSelect(acc.id)}
                                onEdit={(targetAcc) => startEdit(targetAcc)}
                                onDelete={(targetId) => onDeleteAccount(targetId)}
                                onAddTx={(targetId) => {
                                  if (onOpenAddTx) onOpenAddTx(targetId);
                                }}
                              />
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </>
              ) : (
                /* Add / Edit Pocket Form with Card Theme Selector */
                <form onSubmit={handleSave} className="space-y-4 bg-slate-50 dark:bg-slate-900/90 p-4 sm:p-5 rounded-3xl border border-slate-200 dark:border-slate-700 shadow-sm animate-ios-sheet">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                        {editingAcc ? 'Edit Kantong' : 'Tambah Kantong Baru'}
                      </h3>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">Atur nama, jenis, dan warna kartu</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => {
                        setIsAdding(false);
                        setEditingAcc(null);
                      }}
                      className="px-2.5 py-1 text-xs text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors"
                    >
                      Batal
                    </button>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Nama Kantong
                    </label>
                    <input
                      type="text"
                      required
                      value={name}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => {
                        const val = e.target.value;
                        setName(val);
                        // Auto switch theme if not customized
                        if (!editingAcc) {
                          const low = val.toLowerCase();
                          if (low.includes('bca')) setSelectedTheme('bca');
                          else if (low.includes('gopay')) setSelectedTheme('gopay');
                          else if (low.includes('dana')) setSelectedTheme('dana');
                          else if (low.includes('mandiri')) setSelectedTheme('mandiri');
                          else if (low.includes('bri')) setSelectedTheme('bri');
                          else if (low.includes('jago')) setSelectedTheme('jago');
                          else if (low.includes('shopee')) setSelectedTheme('shopee');
                          else if (low.includes('cash') || low.includes('tunai') || low.includes('dompet')) setSelectedTheme('cash');
                        }
                      }}
                      placeholder="Contoh: BCA Prioritas, GoPay, DANA"
                      className="w-full px-3.5 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-brand shadow-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Kategori Akun
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'Bank', label: 'Bank', icon: 'bank' },
                        { id: 'E-Wallet', label: 'E-Wallet', icon: 'smartphone' },
                        { id: 'Cash', label: 'Tunai', icon: 'cash' },
                      ].map(item => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => {
                            setType(item.id);
                            if (item.id === 'Cash') setSelectedTheme('cash');
                            else if (item.id === 'E-Wallet' && selectedTheme === 'bca') setSelectedTheme('gopay');
                          }}
                          className={`py-2 px-2 rounded-xl border text-xs font-bold flex items-center justify-center gap-1.5 transition-all ios-btn-tap ${
                            type === item.id
                              ? 'bg-sky-50 dark:bg-slate-700 border-brand text-brand dark:text-sky-300 shadow-xs'
                              : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
                          }`}
                        >
                          <Icon name={item.icon} className="w-4 h-4" />
                          <span>{item.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Nomor Akun / Masked ID (Opsional)
                    </label>
                    <input
                      type="text"
                      value={accountNumber}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => setAccountNumber(e.target.value)}
                      placeholder="e.g. •••• 8829 atau 0812-3456-7890"
                      className="w-full px-3.5 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-brand shadow-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                      Pilihan Desain Kartu
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {Object.values(POCKET_THEMES).map(themeItem => (
                        <button
                          key={themeItem.id}
                          type="button"
                          onClick={() => setSelectedTheme(themeItem.id)}
                          className={`p-2 rounded-xl border flex items-center gap-2 transition-all ios-btn-tap ${
                            selectedTheme === themeItem.id
                              ? 'border-brand dark:border-sky-400 ring-2 ring-sky-400/30 bg-sky-50/50 dark:bg-slate-800'
                              : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-850'
                          }`}
                        >
                          <div className={`w-4 h-4 rounded-full ${themeItem.swatch} shrink-0 shadow-xs`} />
                          <span className="text-[11px] font-semibold text-slate-800 dark:text-slate-200 truncate">
                            {themeItem.label}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                      Saldo Awal (Rp)
                    </label>
                    <input
                      type="text"
                      inputMode="numeric"
                      value={initialBalance ? formatIDR(parseRawNumber(initialBalance)) : ''}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => {
                        const num = parseRawNumber(e.target.value);
                        setInitialBalance(num ? num.toString() : '');
                      }}
                      placeholder="Rp 0"
                      className="w-full px-3.5 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-xs font-bold text-slate-900 dark:text-white focus:outline-none focus:border-brand shadow-xs"
                    />
                  </div>

                  <div className="pt-2 flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setIsAdding(false);
                        setEditingAcc(null);
                      }}
                      className="flex-1 py-3 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 text-xs font-bold rounded-2xl transition-colors ios-btn-tap"
                    >
                      Batal
                    </button>
                    <button
                      type="submit"
                      className="flex-2 py-3 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-2xl shadow-md transition-colors ios-btn-tap"
                    >
                      {editingAcc ? 'Perbarui Kantong' : 'Simpan Kantong Baru'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      );
    };

    const SavingsGoalModal = ({ isOpen, onClose, onSaveGoal, onDepositGoal, goalToEdit, accounts }) => {
      const [title, setTitle] = useState('');
      const [targetAmount, setTargetAmount] = useState('');
      const [currentAmount, setCurrentAmount] = useState('0');
      const [targetDate, setTargetDate] = useState('');
      const [isClosing, setIsClosing] = useState(false);

      useEffect(() => {
        if (goalToEdit) {
          setTitle(goalToEdit.title || '');
          setTargetAmount(goalToEdit.targetAmount ? String(goalToEdit.targetAmount) : '');
          setCurrentAmount(goalToEdit.currentAmount ? String(goalToEdit.currentAmount) : '0');
          setTargetDate(goalToEdit.targetDate || '');
        } else {
          setTitle('');
          setTargetAmount('');
          setCurrentAmount('0');
          setTargetDate('');
        }
      }, [goalToEdit, isOpen]);

      if (!isOpen) return null;

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          onClose();
        }, 220);
      };

      const handleSubmit = (e) => {
        e.preventDefault();
        const rawTarget = parseRawNumber(targetAmount);
        const rawCurrent = parseRawNumber(currentAmount);
        if (!title.trim() || rawTarget <= 0) return;

        const goalData = {
          id: goalToEdit ? goalToEdit.id : ('goal_' + Date.now()),
          title: title.trim(),
          targetAmount: rawTarget,
          currentAmount: rawCurrent,
          targetDate: targetDate || '',
          createdAt: goalToEdit ? goalToEdit.createdAt : new Date().toISOString()
        };

        HapticFeedback.save();
        onSaveGoal(goalData);
        handleClose();
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-slate-800 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'}`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="ios-modal-header px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-white dark:bg-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                {goalToEdit ? 'Edit Kantong Impian' : 'Target Impian Baru'}
              </h2>
              <button
                type="button"
                onClick={handleClose}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                aria-label="Tutup"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="ios-modal-body flex-1 overflow-y-auto pb-28 p-4 sm:p-5 space-y-4 no-scrollbar">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Nama Impian</label>
                <input
                  type="text"
                  required
                  value={title}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Contoh: Beli Laptop Baru / Dana Darurat"
                  className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                  autoFocus
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Target Nominal (Rp)</label>
                <input
                  type="text"
                  inputMode="numeric"
                  required
                  value={targetAmount ? formatIDR(parseRawNumber(targetAmount)) : ''}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => {
                    const num = parseRawNumber(e.target.value);
                    setTargetAmount(num ? num.toString() : '');
                  }}
                  placeholder="Rp 0"
                  className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-bold text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Tabungan Terkumpul Saat Ini (Rp)</label>
                <input
                  type="text"
                  inputMode="numeric"
                  value={currentAmount ? formatIDR(parseRawNumber(currentAmount)) : ''}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => {
                    const num = parseRawNumber(e.target.value);
                    setCurrentAmount(num ? num.toString() : '0');
                  }}
                  placeholder="Rp 0"
                  className="w-full px-3.5 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Target Tercapai (Opsional)</label>
                <input
                  type="date"
                  value={targetDate}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => setTargetDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-3 bg-[#0284C7] hover:bg-[#0369A1] text-white font-semibold text-sm rounded-xl transition-colors shadow-sm ios-btn-tap"
                >
                  Simpan Target Impian
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    const SettingsModal = ({ isOpen, onClose, userProfile, onUpdateProfile, onHardReset, onImportData, onExportData, onOpenCsvImport, onExportCsv, theme, onToggleTheme, customCategories = [], onSaveCustomCategory, onDeleteCustomCategory, onOpenDeveloperGate }) => {
      const [name, setName] = useState(userProfile.name || '');
      const [username, setUsername] = useState(userProfile.username || '');
      const [avatar, setAvatar] = useState(userProfile.avatar || '');
      const [isChangingPin, setIsChangingPin] = useState(false);
      const [currentPin, setCurrentPin] = useState('');
      const [newPin, setNewPin] = useState('');
      const [confirmPin, setConfirmPin] = useState('');
      const [pinMsg, setPinMsg] = useState({ text: '', isError: false });
      const [isClosing, setIsClosing] = useState(false);

      // Custom Category Management in Settings
      const [isManagingCategories, setIsManagingCategories] = useState(false);
      const [catNameInput, setCatNameInput] = useState('');
      const [catEmojiInput, setCatEmojiInput] = useState('🏷️');
      const [catTypeInput, setCatTypeInput] = useState('EXPENSE');
      const [editingCatId, setEditingCatId] = useState(null);
      const [catErrorMsg, setCatErrorMsg] = useState('');

      const emojiPresets = ['🍔', '☕', '🚗', '🛍️', '💡', '🎮', '💊', '💼', '🎁', '📈', '🏷️', '🏠', '✈️', '📚', '🐾', '⚽'];

      useEffect(() => {
        setName(userProfile.name || '');
        setUsername(userProfile.username || '');
        setAvatar(userProfile.avatar || '');
      }, [userProfile, isOpen]);

      if (!isOpen) return null;

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          onClose();
        }, 220);
      };

      const handleSaveProfile = (e) => {
        e.preventDefault();
        onUpdateProfile({
          name: name.trim() || userProfile.name,
          username: username.trim() || userProfile.username,
          avatar
        });
        handleClose();
      };

      const handleChangePin = async (e) => {
        e.preventDefault();
        const storedPin = StorageService.getPin();
        const isValid = await CryptoService.verifyPin(currentPin, storedPin);
        if (!isValid) {
          setPinMsg({ text: 'PIN saat ini salah', isError: true });
          return;
        }
        if (newPin.length !== 6 || !/^\\d{6}$/.test(newPin)) {
          setPinMsg({ text: 'PIN baru harus 6 digit angka', isError: true });
          return;
        }
        if (newPin !== confirmPin) {
          setPinMsg({ text: 'Konfirmasi PIN tidak sama', isError: true });
          return;
        }

        const hashed = await CryptoService.hashPin(newPin);
        StorageService.setPin(hashed);
        setPinMsg({ text: 'PIN berhasil diubah!', isError: false });
        setTimeout(() => {
          setIsChangingPin(false);
          setCurrentPin('');
          setNewPin('');
          setConfirmPin('');
          setPinMsg({ text: '', isError: false });
        }, 1200);
      };

      const handleFileImport = (e) => {
        const file = e.target.files?.[0];
        if (file && file.size <= 2 * 1024 * 1024) {
          const reader = new FileReader();
          reader.onload = (event) => {
            try {
              const rawData = JSON.parse(event.target.result);
              const validData = Validators.validateBackupSchema(rawData);
              if (!validData) {
                alert('File JSON tidak sesuai skema Voralet atau rusak.');
                return;
              }
              onImportData(validData);
              handleClose();
            } catch (err) {
              alert('File JSON tidak valid atau rusak.');
            }
          };
          reader.readAsText(file);
        } else if (file) {
          alert('Ukuran file backup maksimal 2 MB.');
        }
        e.target.value = '';
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-slate-800 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'}`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="ios-modal-header px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-white dark:bg-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Pengaturan & Profil</h2>
              <button
                type="button"
                onClick={handleClose}
                className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                aria-label="Tutup"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <div className="ios-modal-body flex-1 overflow-y-auto pb-28 p-4 sm:p-5 space-y-5 no-scrollbar">
              {/* Profil Identitas */}
              <form onSubmit={handleSaveProfile} className="p-4 rounded-2xl bg-white dark:bg-slate-800/90 border border-slate-200/90 dark:border-slate-700 shadow-[0_4px_16px_rgba(15,23,42,0.08)] dark:shadow-[0_6px_20px_rgba(0,0,0,0.4)] space-y-4">
                <div className="flex items-center gap-4">
                  <div className="relative shrink-0 rounded-full shadow-[0_6px_18px_rgba(15,23,42,0.16)] dark:shadow-[0_8px_24px_rgba(0,0,0,0.6)] ring-2 ring-white dark:ring-slate-700">
                    <Avatar avatar={avatar} name={name} size="w-16 h-16" textSize="text-xl" />
                    <label
                      htmlFor="settings-avatar-upload"
                      className="absolute bottom-0 right-0 w-6 h-6 bg-brand text-white rounded-full flex items-center justify-center cursor-pointer shadow hover:bg-brand-hover transition-colors"
                      title="Ubah Foto"
                    >
                      <Icon name="camera" className="w-3.5 h-3.5" />
                    </label>
                    <input
                      id="settings-avatar-upload"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) compressImage(file, (dataUrl) => setAvatar(dataUrl));
                      }}
                    />
                  </div>

                  <div className="flex-1 space-y-2">
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Nama Tampilan</label>
                      <input
                        type="text"
                        value={name}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold text-slate-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-0.5">Username (@id)</label>
                      <div className="relative">
                        <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-mono font-bold">@</span>
                        <input
                          type="text"
                          value={username}
                          onFocus={handleGlobalInputFocus}
                          onBlur={handleGlobalInputBlur}
                          onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                          className="w-full pl-6 pr-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-mono font-semibold text-slate-900 dark:text-white"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-2">
                  {avatar && (
                    <button
                      type="button"
                      onClick={() => setAvatar('')}
                      className="px-3 py-1.5 text-xs text-rose-500 hover:underline"
                    >
                      Hapus Foto
                    </button>
                  )}
                  <button
                    type="submit"
                    className="px-4 py-2 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover ios-btn-tap"
                  >
                    Simpan Profil
                  </button>
                </div>
              </form>

              {/* Tampilan & Mode Gelap */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <IconBadge icon={theme === 'dark' ? 'moon' : 'sun'} className="p-2 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white">Mode Tampilan</h4>
                      <p className="text-[11px] text-slate-400">Pilih tema terang atau gelap</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={onToggleTheme}
                    className={`px-3.5 py-1.5 rounded-xl border font-semibold text-xs transition-all flex items-center gap-2 ios-btn-tap ${
                      theme === 'dark'
                        ? 'bg-slate-900 border-slate-700 text-sky-400 shadow-inner'
                        : 'bg-white border-slate-200 text-slate-700 shadow-sm'
                    }`}
                  >
                    <span className={`w-2 h-2 rounded-full ${theme === 'dark' ? 'bg-sky-400 animate-pulse' : 'bg-amber-400'}`}></span>
                    <span>{theme === 'dark' ? 'Mode Gelap (Aktif)' : 'Mode Terang (Aktif)'}</span>
                  </button>
                </div>
              </div>

              {/* Kategori Transaksi Kustom (v2.1.0) */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    <IconBadge icon="tag" className="p-2 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white">Kategori Kustom</h4>
                      <p className="text-[11px] text-slate-400">Tambah dan kelola kategori transaksi pribadi</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setIsManagingCategories(!isManagingCategories);
                      setEditingCatId(null);
                      setCatNameInput('');
                      setCatErrorMsg('');
                    }}
                    className="text-xs font-semibold text-brand dark:text-sky-400 hover:underline ios-btn-tap"
                  >
                    {isManagingCategories ? 'Tutup' : 'Kelola'}
                  </button>
                </div>

                {isManagingCategories && (
                  <div className="p-3.5 bg-slate-50 dark:bg-[#121212] border border-slate-200 dark:border-[#27272A] rounded-2xl space-y-3 mt-2 animate-ios-sheet">
                    {/* Add / Edit Form */}
                    <div className="space-y-2">
                      <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 block">
                        {editingCatId ? 'Edit Kategori' : 'Tambah Kategori Baru'}
                      </span>
                      
                      <div className="flex gap-2">
                        <select
                          value={catTypeInput}
                          onChange={(e) => setCatTypeInput(e.target.value)}
                          className="px-2.5 py-1.5 bg-white dark:bg-[#181818] border border-slate-200 dark:border-zinc-700 rounded-xl text-xs font-semibold text-slate-800 dark:text-slate-200"
                        >
                          <option value="EXPENSE">Pengeluaran</option>
                          <option value="INCOME">Pemasukan</option>
                          <option value="ALL">Semua Jenis</option>
                        </select>
                        <input
                          type="text"
                          maxLength={30}
                          value={catNameInput}
                          onChange={(e) => {
                            setCatNameInput(e.target.value);
                            setCatErrorMsg('');
                          }}
                          placeholder="Nama kategori..."
                          className="flex-1 px-3 py-1.5 bg-white dark:bg-[#181818] border border-slate-200 dark:border-zinc-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                        />
                      </div>

                      {/* Emoji Selector */}
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500 block mb-1">Pilih Icon Emoji:</label>
                        <div className="flex flex-wrap gap-1.5 p-2 bg-white dark:bg-[#181818] rounded-xl border border-slate-200 dark:border-zinc-700 max-h-24 overflow-y-auto">
                          {emojiPresets.map(emoji => (
                            <button
                              key={emoji}
                              type="button"
                              onClick={() => setCatEmojiInput(emoji)}
                              className={`w-7 h-7 flex items-center justify-center rounded-lg text-sm transition-all ios-btn-tap ${
                                catEmojiInput === emoji ? 'bg-sky-100 dark:bg-slate-700 scale-110 shadow-sm' : 'hover:bg-slate-100 dark:hover:bg-zinc-800'
                              }`}
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </div>

                      {catErrorMsg && <p className="text-[10px] text-rose-500 font-semibold">{catErrorMsg}</p>}

                      <div className="flex gap-2">
                        {editingCatId && (
                          <button
                            type="button"
                            onClick={() => {
                              setEditingCatId(null);
                              setCatNameInput('');
                              setCatErrorMsg('');
                            }}
                            className="px-3 py-1.5 bg-slate-200 dark:bg-zinc-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-semibold ios-btn-tap"
                          >
                            Batal Edit
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => {
                            const trimmed = catNameInput.trim();
                            if (!trimmed) {
                              setCatErrorMsg('Nama kategori tidak boleh kosong');
                              return;
                            }
                            const catObj = {
                              id: editingCatId || ('custom_' + Date.now().toString(36)),
                              label: Validators.sanitizeText(trimmed, 40),
                              icon: catEmojiInput || '🏷️',
                              type: catTypeInput,
                              isCustom: true
                            };
                            if (typeof onSaveCustomCategory === 'function') {
                              onSaveCustomCategory(catObj);
                            }
                            setEditingCatId(null);
                            setCatNameInput('');
                            setCatErrorMsg('');
                          }}
                          className="flex-1 py-1.5 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover ios-btn-tap flex items-center justify-center gap-1"
                        >
                          <Icon name="check" className="w-3.5 h-3.5" />
                          <span>{editingCatId ? 'Simpan Perubahan' : '+ Simpan Kategori'}</span>
                        </button>
                      </div>
                    </div>

                    {/* Existing Custom Categories List */}
                    <div className="pt-2 border-t border-slate-200 dark:border-zinc-800">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                        Daftar Kategori Kustom ({customCategories.length})
                      </span>
                      {customCategories.length === 0 ? (
                        <p className="text-[11px] text-slate-400 italic">Belum ada kategori kustom yang dibuat.</p>
                      ) : (
                        <div className="space-y-1.5 max-h-48 overflow-y-auto">
                          {customCategories.map(cat => (
                            <div
                              key={cat.id}
                              className="flex items-center justify-between p-2 rounded-xl bg-white dark:bg-[#181818] border border-slate-200 dark:border-zinc-700"
                            >
                              <div className="flex items-center gap-2 min-w-0">
                                <span className="text-base">{cat.icon}</span>
                                <div className="min-w-0">
                                  <p className="text-xs font-bold text-slate-800 dark:text-white truncate">{cat.label}</p>
                                  <span className="text-[9px] text-slate-400 uppercase tracking-wider">{cat.type}</span>
                                </div>
                              </div>
                              <div className="flex items-center gap-1 shrink-0">
                                <button
                                  type="button"
                                  onClick={() => {
                                    setEditingCatId(cat.id);
                                    setCatNameInput(cat.label);
                                    setCatEmojiInput(cat.icon);
                                    setCatTypeInput(cat.type);
                                  }}
                                  className="p-1 text-slate-400 hover:text-brand rounded-lg ios-btn-tap"
                                  title="Edit"
                                >
                                  <Icon name="edit" className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => {
                                    if (confirm(`Hapus kategori "${cat.label}"?`)) {
                                      if (typeof onDeleteCustomCategory === 'function') {
                                        onDeleteCustomCategory(cat.id);
                                      }
                                    }
                                  }}
                                  className="p-1 text-slate-400 hover:text-rose-500 rounded-lg ios-btn-tap"
                                  title="Hapus"
                                >
                                  <Icon name="trash" className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Keamanan & Ubah PIN */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    <IconBadge icon="lock" className="p-2 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white">Keamanan PIN</h4>
                      <p className="text-[11px] text-slate-400">Ubah 6-digit PIN keamanan brankas</p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setIsChangingPin(prev => !prev)}
                    className="text-xs font-semibold text-brand dark:text-sky-400 hover:underline"
                  >
                    {isChangingPin ? 'Tutup' : 'Ubah PIN'}
                  </button>
                </div>

                {isChangingPin && (
                  <form onSubmit={handleChangePin} className="p-3.5 bg-slate-50 dark:bg-[#121212] border border-slate-200 dark:border-[#27272A] rounded-2xl space-y-3 mt-2">
                    <div>
                      <label className="text-[11px] font-semibold text-slate-600 dark:text-zinc-400 block mb-1">PIN Lama</label>
                      <input
                        type="password"
                        maxLength={6}
                        required
                        value={currentPin}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => setCurrentPin(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                        placeholder="••••••"
                        className="w-full px-3 py-2 bg-white dark:bg-[#181818] border-2 border-slate-300 dark:border-zinc-700 rounded-xl text-center font-bold tracking-widest text-sm text-slate-900 dark:text-white focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-semibold text-slate-600 dark:text-zinc-400 block mb-1">PIN Baru (6 Angka)</label>
                      <input
                        type="password"
                        maxLength={6}
                        required
                        value={newPin}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => setNewPin(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                        placeholder="••••••"
                        className="w-full px-3 py-2 bg-white dark:bg-[#181818] border-2 border-slate-300 dark:border-zinc-700 rounded-xl text-center font-bold tracking-widest text-sm text-slate-900 dark:text-white focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-semibold text-slate-600 dark:text-zinc-400 block mb-1">Konfirmasi PIN Baru</label>
                      <input
                        type="password"
                        maxLength={6}
                        required
                        value={confirmPin}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => setConfirmPin(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                        placeholder="••••••"
                        className="w-full px-3 py-2 bg-white dark:bg-[#181818] border-2 border-slate-300 dark:border-zinc-700 rounded-xl text-center font-bold tracking-widest text-sm text-slate-900 dark:text-white focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors"
                      />
                    </div>

                    {pinMsg.text && (
                      <p className={`text-xs font-semibold ${pinMsg.isError ? 'text-rose-500' : 'text-emerald-500'}`}>
                        {pinMsg.text}
                      </p>
                    )}

                    <button
                      type="submit"
                      className="w-full py-2 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover ios-btn-tap"
                    >
                      Simpan PIN Baru
                    </button>
                  </form>
                )}
              </div>

              {/* Cadangan & Migrasi Data */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700 space-y-2.5">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">Cadangan & Migrasi Data</h4>
                    <p className="text-[11px] text-slate-400">
                      Ekspor/impor cadangan JSON atau migrasi data mutasi dari aplikasi lain via CSV.
                    </p>
                  </div>
                </div>

                {/* CSV Migration Action Banner */}
                <div className="p-3 rounded-2xl bg-sky-50/80 dark:bg-slate-900/80 border border-sky-200/80 dark:border-slate-700 flex items-center justify-between gap-3 shadow-xs">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="w-8 h-8 rounded-xl bg-brand text-white flex items-center justify-center shrink-0 shadow-sm">
                      <Icon name="file-text" className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <h5 className="text-xs font-bold text-slate-900 dark:text-white truncate leading-tight">
                        Impor Transaksi dari CSV
                      </h5>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                        Pindahkan catatan mutasi dari spreadsheet / aplikasi lain
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      handleClose();
                      if (onOpenCsvImport) onOpenCsvImport();
                    }}
                    className="px-3 py-1.5 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-xl shrink-0 shadow-xs ios-btn-tap flex items-center gap-1"
                  >
                    <Icon name="upload" className="w-3.5 h-3.5" />
                    <span>Mulai Impor</span>
                  </button>
                </div>

                {/* Standard JSON Backup / Restore Buttons */}
                <div className="flex gap-2 pt-0.5">
                  <button
                    type="button"
                    onClick={onExportData}
                    className="flex-1 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 ios-btn-tap"
                  >
                    <Icon name="download" className="w-4 h-4" />
                    <span>Ekspor Cadangan</span>
                  </button>
                  <label className="flex-1 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 cursor-pointer ios-btn-tap">
                    <Icon name="upload" className="w-4 h-4" />
                    <span>Pulihkan JSON</span>
                    <input type="file" accept=".json" className="hidden" onChange={handleFileImport} />
                  </label>
                </div>
              </div>

              {/* Profile / About Section with Brand Logo */}
              <div className="pt-4 border-t border-slate-100 dark:border-slate-700 flex flex-col items-center text-center space-y-1.5 select-none">
                <VoraletLogo size="md" className="mb-1" />
                <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300">
                  Voralet iOS Edition • Versi v__VORALET_VERSION__
                </p>
                <p className="text-[10px] text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed">
                  Keuangan Sehat • Impian Dekat. 100% Offline & Terenkripsi Lokal di Perangkat Anda.
                </p>
              </div>

              {/* Master Developer & Security Gate (Code: 2026) */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700">
                <button
                  type="button"
                  onClick={() => {
                    if (onOpenDeveloperGate) onOpenDeveloperGate();
                  }}
                  className="w-full py-2.5 px-3 bg-sky-50 dark:bg-slate-700/60 hover:bg-sky-100 dark:hover:bg-slate-700 text-sky-700 dark:text-sky-300 text-xs font-semibold rounded-xl border border-sky-200/80 dark:border-slate-600 flex items-center justify-between transition-colors ios-btn-tap"
                >
                  <div className="flex items-center gap-2">
                    <Icon name="shield-check" className="w-4 h-4 text-brand dark:text-sky-400" />
                    <span>Opsi Pengembang & Keamanan Master</span>
                  </div>
                  <span className="text-[10px] bg-sky-200/70 dark:bg-slate-800 px-2 py-0.5 rounded-md font-mono font-bold text-brand dark:text-sky-300">KODE: 2026</span>
                </button>
              </div>

              {/* Reset Data */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700">
                <button
                  type="button"
                  onClick={() => {
                    if (onOpenDeveloperGate) {
                      onOpenDeveloperGate();
                    } else if (confirm('PERINGATAN: Semua data dompet, mutasi, hutang, dan PIN akan dihapus total dari perangkat ini. Lanjutkan?')) {
                      onHardReset();
                    }
                  }}
                  className="w-full py-2.5 bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 hover:bg-rose-100 text-xs font-semibold rounded-xl border border-rose-200 dark:border-rose-900/60 transition-colors ios-btn-tap"
                >
                  Reset Semua Data Aplikasi
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    };

    // =========================================================================
    // CSV IMPORT MODAL (Preview, Field Mapping, Verification & Batch Execution)
    // =========================================================================
    const CsvImportModal = ({
      isOpen,
      onClose,
      accounts = [],
      customCategories = [],
      onImportBatch
    }) => {
      const [step, setStep] = useState(1); // 1: Select File/Paste, 2: Column Mapping & Preview, 3: Success Result
      const [rawCsvText, setRawCsvText] = useState('');
      const [parsedRows, setParsedRows] = useState([]);
      const [headers, setHeaders] = useState([]);
      const [fileName, setFileName] = useState('');
      const [targetAccountId, setTargetAccountId] = useState(accounts[0]?.id || '');
      const [hasHeaderRow, setHasHeaderRow] = useState(true);
      const [errorMessage, setErrorMessage] = useState('');
      const [isClosing, setIsClosing] = useState(false);
      const [importStats, setImportStats] = useState({ total: 0, expenses: 0, incomes: 0, sumAmount: 0 });

      // Column mapping states
      const [colDate, setColDate] = useState(0);
      const [colAmount, setColAmount] = useState(1);
      const [colType, setColType] = useState(-1);
      const [colCategory, setColCategory] = useState(-1);
      const [colNotes, setColNotes] = useState(-1);
      const [defaultType, setDefaultType] = useState('EXPENSE'); // Used if colType is -1

      const allCategories = useMemo(() => getAllCategories(customCategories), [customCategories]);

      useEffect(() => {
        if (accounts.length > 0 && !targetAccountId) {
          setTargetAccountId(accounts[0].id);
        }
      }, [accounts, targetAccountId]);

      useEffect(() => {
        if (!isOpen) {
          // Reset states when closed
          setStep(1);
          setRawCsvText('');
          setParsedRows([]);
          setHeaders([]);
          setFileName('');
          setErrorMessage('');
        }
      }, [isOpen]);

      if (!isOpen) return null;

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          onClose();
        }, 220);
      };

      const handleFileSelected = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setErrorMessage('');
        setFileName(file.name);

        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target?.result;
          processCsvText(text, file.name);
        };
        reader.onerror = () => {
          setErrorMessage('Gagal membaca file CSV. Pastikan format teks UTF-8.');
        };
        reader.readAsText(file);
        e.target.value = '';
      };

      const handleDownloadTemplate = () => {
        const content = CsvService.getCSVTemplate();
        const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'voralet_template_mutasi.csv';
        a.click();
        URL.revokeObjectURL(url);
      };

      const processCsvText = (text, name = 'Pasted_Data.csv') => {
        if (!text || !text.trim()) {
          setErrorMessage('Konten CSV kosong.');
          return;
        }

        const rows = CsvService.parseCSV(text);
        if (rows.length === 0) {
          setErrorMessage('Tidak ada baris data yang terdeteksi dalam file CSV.');
          return;
        }

        const firstRow = rows[0];
        setHeaders(firstRow);
        setParsedRows(rows);
        setRawCsvText(text);
        setFileName(name);

        // Auto-detect columns
        const detected = CsvService.detectColumns(firstRow);
        setColDate(detected.date >= 0 ? detected.date : 0);
        setColAmount(detected.amount >= 0 ? detected.amount : (firstRow.length > 1 ? 1 : 0));
        setColType(detected.type);
        setColCategory(detected.category);
        setColNotes(detected.notes);

        setStep(2);
      };

      // Preview rows to display
      const dataRows = hasHeaderRow ? parsedRows.slice(1) : parsedRows;

      // Generate parsed transactions preview & stats
      const previewTransactions = useMemo(() => {
        if (dataRows.length === 0) return [];
        const result = [];
        let expCount = 0;
        let incCount = 0;
        let totalAmt = 0;

        for (let i = 0; i < dataRows.length; i++) {
          const row = dataRows[i];
          if (!row || row.length === 0 || row.every(cell => !cell)) continue;

          // 1. Parse Date
          const rawDate = colDate >= 0 ? row[colDate] : '';
          const date = CsvService.parseFlexibleDate(rawDate);

          // 2. Parse Amount & Type
          const rawAmt = colAmount >= 0 ? row[colAmount] : '';
          const parsedNum = CsvService.parseAmount(rawAmt);
          const absAmount = Math.abs(parsedNum);
          if (absAmount <= 0) continue; // Skip 0 or invalid

          let type = defaultType;
          if (colType >= 0 && row[colType]) {
            const rawType = String(row[colType]).trim().toLowerCase();
            if (/masuk|income|kredit|cr|plus|\\+|pendapatan|terima/i.test(rawType)) {
              type = 'INCOME';
            } else if (/keluar|expense|debet|dr|minus|-|pengeluaran|bayar/i.test(rawType)) {
              type = 'EXPENSE';
            }
          } else if (parsedNum < 0) {
            type = 'EXPENSE';
          }

          // 3. Category
          let category = 'lainnya';
          if (colCategory >= 0 && row[colCategory]) {
            category = CsvService.matchCategory(row[colCategory], allCategories);
          }

          // 4. Notes
          let notes = '';
          if (colNotes >= 0 && row[colNotes]) {
            notes = String(row[colNotes]).trim();
          }

          if (type === 'INCOME') incCount++;
          else expCount++;
          totalAmt += absAmount;

          result.push({
            id: 'tx_csv_' + Date.now() + '_' + i,
            accountId: targetAccountId || (accounts[0]?.id || 'acc_default'),
            type,
            amount: absAmount,
            category,
            date,
            notes: Validators.sanitizeText(notes, 100),
            createdAt: new Date().toISOString()
          });
        }

        setImportStats({
          total: result.length,
          expenses: expCount,
          incomes: incCount,
          sumAmount: totalAmt
        });

        return result;
      }, [dataRows, colDate, colAmount, colType, colCategory, colNotes, defaultType, targetAccountId, allCategories, accounts]);

      const handleExecuteImport = () => {
        if (previewTransactions.length === 0) {
          alert('Tidak ada transaksi valid untuk diimpor. Periksa kembali pemetaan kolom.');
          return;
        }

        if (!targetAccountId) {
          alert('Silakan pilih kantong/dompet tujuan untuk mutasi ini.');
          return;
        }

        // Execute batch import
        if (typeof onImportBatch === 'function') {
          onImportBatch(previewTransactions);
        }
        HapticFeedback.save();
        setStep(3);
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-slate-800 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'} max-w-lg mx-auto`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="ios-modal-header px-5 py-3.5 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-white dark:bg-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400">
                  <Icon name="file-text" className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                    Impor Transaksi CSV
                  </h2>
                  <p className="text-[10px] text-slate-400">
                    {step === 1 ? 'Pilih atau unggah file CSV' : step === 2 ? 'Sesuaikan Kolom & Pratinjau' : 'Impor Selesai'}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleClose}
                className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                aria-label="Tutup"
              >
                <Icon name="x" className="w-4 h-4" />
              </button>
            </div>

            <div className="ios-modal-body flex-1 overflow-y-auto pb-28 p-4 sm:p-5 space-y-4 no-scrollbar">
              {/* STEP 1: Upload or Paste CSV */}
              {step === 1 && (
                <div className="space-y-4">
                  <div className="p-4 rounded-2xl bg-sky-50/70 dark:bg-slate-900/60 border border-sky-100 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-300 space-y-2">
                    <p className="font-semibold text-slate-800 dark:text-white">
                      Migrasi mutasi dari aplikasi keuangan lain atau spreadsheet Excel/Google Sheets.
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Sistem kami secara otomatis mendeteksi kolom Tanggal, Nominal, Kategori, Catatan, serta pembatas koma maupun titik koma.
                    </p>
                    <div className="pt-1">
                      <button
                        type="button"
                        onClick={handleDownloadTemplate}
                        className="inline-flex items-center gap-1 text-[11px] font-bold text-brand hover:underline"
                      >
                        <Icon name="download" className="w-3.5 h-3.5" />
                        <span>Unduh Contoh Template CSV</span>
                      </button>
                    </div>
                  </div>

                  {/* Upload Box */}
                  <label className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand dark:hover:border-brand rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer transition-colors bg-slate-50/50 dark:bg-slate-900/30 ios-btn-tap group">
                    <div className="w-12 h-12 rounded-2xl bg-white dark:bg-slate-800 shadow-sm border border-slate-200 dark:border-slate-700 flex items-center justify-center text-brand mb-2 group-hover:scale-105 transition-transform">
                      <Icon name="upload" className="w-6 h-6" />
                    </div>
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                      Pilih Berkas .CSV dari Perangkat
                    </span>
                    <span className="text-[10px] text-slate-400 mt-0.5">
                      Klik untuk memilih file CSV
                    </span>
                    <input
                      type="file"
                      accept=".csv,text/csv,text/plain"
                      onChange={handleFileSelected}
                      className="hidden"
                    />
                  </label>

                  {/* Or Paste Raw CSV Text */}
                  <div className="space-y-1.5 pt-1">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                        Atau Salin & Tempel Teks CSV di Sini:
                      </label>
                      <button
                        type="button"
                        onClick={() => {
                          setRawCsvText("Tanggal,Jenis,Nominal,Kategori,Catatan\\n2026-09-15,Pengeluaran,35000,Makan,Makan siang\\n2026-09-15,Pemasukan,5000000,Gaji,Gaji kantor");
                        }}
                        className="text-[10px] font-bold text-brand hover:underline"
                      >
                        Pakai Contoh
                      </button>
                    </div>
                    <textarea
                      rows={4}
                      value={rawCsvText}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => setRawCsvText(e.target.value)}
                      placeholder="Contoh:&#10;Tanggal,Nominal,Catatan&#10;2026-09-15,50000,Makan Siang&#10;2026-09-16,25000,Kopi"
                      className="w-full p-3 font-mono text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                    />
                  </div>

                  {errorMessage && (
                    <p className="text-xs font-semibold text-rose-500 bg-rose-50 dark:bg-rose-950/40 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
                      {errorMessage}
                    </p>
                  )}

                  <button
                    type="button"
                    disabled={!rawCsvText.trim()}
                    onClick={() => processCsvText(rawCsvText, 'Teks_CSV_Langsung.csv')}
                    className="w-full py-2.5 bg-brand hover:bg-brand-hover disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-sm transition-all ios-btn-tap"
                  >
                    Lanjutkan ke Pemetaan Kolom →
                  </button>
                </div>
              )}

              {/* STEP 2: Mapping & Preview */}
              {step === 2 && (
                <div className="space-y-4">
                  {/* File info banner */}
                  <div className="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl flex items-center justify-between text-xs">
                    <div>
                      <p className="font-bold text-slate-800 dark:text-white truncate max-w-[200px]">{fileName}</p>
                      <p className="text-[10px] text-slate-400">{parsedRows.length} baris terdeteksi</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="text-[11px] font-semibold text-brand hover:underline"
                    >
                      Ganti Berkas
                    </button>
                  </div>

                  {/* Destination Pocket Selection */}
                  <div>
                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                      Pilih Dompet / Kantong Tujuan:
                    </label>
                    <select
                      value={targetAccountId}
                      onChange={(e) => setTargetAccountId(e.target.value)}
                      className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                    >
                      {accounts.map(acc => (
                        <option key={acc.id} value={acc.id}>{acc.name}</option>
                      ))}
                    </select>
                  </div>

                  {/* Header row toggle */}
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={hasHeaderRow}
                      onChange={(e) => setHasHeaderRow(e.target.checked)}
                      className="w-4 h-4 rounded text-brand focus:ring-brand accent-brand"
                    />
                    <span className="text-xs text-slate-700 dark:text-slate-300 font-medium">
                      Baris pertama adalah judul kolom (Header)
                    </span>
                  </label>

                  {/* Column Mapping Selectors */}
                  <div className="p-3.5 bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-700 rounded-2xl space-y-3">
                    <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                      <Icon name="filter" className="w-3.5 h-3.5 text-brand" />
                      Sesuaikan Pemetaan Kolom CSV
                    </h4>

                    <div className="grid grid-cols-2 gap-2.5">
                      {/* Date Column */}
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                          Kolom Tanggal *
                        </label>
                        <select
                          value={colDate}
                          onChange={(e) => setColDate(parseInt(e.target.value, 10))}
                          className="w-full px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200"
                        >
                          {headers.map((h, i) => (
                            <option key={i} value={i}>Kolom {i + 1}: {h || `(Kolom ${i + 1})`}</option>
                          ))}
                        </select>
                      </div>

                      {/* Amount Column */}
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                          Kolom Nominal *
                        </label>
                        <select
                          value={colAmount}
                          onChange={(e) => setColAmount(parseInt(e.target.value, 10))}
                          className="w-full px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200"
                        >
                          {headers.map((h, i) => (
                            <option key={i} value={i}>Kolom {i + 1}: {h || `(Kolom ${i + 1})`}</option>
                          ))}
                        </select>
                      </div>

                      {/* Type Column */}
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                          Kolom Jenis / Tipe (Opsional)
                        </label>
                        <select
                          value={colType}
                          onChange={(e) => setColType(parseInt(e.target.value, 10))}
                          className="w-full px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200"
                        >
                          <option value={-1}>-- Tidak Ada (Gunakan Default) --</option>
                          {headers.map((h, i) => (
                            <option key={i} value={i}>Kolom {i + 1}: {h || `(Kolom ${i + 1})`}</option>
                          ))}
                        </select>
                      </div>

                      {/* Default Type if none */}
                      {colType === -1 && (
                        <div>
                          <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                            Jenis Bawaan
                          </label>
                          <select
                            value={defaultType}
                            onChange={(e) => setDefaultType(e.target.value)}
                            className="w-full px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200"
                          >
                            <option value="EXPENSE">Pengeluaran</option>
                            <option value="INCOME">Pemasukan</option>
                          </select>
                        </div>
                      )}

                      {/* Category Column */}
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                          Kolom Kategori (Opsional)
                        </label>
                        <select
                          value={colCategory}
                          onChange={(e) => setColCategory(parseInt(e.target.value, 10))}
                          className="w-full px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200"
                        >
                          <option value={-1}>-- Tidak Ada --</option>
                          {headers.map((h, i) => (
                            <option key={i} value={i}>Kolom {i + 1}: {h || `(Kolom ${i + 1})`}</option>
                          ))}
                        </select>
                      </div>

                      {/* Notes Column */}
                      <div>
                        <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                          Kolom Catatan / Deskripsi (Opsional)
                        </label>
                        <select
                          value={colNotes}
                          onChange={(e) => setColNotes(parseInt(e.target.value, 10))}
                          className="w-full px-2 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200"
                        >
                          <option value={-1}>-- Tidak Ada --</option>
                          {headers.map((h, i) => (
                            <option key={i} value={i}>Kolom {i + 1}: {h || `(Kolom ${i + 1})`}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Summary Metric Badge */}
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                      <span className="text-[10px] font-semibold text-slate-400 block">Total Mutasi</span>
                      <span className="text-sm font-extrabold text-slate-800 dark:text-white">
                        {importStats.total}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900">
                      <span className="text-[10px] font-semibold text-rose-500 block">Pengeluaran</span>
                      <span className="text-sm font-extrabold text-rose-600 dark:text-rose-400">
                        {importStats.expenses}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900">
                      <span className="text-[10px] font-semibold text-emerald-500 block">Pemasukan</span>
                      <span className="text-sm font-extrabold text-emerald-600 dark:text-emerald-400">
                        {importStats.incomes}
                      </span>
                    </div>
                  </div>

                  {/* Preview of first 5 transactions */}
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1.5">
                      Pratinjau Hasil Impor (5 Teratas):
                    </span>
                    <div className="space-y-1.5 max-h-48 overflow-y-auto no-scrollbar">
                      {previewTransactions.slice(0, 5).map((t, idx) => {
                        const catObj = allCategories.find(c => c.id === t.category);
                        return (
                          <div key={idx} className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-xs">
                            <div className="min-w-0 pr-2">
                              <p className="font-bold text-slate-800 dark:text-slate-200 truncate">
                                {t.notes || catObj?.label || 'Mutasi'}
                              </p>
                              <p className="text-[10px] text-slate-400">
                                {formatDateID(t.date)} • {catObj?.label || 'Lainnya'}
                              </p>
                            </div>
                            <span className={`font-extrabold whitespace-nowrap ${t.type === 'INCOME' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
                              {t.type === 'INCOME' ? '+' : '-'}{formatIDR(t.amount)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="flex-1 py-2.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold rounded-xl ios-btn-tap"
                    >
                      Kembali
                    </button>
                    <button
                      type="button"
                      disabled={previewTransactions.length === 0}
                      onClick={handleExecuteImport}
                      className="flex-1 py-2.5 bg-brand hover:bg-brand-hover disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-sm ios-btn-tap flex items-center justify-center gap-1.5"
                    >
                      <Icon name="check" className="w-4 h-4" />
                      <span>Impor {previewTransactions.length} Mutasi</span>
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 3: Success Confirmation */}
              {step === 3 && (
                <div className="text-center py-6 space-y-4 animate-ios-sheet">
                  <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto shadow-md">
                    <Icon name="check-circle" className="w-8 h-8" strokeWidth={2.5} />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-base font-bold text-slate-900 dark:text-white">
                      Impor Berhasil Diselesaikan!
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mx-auto">
                      Sebanyak <strong>{importStats.total} transaksi</strong> telah berhasil ditambahkan ke riwayat dompet Anda.
                    </p>
                  </div>

                  <div className="p-3 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 max-w-xs mx-auto text-xs space-y-1 text-slate-600 dark:text-slate-300">
                    <div className="flex justify-between">
                      <span>Pengeluaran:</span>
                      <strong className="text-rose-500">{importStats.expenses} transaksi</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Pemasukan:</span>
                      <strong className="text-emerald-500">{importStats.incomes} transaksi</strong>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleClose}
                    className="w-full max-w-xs mx-auto py-2.5 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-xl shadow-sm ios-btn-tap"
                  >
                    Selesai & Lihat Dashboard
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    };

    // =========================================================================
    // MASTER DEVELOPER SECURITY MODAL (VERIFICATION KEY: 2026)
    // =========================================================================
    const DeveloperSecurityModal = ({ isOpen, onClose, onHardReset, accounts, transactions, debts, savingsGoals }) => {
      if (!isOpen) return null;

      const [masterCode, setMasterCode] = useState('');
      const [isAuthorized, setIsAuthorized] = useState(false);
      const [errorMsg, setErrorMsg] = useState('');
      const [storageReport, setStorageReport] = useState([]);
      const [integrityReport, setIntegrityReport] = useState(null);
      const [isShaking, setIsShaking] = useState(false);

      useEffect(() => {
        if (isOpen) {
          setMasterCode('');
          setIsAuthorized(false);
          setErrorMsg('');
          setIntegrityReport(CryptoService.verifyIntegrity());
          setStorageReport(SafeStorage.getRawStorageReport());
        }
      }, [isOpen]);

      const handleAuthorize = (e) => {
        if (e) e.preventDefault();
        if (CryptoService.verifyMasterCode(masterCode)) {
          setIsAuthorized(true);
          setErrorMsg('');
          setStorageReport(SafeStorage.getRawStorageReport());
          setIntegrityReport(CryptoService.verifyIntegrity());
        } else {
          setErrorMsg('Kunci Master Salah! Diperlukan kode verifikasi: 2026');
          setIsShaking(true);
          setTimeout(() => setIsShaking(false), 500);
        }
      };

      const handleReverifyIntegrity = () => {
        const res = CryptoService.verifyIntegrity();
        setIntegrityReport(res);
        setStorageReport(SafeStorage.getRawStorageReport());
      };

      return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-900/60 backdrop-blur-sm animate-ios-sheet">
          <div className="w-full max-w-md bg-white dark:bg-slate-800 rounded-t-3xl sm:rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-700 max-h-[92dvh] flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-full bg-sky-100 dark:bg-slate-700 flex items-center justify-center text-brand dark:text-sky-400">
                  <Icon name="shield-check" className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Master Security Gate</h3>
                  <p className="text-[10px] text-slate-400">Akses Pengembang & Integritas Kode v2.3.0</p>
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 flex items-center justify-center text-slate-500 ios-btn-tap"
              >
                <Icon name="x" className="w-4 h-4" />
              </button>
            </div>

            {/* Content */}
            <div className="p-4 sm:p-5 overflow-y-auto space-y-4">
              {!isAuthorized ? (
                <div className={`space-y-4 ${isShaking ? 'animate-ios-pin-shake' : ''}`}>
                  <div className="p-4 bg-sky-50 dark:bg-slate-700/50 rounded-2xl border border-sky-100 dark:border-slate-600 text-center">
                    <Icon name="lock" className="w-8 h-8 text-brand dark:text-sky-400 mx-auto mb-2" />
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">Autentikasi Pengembang</h4>
                    <p className="text-[11px] text-slate-500 dark:text-slate-300 mt-1">
                      Masukkan master security verification key <span className="font-bold text-brand dark:text-sky-400">2026</span> untuk mengakses konfigurasi sistem.
                    </p>
                  </div>

                  <form onSubmit={handleAuthorize} className="space-y-3">
                    <div>
                      <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">
                        Master Security Key
                      </label>
                      <input
                        type="password"
                        autoFocus
                        maxLength={6}
                        value={masterCode}
                        onChange={(e) => {
                          setMasterCode(e.target.value.slice(0, 6));
                          if (errorMsg) setErrorMsg('');
                        }}
                        placeholder="Ketik 2026"
                        className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-center font-mono font-bold tracking-widest text-base text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                      />
                    </div>

                    {errorMsg && (
                      <p className="text-xs font-semibold text-rose-500 text-center">{errorMsg}</p>
                    )}

                    <button
                      type="submit"
                      className="w-full py-2.5 bg-brand text-white font-semibold text-xs rounded-xl hover:bg-brand-hover ios-btn-tap"
                    >
                      Buka Akses Master (2026)
                    </button>
                  </form>
                </div>
              ) : (
                <div className="space-y-4 animate-ios-spring-pop">
                  {/* Authorized Banner */}
                  <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-2xl flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Icon name="check-circle" className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      <div>
                        <p className="text-xs font-bold text-emerald-800 dark:text-emerald-200">MASTER ACCESS GRANTED</p>
                        <p className="text-[10px] text-emerald-600 dark:text-emerald-400">Kode 2026 terverifikasi dengan aman</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-200 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-200 rounded font-bold">LEVEL-0</span>
                  </div>

                  {/* Code Integrity & Anti-Tamper */}
                  <div className="p-3.5 bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <Icon name="shield-check" className="w-3.5 h-3.5 text-brand" />
                        Integritas Kode & Anti-Tamper
                      </span>
                      <button
                        type="button"
                        onClick={handleReverifyIntegrity}
                        className="text-[11px] text-brand dark:text-sky-400 font-semibold hover:underline"
                      >
                        Pindai Ulang
                      </button>
                    </div>
                    <div className="text-[11px] font-mono space-y-1 text-slate-600 dark:text-slate-300">
                      <div className="flex justify-between">
                        <span>Status Sistem:</span>
                        <span className="text-emerald-600 font-bold">{integrityReport?.intact ? 'VALID / UNTOUCHED' : 'ANOMALY'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Checksum Engine:</span>
                        <span className="text-slate-500">{integrityReport?.checksum || 'SHA256-V230'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Anti-Tamper Isolation:</span>
                        <span className="text-emerald-600 font-bold">ACTIVE</span>
                      </div>
                    </div>
                  </div>

                  {/* Storage Encryption Inspector */}
                  <div className="p-3.5 bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <Icon name="lock" className="w-3.5 h-3.5 text-brand" />
                        Enkripsi Penyimpanan (Dynamic Salt)
                      </span>
                      <span className="text-[10px] text-emerald-600 font-bold font-mono">enc:v2: ACTIVE</span>
                    </div>
                    <p className="text-[10px] text-slate-400">
                      Seluruh mutasi, saldo, kantong, hutang, dan impian dienkripsi sebelum disimpan ke localStorage.
                    </p>
                    <div className="max-h-28 overflow-y-auto space-y-1 text-[10px] font-mono bg-white dark:bg-slate-950 p-2 rounded-xl border border-slate-200 dark:border-slate-800">
                      {storageReport.length === 0 ? (
                        <p className="text-slate-400">Penyimpanan kosong atau berbasis memori</p>
                      ) : (
                        storageReport.map((item, idx) => (
                          <div key={idx} className="flex justify-between py-0.5 border-b border-slate-100 dark:border-slate-900 last:border-0">
                            <span className="text-slate-700 dark:text-slate-300 truncate max-w-[120px]">{item.key}</span>
                            <span className="text-emerald-500 truncate max-w-[150px]">{item.sample}</span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* App Telemetry & Diagnostics */}
                  <div className="p-3.5 bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-1 text-[11px] font-mono text-slate-600 dark:text-slate-300">
                    <div className="flex justify-between">
                      <span>Versi Voralet:</span>
                      <span className="font-bold">v2.3.0 (Production)</span>
                    </div>
                    <div className="flex justify-between">
                      <span>React Core:</span>
                      <span>18.3.1 (Concurrent Root)</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Kantong Aktif:</span>
                      <span>{accounts?.length || 0} akun</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Catatan Mutasi:</span>
                      <span>{transactions?.length || 0} entri</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Hutang / Piutang:</span>
                      <span>{debts?.length || 0} entri</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Kantong Impian:</span>
                      <span>{savingsGoals?.length || 0} target</span>
                    </div>
                  </div>

                  {/* Master Reset Operation */}
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={() => {
                        if (confirm('PERINGATAN MASTER DEVELOPER (KODE 2026): Hapus semua data aplikasi dan kembalikan ke kondisi pabrik?')) {
                          onHardReset();
                          onClose();
                        }
                      }}
                      className="w-full py-2.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-xl transition-colors ios-btn-tap flex items-center justify-center gap-1.5"
                    >
                      <Icon name="trash" className="w-4 h-4" />
                      <span>Eksekusi Master Factory Reset</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    };
"""
