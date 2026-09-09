PART6_MODALS = """
    // =========================================================================
    // 6. CORE MODALS (TRANSACTION, ACCOUNTS, SAVINGS, SETTINGS)
    // =========================================================================
    const TransactionModal = ({ isOpen, onClose, initialData, accounts, onAddTransaction }) => {
      const [type, setType] = useState('EXPENSE');
      const [amountStr, setAmountStr] = useState('');
      const [accountId, setAccountId] = useState(accounts[0]?.id || '');
      const [category, setCategory] = useState(CATEGORIES[0].id);
      const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
      const [notes, setNotes] = useState('');
      const [error, setError] = useState('');
      const [isClosing, setIsClosing] = useState(false);

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          onClose();
        }, 220);
      };

      useEffect(() => {
        if (initialData) {
          setType(initialData.type || 'EXPENSE');
          setAmountStr(initialData.amount ? String(initialData.amount) : '');
          setCategory(initialData.category || CATEGORIES[0].id);
          setNotes(initialData.notes || '');
          if (initialData.accountId) setAccountId(initialData.accountId);
        } else {
          setType('EXPENSE');
          setAmountStr('');
          setCategory(CATEGORIES[0].id);
          setNotes('');
        }
        if (accounts.length > 0 && !accounts.some(a => a.id === accountId)) {
          setAccountId(accounts[0].id);
        }
      }, [initialData, accounts, isOpen]);

      if (!isOpen) return null;

      const filteredCategories = CATEGORIES.filter(c => c.type === 'ALL' || c.type === type);

      const handleQuickAdd = (value) => {
        const current = parseRawNumber(amountStr);
        setAmountStr((current + value).toString());
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
                  const newCats = CATEGORIES.filter(c => c.type === 'ALL' || c.type === newType);
                  if (!newCats.some(c => c.id === category)) {
                    setCategory(newCats[0].id);
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
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">Kategori</label>
                <div className="grid grid-cols-3 gap-2">
                  {filteredCategories.map(cat => (
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
                      <Icon name={cat.icon} className="w-5 h-5" />
                      <span className="text-[11px] leading-tight line-clamp-1">{cat.label}</span>
                    </button>
                  ))}
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

    const AccountsManagerModal = ({ isOpen, onClose, accounts, transactions, onAddAccount, onDeleteAccount, onEditAccount }) => {
      const [isAdding, setIsAdding] = useState(false);
      const [name, setName] = useState('');
      const [type, setType] = useState('Bank');
      const [initialBalance, setInitialBalance] = useState('');
      const [editingAcc, setEditingAcc] = useState(null);
      const [isClosing, setIsClosing] = useState(false);

      const safeAccounts = Array.isArray(accounts) ? accounts.filter(Boolean) : [];
      const safeTransactions = Array.isArray(transactions) ? transactions.filter(Boolean) : [];

      useEffect(() => {
        if (!isOpen) {
          setIsAdding(false);
          setEditingAcc(null);
          setName('');
          setInitialBalance('');
          setType('Bank');
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

      const handleSave = (e) => {
        e.preventDefault();
        const trimmed = (name || '').trim();
        if (!trimmed) return;
        const bal = parseRawNumber(initialBalance);

        if (editingAcc && editingAcc.id) {
          onEditAccount(editingAcc.id, { name: trimmed, type, initialBalance: bal });
          setEditingAcc(null);
        } else {
          const newAcc = {
            id: 'acc_' + Date.now(),
            name: trimmed,
            type,
            initialBalance: bal,
            createdAt: new Date().toISOString()
          };
          onAddAccount(newAcc);
        }

        setName('');
        setInitialBalance('');
        setType('Bank');
        setIsAdding(false);
      };

      const startEdit = (acc) => {
        setEditingAcc(acc);
        setName(acc.name || '');
        setType(acc.type || 'Bank');
        setInitialBalance(acc.initialBalance ? String(acc.initialBalance) : '0');
        setIsAdding(true);
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-slate-800 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'}`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="ios-modal-header px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-white dark:bg-slate-800">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Kelola Dompet & Akun</h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">Saldo sinkron otomatis dari mutasi</p>
              </div>
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

            <div className="ios-modal-body flex-1 overflow-y-auto pb-28 p-4 sm:p-5 space-y-4 no-scrollbar">
              {!isAdding ? (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      Daftar Dompet ({safeAccounts.length})
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setEditingAcc(null);
                        setName('');
                        setInitialBalance('');
                        setType('Bank');
                        setIsAdding(true);
                      }}
                      className="px-3 py-1.5 bg-sky-100 dark:bg-slate-700 text-brand dark:text-sky-300 text-xs font-semibold rounded-xl flex items-center gap-1 ios-btn-tap"
                    >
                      <Icon name="plus" className="w-4 h-4" />
                      <span>Tambah Dompet</span>
                    </button>
                  </div>

                  <div className="space-y-2">
                    {safeAccounts.map(acc => {
                      const bal = Ledger.getAccountBalance(acc.id, safeAccounts, safeTransactions);
                      return (
                        <div
                          key={acc.id}
                          className="p-3 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-700 flex items-center justify-between"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center text-brand">
                              <Icon name={acc.type === 'Bank' ? 'bank' : acc.type === 'Cash' ? 'cash' : 'smartphone'} className="w-5 h-5" />
                            </div>
                            <div>
                              <h4 className="text-xs font-bold text-slate-900 dark:text-white">{acc.name}</h4>
                              <span className="text-[11px] text-slate-500 dark:text-slate-400">{acc.type} • {formatIDR(bal)}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            <button
                              type="button"
                              onClick={() => startEdit(acc)}
                              className="p-1.5 text-slate-500 hover:text-brand rounded-lg ios-btn-tap"
                            >
                              <Icon name="edit" className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => onDeleteAccount(acc.id)}
                              className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg ios-btn-tap"
                            >
                              <Icon name="trash" className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              ) : (
                <form onSubmit={handleSave} className="space-y-3 bg-slate-50 dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-800 dark:text-white">
                      {editingAcc ? 'Edit Dompet' : 'Tambah Dompet'}
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setIsAdding(false);
                        setEditingAcc(null);
                      }}
                      className="text-xs text-slate-500 hover:underline"
                    >
                      Batal
                    </button>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Nama Dompet</label>
                    <input
                      type="text"
                      required
                      value={name}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Contoh: BCA / GoPay"
                      className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Kategori</label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'Cash', label: 'Tunai', icon: 'cash' },
                        { id: 'Bank', label: 'Bank', icon: 'bank' },
                        { id: 'E-Wallet', label: 'E-Wallet', icon: 'smartphone' }
                      ].map(item => (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => setType(item.id)}
                          className={`py-1.5 px-2 rounded-xl border text-xs font-medium flex items-center justify-center gap-1.5 ios-btn-tap ${
                            type === item.id
                              ? 'bg-sky-50 dark:bg-slate-700 border-brand text-brand dark:text-sky-400 font-bold'
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
                    <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">Saldo Awal (Rp)</label>
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
                      className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-2.5 bg-brand hover:bg-brand-hover text-white text-xs font-semibold rounded-xl transition-colors mt-2"
                  >
                    Simpan Dompet
                  </button>
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

    const SettingsModal = ({ isOpen, onClose, userProfile, onUpdateProfile, onHardReset, onImportData, onExportData, theme, onToggleTheme }) => {
      const [name, setName] = useState(userProfile.name || '');
      const [username, setUsername] = useState(userProfile.username || '');
      const [avatar, setAvatar] = useState(userProfile.avatar || '');
      const [isChangingPin, setIsChangingPin] = useState(false);
      const [currentPin, setCurrentPin] = useState('');
      const [newPin, setNewPin] = useState('');
      const [confirmPin, setConfirmPin] = useState('');
      const [pinMsg, setPinMsg] = useState({ text: '', isError: false });
      const [isClosing, setIsClosing] = useState(false);

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

              {/* Cadangan Data (JSON Backup & Restore) */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700 space-y-2">
                <h4 className="text-xs font-bold text-slate-900 dark:text-white">Cadangan & Pemulihan Offline</h4>
                <p className="text-[11px] text-slate-400">
                  Seluruh data disimpan 100% di perangkat kamu. Simpan cadangan JSON secara berkala.
                </p>
                <div className="flex gap-2 pt-1">
                  <button
                    type="button"
                    onClick={onExportData}
                    className="flex-1 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 ios-btn-tap"
                  >
                    <Icon name="download" className="w-4 h-4" />
                    <span>Ekspor JSON</span>
                  </button>
                  <label className="flex-1 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 text-slate-700 dark:text-slate-200 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 cursor-pointer ios-btn-tap">
                    <Icon name="upload" className="w-4 h-4" />
                    <span>Impor JSON</span>
                    <input type="file" accept=".json" className="hidden" onChange={handleFileImport} />
                  </label>
                </div>
              </div>

              {/* Profile / About Section with Brand Logo */}
              <div className="pt-4 border-t border-slate-100 dark:border-slate-700 flex flex-col items-center text-center space-y-1.5 select-none">
                <VoraletLogo size="md" className="mb-1" />
                <p className="text-[11px] font-bold text-slate-700 dark:text-slate-300">
                  Voralet iOS Edition • Versi __VORALET_VERSION__
                </p>
                <p className="text-[10px] text-slate-400 dark:text-slate-500 max-w-xs leading-relaxed">
                  Keuangan Sehat • Impian Dekat. 100% Offline & Terenkripsi Lokal di Perangkat Anda.
                </p>
              </div>

              {/* Reset Data */}
              <div className="pt-3 border-t border-slate-100 dark:border-slate-700">
                <button
                  type="button"
                  onClick={() => {
                    if (confirm('PERINGATAN: Semua data dompet, mutasi, hutang, dan PIN akan dihapus total dari perangkat ini. Lanjutkan?')) {
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
"""
