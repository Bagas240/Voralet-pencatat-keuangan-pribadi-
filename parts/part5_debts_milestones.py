PART5_DEBTS_MILESTONES = """
    // =========================================================================
    // 4. SAFE-TO-SPEND, QUICK SHORTCUTS & FINANCIAL MILESTONES
    // =========================================================================
    const SafeToSpendCard = ({ accounts, transactions, hideBalance, onSetBudget, safeBudget }) => {
      const [isEditingBudget, setIsEditingBudget] = useState(false);
      const [budgetInput, setBudgetInput] = useState('');

      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth();
      const totalDays = new Date(year, month + 1, 0).getDate();
      const currentDay = now.getDate();
      const daysRemaining = Math.max(1, totalDays - currentDay + 1);

      const totalLiquid = Ledger.getTotalBalance(accounts, transactions);
      const currentMonthTotals = useMemo(() => {
        const monthPrefix = `${year}-${String(month + 1).padStart(2, '0')}`;
        const thisMonthTx = (transactions || []).filter(t => t && t.date && t.date.startsWith(monthPrefix));
        return Ledger.getSummaryTotals(thisMonthTx);
      }, [transactions, year, month]);

      const effectiveBudget = safeBudget > 0 ? safeBudget : totalLiquid;
      const spentThisMonth = currentMonthTotals.expense;
      const remainingMonthBudget = Math.max(0, safeBudget > 0 ? (safeBudget - spentThisMonth) : totalLiquid);
      const dailyAllowance = Math.floor(remainingMonthBudget / daysRemaining);

      const handleSaveBudget = (e) => {
        e.preventDefault();
        const num = parseRawNumber(budgetInput);
        onSetBudget(num);
        setIsEditingBudget(false);
      };

      return (
        <div className="ios-inset-group mb-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <IconBadge icon="shield-check" className="p-1.5 rounded-xl bg-sky-100 dark:bg-slate-700 text-brand dark:text-sky-400" iconClass="w-4 h-4" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Safe-to-Spend Harian
              </span>
            </div>
            <button
              type="button"
              onClick={() => {
                setBudgetInput(safeBudget ? String(safeBudget) : '');
                setIsEditingBudget(true);
              }}
              className="text-[11px] font-semibold text-brand dark:text-sky-400 hover:underline flex items-center gap-1 ios-btn-tap"
            >
              <Icon name="edit" className="w-3 h-3" />
              <span>{safeBudget > 0 ? 'Atur Limit' : 'Pasang Limit'}</span>
            </button>
          </div>

          <div className="flex items-baseline justify-between mt-1">
            <div>
              <div className="text-xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {hideBalance ? 'Rp ••••••' : formatIDR(dailyAllowance)}
                <span className="text-xs font-normal text-slate-400 dark:text-slate-500 ml-1">/ hari</span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Sisa {daysRemaining} hari di bulan ini • Sisa dana {hideBalance ? 'Rp ••••••' : formatIDR(remainingMonthBudget)}
              </p>
            </div>
            <div className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
              dailyAllowance > 50000 ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border border-emerald-200/50' : 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 border border-amber-200/50'
            }`}>
              {dailyAllowance > 50000 ? 'Aman' : 'Hemat'}
            </div>
          </div>

          {isEditingBudget && (
            <form onSubmit={handleSaveBudget} className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700 flex gap-2">
              <input
                type="text"
                inputMode="numeric"
                value={budgetInput ? formatIDR(parseRawNumber(budgetInput)) : ''}
                onFocus={handleGlobalInputFocus}
                onBlur={handleGlobalInputBlur}
                onChange={(e) => setBudgetInput(parseRawNumber(e.target.value).toString())}
                placeholder="Limit belanja bulanan (Rp)"
                className="flex-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-medium text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                autoFocus
              />
              <button
                type="submit"
                className="px-3 py-1.5 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover ios-btn-tap"
              >
                Simpan
              </button>
              <button
                type="button"
                onClick={() => setIsEditingBudget(false)}
                className="px-2.5 py-1.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-medium rounded-xl ios-btn-tap"
              >
                Batal
              </button>
            </form>
          )}
        </div>
      );
    };

    // Quick Expense Presets
    const QuickExpenseBar = ({ onSelectQuickExpense }) => {
      const presets = [
        { label: 'Kopi', amount: 25000, category: 'makan', icon: 'food' },
        { label: 'Makan', amount: 35000, category: 'makan', icon: 'food' },
        { label: 'Bensin', amount: 50000, category: 'transport', icon: 'transport' },
        { label: 'Harian', amount: 100000, category: 'belanja', icon: 'shopping' }
      ];

      return (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2 px-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Pintas Cepat
            </span>
            <span className="text-[10px] text-slate-400">1-Tap Catat</span>
          </div>
          <div className="grid grid-cols-4 gap-2">
            {presets.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectQuickExpense(p)}
                className="p-2.5 rounded-[18px] bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/60 shadow-sm flex flex-col items-center text-center ios-btn-tap hover:border-brand/40 transition-all"
              >
                <div className="w-8 h-8 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400 flex items-center justify-center mb-1">
                  <Icon name={p.icon} className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold text-slate-800 dark:text-slate-200">{p.label}</span>
                <span className="text-[10px] text-slate-400 font-medium">Rp {p.amount / 1000}rb</span>
              </button>
            ))}
          </div>
        </div>
      );
    };

    // Financial Milestones & Achievement Badges
    const MilestonesCard = ({ transactions, savingsGoals, debts, totalBalance }) => {
      const [isOpen, setIsOpen] = useState(false);

      const milestones = useMemo(() => {
        const txCount = (transactions || []).length;
        const activeGoalsCount = (savingsGoals || []).length;
        const unpaidDebts = (debts || []).filter(d => d.status !== 'LUNAS' && d.type === 'HUTANG').length;

        return [
          {
            id: 'first_tx',
            title: 'Pencatat Aktif',
            desc: 'Catat minimal 5 mutasi',
            icon: 'award',
            unlocked: txCount >= 5,
            progress: `${Math.min(txCount, 5)}/5`
          },
          {
            id: 'discipline',
            title: 'Disiplin Keuangan',
            desc: 'Catat 15 mutasi keuangan',
            icon: 'shield-check',
            unlocked: txCount >= 15,
            progress: `${Math.min(txCount, 15)}/15`
          },
          {
            id: 'dreamer',
            title: 'Pemburu Impian',
            desc: 'Buat target kantong impian',
            icon: 'target',
            unlocked: activeGoalsCount >= 1,
            progress: `${Math.min(activeGoalsCount, 1)}/1`
          },
          {
            id: 'debt_free',
            title: 'Bebas Beban Hutang',
            desc: 'Nol hutang belum lunas',
            icon: 'check-circle',
            unlocked: unpaidDebts === 0 && (debts || []).length > 0,
            progress: unpaidDebts === 0 ? 'Lunas' : `${unpaidDebts} Hutang`
          },
          {
            id: 'wealth',
            title: 'Sultan Muda',
            desc: 'Total saldo > Rp 1.000.000',
            icon: 'zap',
            unlocked: totalBalance >= 1000000,
            progress: totalBalance >= 1000000 ? 'Tercapai' : `${Math.floor((totalBalance / 1000000) * 100)}%`
          }
        ];
      }, [transactions, savingsGoals, debts, totalBalance]);

      const unlockedCount = milestones.filter(m => m.unlocked).length;

      return (
        <div className="ios-inset-group mb-4">
          <div
            className="flex items-center justify-between cursor-pointer ios-touch-item"
            onClick={() => setIsOpen(prev => !prev)}
          >
            <div className="flex items-center gap-2">
              <IconBadge icon="award" className="p-1.5 rounded-xl bg-amber-50 dark:bg-slate-700 text-amber-500" iconClass="w-4 h-4" />
              <div>
                <h3 className="text-xs font-bold text-slate-900 dark:text-white">Milestone Keuangan</h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  {unlockedCount} dari {milestones.length} lencana tercapai
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-16 h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-brand transition-all duration-300"
                  style={{ width: `${(unlockedCount / milestones.length) * 100}%` }}
                />
              </div>
              <span className="text-xs font-bold text-brand">{Math.round((unlockedCount / milestones.length) * 100)}%</span>
            </div>
          </div>

          {isOpen && (
            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700 space-y-2">
              {milestones.map(m => (
                <div
                  key={m.id}
                  className={`p-2.5 rounded-xl flex items-center justify-between ${
                    m.unlocked
                      ? 'bg-sky-50 dark:bg-slate-700/60 border border-sky-100 dark:border-slate-700'
                      : 'bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 opacity-70'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      m.unlocked ? 'bg-brand text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-400'
                    }`}>
                      <Icon name={m.icon} className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">{m.title}</h4>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400">{m.desc}</p>
                    </div>
                  </div>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    m.unlocked ? 'bg-sky-100 dark:bg-slate-600 text-brand dark:text-sky-300' : 'bg-slate-200 dark:bg-slate-700 text-slate-500'
                  }`}>
                    {m.progress}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    };

    // =========================================================================
    // 5. DEBT & LOAN TRACKER (HUTANG & PIUTANG VIEW + MODAL)
    // =========================================================================
    const DebtModal = ({ isOpen, onClose, debtToEdit, onSaveDebt }) => {
      const [type, setType] = useState('HUTANG'); // HUTANG (Saya berhutang) | PIUTANG (Orang lain berhutang)
      const [personName, setPersonName] = useState('');
      const [amountStr, setAmountStr] = useState('');
      const [dueDate, setDueDate] = useState('');
      const [notes, setNotes] = useState('');
      const [isClosing, setIsClosing] = useState(false);

      useEffect(() => {
        if (debtToEdit) {
          setType(debtToEdit.type || 'HUTANG');
          setPersonName(debtToEdit.personName || '');
          setAmountStr(debtToEdit.amount ? String(debtToEdit.amount) : '');
          setDueDate(debtToEdit.dueDate || '');
          setNotes(debtToEdit.notes || '');
        } else {
          setType('HUTANG');
          setPersonName('');
          setAmountStr('');
          setDueDate('');
          setNotes('');
        }
      }, [debtToEdit, isOpen]);

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
        const rawAmt = parseRawNumber(amountStr);
        if (!personName.trim() || rawAmt <= 0) return;

        const debtData = {
          id: debtToEdit ? debtToEdit.id : ('debt_' + Date.now()),
          type,
          personName: personName.trim(),
          amount: rawAmt,
          dueDate: dueDate || '',
          notes: notes.trim(),
          status: debtToEdit ? debtToEdit.status : 'BELUM_LUNAS',
          createdAt: debtToEdit ? debtToEdit.createdAt : new Date().toISOString()
        };

        onSaveDebt(debtData);
        handleClose();
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-slate-800 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'}`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="ios-modal-header px-5 py-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between bg-white dark:bg-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                {debtToEdit ? 'Edit Catatan' : 'Catat Hutang / Piutang'}
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
              <div className="grid grid-cols-2 p-1 bg-slate-100 dark:bg-slate-900 rounded-xl">
                <button
                  type="button"
                  onClick={() => setType('HUTANG')}
                  className={`py-2 rounded-lg text-xs font-semibold transition-all ios-btn-tap ${
                    type === 'HUTANG'
                      ? 'bg-white dark:bg-slate-800 text-rose-600 dark:text-rose-400 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Saya Berhutang
                </button>
                <button
                  type="button"
                  onClick={() => setType('PIUTANG')}
                  className={`py-2 rounded-lg text-xs font-semibold transition-all ios-btn-tap ${
                    type === 'PIUTANG'
                      ? 'bg-white dark:bg-slate-800 text-emerald-600 dark:text-emerald-400 shadow-sm'
                      : 'text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Orang Berhutang (Piutang)
                </button>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Nama Kontak / Orang
                </label>
                <input
                  type="text"
                  required
                  value={personName}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => setPersonName(e.target.value)}
                  placeholder="Contoh: Rian / Bu Ani"
                  className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                  autoFocus
                />
              </div>

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
                  }}
                  placeholder="Rp 0"
                  className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-base font-bold text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Jatuh Tempo (Opsional)</label>
                  <input
                    type="date"
                    value={dueDate}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Catatan</label>
                  <input
                    type="text"
                    value={notes}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Contoh: Talangan makan siang"
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-3 bg-[#0284C7] hover:bg-[#0369A1] text-white font-semibold text-sm rounded-xl transition-colors shadow-sm ios-btn-tap"
                >
                  {debtToEdit ? 'Simpan Perubahan' : 'Catat'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    const DebtsView = ({ debts, onAddDebt, onToggleStatus, onDeleteDebt, hideBalance, onEditDebt, onModalChange }) => {
      const [filterTab, setFilterTab] = useState('ALL'); // ALL | HUTANG | PIUTANG
      const [isModalOpen, setIsModalOpen] = useState(false);
      const [selectedDebt, setSelectedDebt] = useState(null);

      useEffect(() => {
        if (typeof onModalChange === 'function') {
          onModalChange(isModalOpen);
        }
      }, [isModalOpen, onModalChange]);

      const safeDebts = Array.isArray(debts) ? debts : [];

      const totals = useMemo(() => {
        let totalHutang = 0;
        let totalPiutang = 0;
        safeDebts.forEach(d => {
          if (d.status !== 'LUNAS') {
            const amt = Number(d.amount) || 0;
            if (d.type === 'HUTANG') totalHutang += amt;
            else totalPiutang += amt;
          }
        });
        return { totalHutang, totalPiutang, net: totalPiutang - totalHutang };
      }, [safeDebts]);

      const filteredList = useMemo(() => {
        if (filterTab === 'ALL') return safeDebts;
        return safeDebts.filter(d => d.type === filterTab);
      }, [safeDebts, filterTab]);

      return (
        <div className="space-y-4 pb-28 animate-ios-tab-view">
          {/* Page Title & Add Button */}
          <div className="flex items-center justify-between pt-1">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">Hutang & Piutang</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Kelola pinjaman dan jatuh tempo</p>
            </div>
            <button
              type="button"
              onClick={() => {
                setSelectedDebt(null);
                setIsModalOpen(true);
              }}
              className="px-4 py-2.5 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-2xl flex items-center gap-2 shadow-sm transition-all ios-btn-tap"
            >
              <Icon name="plus" className="w-4 h-4" strokeWidth={2.4} />
              <span>Catat Baru</span>
            </button>
          </div>

          {/* Header Summary */}
          <div className="grid grid-cols-2 gap-3">
            <div className="ios-inset-group">
              <span className="text-[10px] font-bold uppercase tracking-wider text-rose-500 block mb-1">
                Hutang Saya (Belum Lunas)
              </span>
              <div className="text-lg font-bold text-slate-900 dark:text-white">
                {hideBalance ? 'Rp ••••••' : formatIDR(totals.totalHutang)}
              </div>
            </div>
            <div className="ios-inset-group">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-500 block mb-1">
                Piutang Saya (Dipinjam)
              </span>
              <div className="text-lg font-bold text-slate-900 dark:text-white">
                {hideBalance ? 'Rp ••••••' : formatIDR(totals.totalPiutang)}
              </div>
            </div>
          </div>

          {/* Action Bar & Filter */}
          <div className="flex items-center justify-between gap-2">
            <div className="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl text-xs font-semibold">
              {['ALL', 'HUTANG', 'PIUTANG'].map(tab => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setFilterTab(tab)}
                  className={`px-3.5 py-1.5 rounded-lg transition-colors ios-btn-tap ${
                    filterTab === tab
                      ? 'bg-white dark:bg-slate-700 text-brand dark:text-white shadow-sm font-bold'
                      : 'text-slate-500 dark:text-slate-400'
                  }`}
                >
                  {tab === 'ALL' ? 'Semua' : tab === 'HUTANG' ? 'Hutang' : 'Piutang'}
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={() => {
                setSelectedDebt(null);
                setIsModalOpen(true);
              }}
              className="px-3 py-1.5 bg-sky-50 dark:bg-slate-800 text-brand dark:text-sky-400 text-xs font-bold rounded-xl border border-sky-200/60 dark:border-slate-700 flex items-center gap-1.5 shadow-sm ios-btn-tap hover:bg-sky-100"
            >
              <Icon name="plus" className="w-3.5 h-3.5" />
              <span>Tambah</span>
            </button>
          </div>

          {/* Debt List */}
          {filteredList.length === 0 ? (
            <div className="ios-inset-group text-center py-10">
              <IconBadge icon="receipt" className="w-14 h-14 rounded-2xl bg-sky-50 dark:bg-slate-800 text-brand mx-auto mb-3" iconClass="w-7 h-7" />
              <h3 className="text-sm font-bold text-slate-800 dark:text-white">Belum Ada Catatan Hutang / Piutang</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xs mx-auto mb-4">
                Catat pinjaman pribadi atau uang yang sedang dipinjam rekan agar tertata rapi.
              </p>
              <button
                type="button"
                onClick={() => {
                  setSelectedDebt(null);
                  setIsModalOpen(true);
                }}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-xl shadow-sm transition-colors ios-btn-tap mx-auto"
              >
                <Icon name="plus" className="w-4 h-4" />
                <span>Mulai Buat Catatan</span>
              </button>
            </div>
          ) : (
            <div className="ios-inset-group space-y-3">
              {filteredList.map((item, idx) => (
                <div
                  key={item.id}
                  className={`flex items-center justify-between pb-3 ${idx !== filteredList.length - 1 ? 'ios-hairline' : ''}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 ${
                      item.type === 'HUTANG'
                        ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400'
                        : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400'
                    }`}>
                      <Icon name={item.type === 'HUTANG' ? 'arrow-up-right' : 'arrow-down-left'} className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900 dark:text-white">{item.personName}</span>
                        <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded-full ${
                          item.status === 'LUNAS'
                            ? 'bg-slate-100 dark:bg-slate-700 text-slate-500'
                            : item.type === 'HUTANG'
                              ? 'bg-rose-100 dark:bg-rose-900/50 text-rose-700 dark:text-rose-300'
                              : 'bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300'
                        }`}>
                          {item.status === 'LUNAS' ? 'LUNAS' : item.type === 'HUTANG' ? 'HUTANG' : 'PIUTANG'}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        {item.notes ? item.notes : 'Tanpa keterangan'}
                        {item.dueDate && ` • Tempo: ${formatDateID(item.dueDate)}`}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <div className={`text-xs font-bold ${
                        item.type === 'HUTANG' ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'
                      }`}>
                        {hideBalance ? 'Rp ••••••' : formatIDR(item.amount)}
                      </div>
                      <button
                        type="button"
                        onClick={() => onToggleStatus(item.id)}
                        className="text-[10px] font-semibold text-brand dark:text-sky-400 hover:underline"
                      >
                        {item.status === 'LUNAS' ? 'Tandai Belum' : 'Tandai Lunas'}
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => onDeleteDebt(item.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg ios-btn-tap"
                      title="Hapus"
                    >
                      <Icon name="trash" className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {isModalOpen && (
            <DebtModal
              isOpen={isModalOpen}
              debtToEdit={selectedDebt}
              onClose={() => setIsModalOpen(false)}
              onSaveDebt={(data) => {
                onAddDebt(data);
                setIsModalOpen(false);
              }}
            />
          )}
        </div>
      );
    };
"""
