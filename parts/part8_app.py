PART8_APP = """
    // =========================================================================
    // 9. SWIPEABLE TRANSACTION ROW & CONTEXTUAL LONG PRESS
    // =========================================================================
    const SwipeableTransactionRow = ({
      tx,
      idx,
      isLast,
      cat,
      acc,
      hideBalance,
      onDelete,
      onEdit,
      onDuplicate,
      isNewlyAdded = false,
      isDeleting = false,
      onClearNewlyAdded
    }) => {
      const [offsetX, setOffsetX] = useState(0);
      const [isDragging, setIsDragging] = useState(false);
      const startX = useRef(0);
      const startY = useRef(0);
      const longPressTimer = useRef(null);
      const [isMenuOpen, setIsMenuOpen] = useState(false);

      const handleTouchStart = (e) => {
        startX.current = e.touches[0].clientX;
        startY.current = e.touches[0].clientY;
        setIsDragging(false);

        // Long press detection (500ms)
        longPressTimer.current = setTimeout(() => {
          setIsMenuOpen(true);
        }, 500);
      };

      const handleTouchMove = (e) => {
        const diffX = e.touches[0].clientX - startX.current;
        const diffY = e.touches[0].clientY - startY.current;

        // If moved more than 8px, cancel long press
        if (Math.abs(diffX) > 8 || Math.abs(diffY) > 8) {
          clearTimeout(longPressTimer.current);
        }

        // Only drag horizontally if diffX > diffY
        if (Math.abs(diffX) > Math.abs(diffY)) {
          setIsDragging(true);
          // Limit drag between -80 (delete) and 80 (edit)
          const clamped = Math.max(-80, Math.min(80, diffX));
          setOffsetX(clamped);
        }
      };

      const handleTouchEnd = () => {
        clearTimeout(longPressTimer.current);
        if (offsetX < -45) {
          // Revealed delete
          setOffsetX(-70);
        } else if (offsetX > 45) {
          // Revealed edit
          setOffsetX(70);
        } else {
          setOffsetX(0);
        }
        setIsDragging(false);
      };

      return (
        <div
          className={`relative overflow-hidden select-none transition-all duration-300 ease-out ${
            isNewlyAdded ? 'animate-tx-slide-in rounded-2xl' : ''
          } ${isDeleting ? 'animate-tx-fade-out' : ''}`}
          onAnimationEnd={(e) => {
            if (e.target === e.currentTarget && isNewlyAdded && onClearNewlyAdded) {
              onClearNewlyAdded(tx.id);
            }
          }}
        >
          {/* Background Swipe Actions */}
          <div className="absolute inset-0 flex items-center justify-between pointer-events-auto">
            {/* Swipe Right Action: Edit */}
            <button
              type="button"
              onClick={() => {
                setOffsetX(0);
                onEdit(tx);
              }}
              className="w-16 h-full bg-brand text-white flex flex-col items-center justify-center text-[10px] font-bold rounded-l-xl ios-btn-tap"
            >
              <Icon name="edit" className="w-4 h-4 mb-0.5" />
              <span>Edit</span>
            </button>

            {/* Swipe Left Action: Delete */}
            <button
              type="button"
              onClick={() => {
                setOffsetX(0);
                onDelete(tx.id);
              }}
              className="w-16 h-full bg-rose-600 text-white flex flex-col items-center justify-center text-[10px] font-bold rounded-r-xl ios-btn-tap"
            >
              <Icon name="trash" className="w-4 h-4 mb-0.5" />
              <span>Hapus</span>
            </button>
          </div>

          {/* Foreground Row */}
          <div
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
            onClick={() => {
              if (offsetX !== 0) setOffsetX(0);
            }}
            style={{
              transform: `translate3d(${offsetX}px, 0, 0)`,
              transition: isDragging ? 'none' : 'transform 0.25s cubic-bezier(0.32, 0.72, 0, 1)'
            }}
            className={`relative bg-white dark:bg-slate-800 flex items-center justify-between py-3 px-1.5 ${!isLast ? 'ios-hairline' : ''} ios-touch-item`}
          >
            <div className="flex items-center gap-3 min-w-0 pointer-events-none">
              <div className="relative shrink-0">
                <IconBadge icon={cat.icon} className="p-2.5 rounded-2xl bg-sky-100 dark:bg-slate-700 text-brand dark:text-sky-400 shrink-0" />
                <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-white border-2 border-white dark:border-slate-800 ${
                  tx.type === 'EXPENSE' ? 'bg-rose-500' : 'bg-emerald-500'
                }`}>
                  <Icon name={tx.type === 'EXPENSE' ? 'arrow-up-right' : 'arrow-down-left'} className="w-2.5 h-2.5" strokeWidth={3} />
                </div>
              </div>
              <div className="min-w-0">
                <h4 className="text-xs font-bold text-slate-900 dark:text-white truncate">
                  {cat.label}
                </h4>
                <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                  <span>{formatDateID(tx.date)}</span>
                  {acc && (
                    <>
                      <span>•</span>
                      <span className="text-slate-500 dark:text-slate-400 font-medium">{acc.name}</span>
                    </>
                  )}
                  {tx.notes && (
                    <>
                      <span>•</span>
                      <span className="truncate italic max-w-[130px]">{tx.notes}</span>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span className={`text-xs whitespace-nowrap truncate font-bold ${
                tx.type === 'EXPENSE' ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'
              }`}>
                {tx.type === 'EXPENSE' ? '-' : '+'}
                {hideBalance ? 'Rp ••••••' : formatIDR(tx.amount)}
              </span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsMenuOpen(true);
                }}
                className="p-1.5 text-slate-300 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg ios-btn-tap"
                title="Pilihan"
              >
                <Icon name="more-horizontal" className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Contextual Long-Press / More Menu */}
          <ContextualMenuModal
            isOpen={isMenuOpen && !isDeleting}
            title={`${cat.label} - ${formatIDR(tx.amount)}`}
            onClose={() => setIsMenuOpen(false)}
            onEdit={() => onEdit(tx)}
            onDuplicate={() => onDuplicate(tx)}
            onDelete={() => onDelete(tx.id)}
          />
        </div>
      );
    };

    // =========================================================================
    // 10. MAIN DASHBOARD
    // =========================================================================
    const MainDashboard = React.memo(({
      accounts,
      transactions,
      userProfile,
      hideBalance,
      onToggleHideBalance,
      onOpenAddTx,
      onOpenAddIncome,
      onOpenAddExpense,
      onOpenAccounts,
      onOpenSettings,
      onOpenDebts,
      onOpenSavings,
      onOpenNewSavingsGoal,
      onDeleteTx,
      onEditTx,
      onDuplicateTx,
      safeBudget,
      onSetBudget,
      savingsGoals,
      debts,
      onSelectQuickExpense,
      customCategories = [],
      onSelectTab,
      onOpenCsvImport,
      deletingTxIds = new Set(),
      newlyAddedTxIds = new Set(),
      onClearNewlyAddedTx
    }) => {
      const [searchQuery, setSearchQuery] = useState('');
      const [filterType, setFilterType] = useState('ALL'); // ALL | EXPENSE | INCOME
      const [selectedAccountFilter, setSelectedAccountFilter] = useState('ALL');
      const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('ALL');
      const [startDate, setStartDate] = useState('');
      const [endDate, setEndDate] = useState('');
      const [datePreset, setDatePreset] = useState('ALL'); // ALL | TODAY | THIS_WEEK | THIS_MONTH | LAST_MONTH | CUSTOM
      const [isDateFilterOpen, setIsDateFilterOpen] = useState(false);

      const applyDatePreset = (preset) => {
        setDatePreset(preset);
        const now = new Date();
        if (preset === 'ALL') {
          setStartDate('');
          setEndDate('');
        } else if (preset === 'TODAY') {
          const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
          setStartDate(todayStr);
          setEndDate(todayStr);
        } else if (preset === 'THIS_WEEK') {
          const day = now.getDay(); // 0 is Sunday, 1 is Monday...
          const diffToMon = (day === 0 ? -6 : 1) - day;
          const mon = new Date(now.getFullYear(), now.getMonth(), now.getDate() + diffToMon);
          const sun = new Date(mon.getFullYear(), mon.getMonth(), mon.getDate() + 6);
          const monStr = `${mon.getFullYear()}-${String(mon.getMonth() + 1).padStart(2, '0')}-${String(mon.getDate()).padStart(2, '0')}`;
          const sunStr = `${sun.getFullYear()}-${String(sun.getMonth() + 1).padStart(2, '0')}-${String(sun.getDate()).padStart(2, '0')}`;
          setStartDate(monStr);
          setEndDate(sunStr);
        } else if (preset === 'THIS_MONTH') {
          const y = now.getFullYear();
          const m = now.getMonth();
          const firstDay = `${y}-${String(m + 1).padStart(2, '0')}-01`;
          const lastDate = new Date(y, m + 1, 0).getDate();
          const lastDay = `${y}-${String(m + 1).padStart(2, '0')}-${String(lastDate).padStart(2, '0')}`;
          setStartDate(firstDay);
          setEndDate(lastDay);
        } else if (preset === 'LAST_MONTH') {
          const y = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
          const m = now.getMonth() === 0 ? 11 : now.getMonth() - 1;
          const firstDay = `${y}-${String(m + 1).padStart(2, '0')}-01`;
          const lastDate = new Date(y, m + 1, 0).getDate();
          const lastDay = `${y}-${String(m + 1).padStart(2, '0')}-${String(lastDate).padStart(2, '0')}`;
          setStartDate(firstDay);
          setEndDate(lastDay);
        }
      };

      const hasActiveDateFilter = Boolean(startDate || endDate || datePreset !== 'ALL');

      const allCategories = useMemo(() => {
        return getAllCategories(customCategories);
      }, [customCategories]);

      const safeAccounts = useMemo(() => Array.isArray(accounts) ? accounts.filter(Boolean) : [], [accounts]);
      const safeTransactions = useMemo(() => Array.isArray(transactions) ? transactions.filter(Boolean) : [], [transactions]);

      const totalBalance = useMemo(() => {
        return Ledger.getTotalBalance(safeAccounts, safeTransactions);
      }, [safeAccounts, safeTransactions]);

      const monthSummary = useMemo(() => {
        const now = new Date();
        const prefix = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        const thisMonthTx = safeTransactions.filter(t => t && t.date && t.date.startsWith(prefix));
        return Ledger.getSummaryTotals(thisMonthTx);
      }, [safeTransactions]);

      // Pre-calculated account balances map for instant lookup without O(N) recalculations
      const accountBalancesMap = useMemo(() => {
        const map = new Map();
        for (const acc of safeAccounts) {
          map.set(acc.id, Ledger.getAccountBalance(acc.id, safeAccounts, safeTransactions));
        }
        return map;
      }, [safeAccounts, safeTransactions]);

      // Filtered transactions with date-range support
      const filteredTransactions = useMemo(() => {
        return safeTransactions.filter(tx => {
          if (!tx) return false;
          if (filterType !== 'ALL' && tx.type !== filterType) return false;
          if (selectedAccountFilter !== 'ALL' && tx.accountId !== selectedAccountFilter) return false;
          if (selectedCategoryFilter !== 'ALL' && tx.category !== selectedCategoryFilter) return false;
          if (startDate) {
            const txDate = (tx.date || '').slice(0, 10);
            if (txDate && txDate < startDate) return false;
          }
          if (endDate) {
            const txDate = (tx.date || '').slice(0, 10);
            if (txDate && txDate > endDate) return false;
          }
          if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            const catObj = allCategories.find(c => c.id === tx.category);
            const cat = (catObj?.label || '').toLowerCase();
            const notes = (tx.notes || '').toLowerCase();
            const amt = String(tx.amount || '');
            if (!cat.includes(q) && !notes.includes(q) && !amt.includes(q)) return false;
          }
          return true;
        });
      }, [safeTransactions, filterType, selectedAccountFilter, selectedCategoryFilter, startDate, endDate, searchQuery, allCategories]);

      return (
        <div className="space-y-4 pb-28">
          {/* iOS Profile Header Bar - Compact & Natural without elongated box */}
          <div className="flex items-center justify-between pt-1">
            <div
              onClick={onOpenSettings}
              className="inline-flex items-center gap-3 cursor-pointer group ios-card-tap py-1 pr-2 rounded-2xl hover:opacity-90 transition-opacity"
              title="Ketuk untuk buka Pengaturan Profil"
            >
              {/* Profile Avatar with clean circular drop shadow so it stands out distinctly from the background */}
              <div className="relative shrink-0 rounded-full shadow-[0_6px_16px_rgba(15,23,42,0.18)] dark:shadow-[0_8px_24px_rgba(0,0,0,0.65)] ring-2 ring-white dark:ring-slate-700">
                <Avatar avatar={userProfile.avatar} name={userProfile.name} size="w-11 h-11" textSize="text-base" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <h1 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-tight group-hover:text-brand transition-colors truncate">
                    {userProfile.name || 'Sahabat Voralet'}
                  </h1>
                  <Icon name="chevron-right" className="w-3.5 h-3.5 text-slate-400 group-hover:text-brand transition-colors shrink-0" />
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-[11px] font-mono text-brand dark:text-sky-400 font-semibold truncate">
                    @{userProfile.username || 'voralet_user'}
                  </p>
                  <span className="text-[10px] font-bold px-1.5 py-0.2 rounded-md bg-sky-100 dark:bg-sky-950/60 text-[#0284C7] dark:text-sky-400 border border-sky-200/60 dark:border-sky-800/60">
                    v__VORALET_VERSION__
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Hero Balance Card - High Contrast Deep Royal Blue in both Light and Dark Mode */}
          <div className="rounded-[22px] p-5 bg-[#0284C7] dark:bg-[#0369A1] text-white border border-[#0369A1] dark:border-sky-600/40 shadow-lg dark:shadow-[0_10px_26px_rgba(3,105,161,0.35)] transition-colors duration-300 ease-in-out">
            <div className="flex items-center justify-between text-sky-100 mb-1.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-sky-100">Total Saldo Brankas</span>
              <button
                type="button"
                onClick={onToggleHideBalance}
                className="p-1 text-sky-100 hover:text-white transition-colors ios-btn-tap"
                aria-label="Sensor Saldo"
              >
                <Icon name={hideBalance ? 'eye-off' : 'eye'} className="w-4 h-4 text-sky-100" />
              </button>
            </div>

            <div className="text-2xl whitespace-nowrap truncate font-extrabold tracking-tight mb-4 text-white">
              {hideBalance ? 'Rp ••••••••' : formatIDR(totalBalance)}
            </div>

            {/* Monthly income and expense summary */}
            <div className="grid grid-cols-2 gap-2 pt-3 border-t border-sky-400/50 dark:border-sky-500/40">
              <div className="flex items-center gap-2.5 p-1.5 rounded-xl">
                <div className="w-8 h-8 rounded-xl bg-emerald-500/30 text-emerald-100 flex items-center justify-center shrink-0 border border-emerald-300/30">
                  <Icon name="arrow-down-left" className="w-4 h-4 text-emerald-200" strokeWidth={2.5} />
                </div>
                <div className="min-w-0">
                  <span className="text-[10px] text-sky-100 block leading-tight font-medium">Masuk (Bln Ini)</span>
                  <span className="text-xs whitespace-nowrap truncate font-bold text-white block">
                    {hideBalance ? 'Rp ••••••' : formatIDR(monthSummary.income)}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2.5 p-1.5 rounded-xl">
                <div className="w-8 h-8 rounded-xl bg-rose-500/30 text-rose-100 flex items-center justify-center shrink-0 border border-rose-300/30">
                  <Icon name="arrow-up-right" className="w-4 h-4 text-rose-200" strokeWidth={2.5} />
                </div>
                <div className="min-w-0">
                  <span className="text-[10px] text-sky-100 block leading-tight font-medium">Keluar (Bln Ini)</span>
                  <span className="text-xs whitespace-nowrap truncate font-bold text-white block">
                    {hideBalance ? 'Rp ••••••' : formatIDR(monthSummary.expense)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Direct Dual Action Bar: Catat Pemasukan (+) & Catat Pengeluaran (-) with Prominent Icons */}
          <div className="grid grid-cols-2 gap-2.5">
            <button
              type="button"
              onClick={onOpenAddIncome}
              className="py-3 px-3 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.98] text-white rounded-2xl flex items-center justify-center gap-2 shadow-[0_4px_14px_rgba(5,150,105,0.28)] dark:shadow-[0_6px_20px_rgba(5,150,105,0.35)] transition-all ios-btn-tap"
            >
              <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                <Icon name="arrow-down-left" className="w-4 h-4 text-white" strokeWidth={2.5} />
              </div>
              <div className="text-left leading-tight">
                <span className="text-xs font-bold block">Pemasukan</span>
                <span className="text-[10px] text-emerald-100 block font-medium">+ Catat Masuk</span>
              </div>
            </button>

            <button
              type="button"
              onClick={onOpenAddExpense}
              className="py-3 px-3 bg-rose-600 hover:bg-rose-700 active:scale-[0.98] text-white rounded-2xl flex items-center justify-center gap-2 shadow-[0_4px_14px_rgba(225,29,72,0.28)] dark:shadow-[0_6px_20px_rgba(225,29,72,0.35)] transition-all ios-btn-tap"
            >
              <div className="w-7 h-7 rounded-full bg-white/20 flex items-center justify-center shrink-0">
                <Icon name="arrow-up-right" className="w-4 h-4 text-white" strokeWidth={2.5} />
              </div>
              <div className="text-left leading-tight">
                <span className="text-xs font-bold block">Pengeluaran</span>
                <span className="text-[10px] text-rose-100 block font-medium">- Catat Belanja</span>
              </div>
            </button>
          </div>

          {/* Safe-to-Spend Indicator */}
          <SafeToSpendCard
            accounts={safeAccounts}
            transactions={safeTransactions}
            hideBalance={hideBalance}
            safeBudget={safeBudget}
            onSetBudget={onSetBudget}
          />

          {/* Quick Expense Bar */}
          <QuickExpenseBar onSelectQuickExpense={onSelectQuickExpense} />

          {/* Kantong Impian Quick Section */}
          <div className="ios-inset-group">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <IconBadge icon="target" className="p-1.5 rounded-xl bg-emerald-100 dark:bg-slate-700 text-emerald-600 dark:text-emerald-400" iconClass="w-4 h-4" />
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white">Kantong Impian</h3>
                  <p className="text-[10px] text-slate-400">Target & tabungan masa depan</p>
                </div>
              </div>
              <button
                type="button"
                onClick={onOpenNewSavingsGoal}
                className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold rounded-xl flex items-center gap-1 shadow-sm ios-btn-tap"
              >
                <Icon name="plus" className="w-3.5 h-3.5" strokeWidth={2.5} />
                <span>+ Tambah Kantong</span>
              </button>
            </div>

            {savingsGoals && savingsGoals.length > 0 ? (
              <div className="space-y-2.5">
                {savingsGoals.slice(0, 3).map(goal => {
                  const target = Number(goal.targetAmount) || 1;
                  const current = Number(goal.currentAmount) || 0;
                  const pct = Math.min(100, Math.round((current / target) * 100));
                  return (
                    <div
                      key={goal.id}
                      onClick={onOpenSavings}
                      className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/70 border border-slate-100 dark:border-slate-800 cursor-pointer hover:border-emerald-500/40 transition-all ios-card-tap"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">{goal.title}</span>
                        <span className="text-[11px] font-bold text-emerald-600 dark:text-emerald-400">{pct}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden mb-1">
                        <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${pct}%` }} />
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-400">
                        <span>{hideBalance ? 'Rp ••••••' : formatIDR(current)}</span>
                        <span>Target: {hideBalance ? 'Rp ••••••' : formatIDR(target)}</span>
                      </div>
                    </div>
                  );
                })}
                {savingsGoals.length > 3 && (
                  <button
                    type="button"
                    onClick={onOpenSavings}
                    className="w-full text-center text-[11px] font-semibold text-brand dark:text-sky-400 pt-1 hover:underline"
                  >
                    Lihat semua {savingsGoals.length} Kantong Impian →
                  </button>
                )}
              </div>
            ) : (
              <div className="text-center py-4 px-2 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-dashed border-slate-200 dark:border-slate-800">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2.5">
                  Kamu belum memiliki Kantong Impian
                </p>
                <button
                  type="button"
                  onClick={onOpenNewSavingsGoal}
                  className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl inline-flex items-center gap-1.5 shadow-sm ios-btn-tap"
                >
                  <Icon name="plus" className="w-3.5 h-3.5" strokeWidth={2.5} />
                  <span>+ Buat Kantong Impian Sekarang</span>
                </button>
              </div>
            )}
          </div>

          {/* Financial Milestones */}
          <MilestonesCard
            transactions={safeTransactions}
            savingsGoals={savingsGoals}
            debts={debts}
            totalBalance={totalBalance}
          />

          {/* Transactions List with Smart Filter */}
          <div className="ios-inset-group">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Riwayat Mutasi ({filteredTransactions.length})
              </h3>
              {safeAccounts.length > 1 && (
                <select
                  value={selectedAccountFilter}
                  onFocus={handleGlobalInputFocus}
                  onBlur={handleGlobalInputBlur}
                  onChange={(e) => setSelectedAccountFilter(e.target.value)}
                  className="px-2 py-1 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-[11px] font-semibold text-slate-700 dark:text-slate-300 focus:outline-none"
                >
                  <option value="ALL">Semua Dompet</option>
                  {safeAccounts.map(a => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
                </select>
              )}
            </div>

            {/* Live Search & Date Range Filter */}
            <div className="space-y-2 mb-3">
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                    <Icon name="search" className="w-3.5 h-3.5" />
                  </span>
                  <input
                    type="text"
                    value={searchQuery}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Cari transaksi atau catatan..."
                    className="w-full pl-8 pr-8 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                  />
                  {searchQuery && (
                    <button
                      type="button"
                      onClick={() => setSearchQuery('')}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-0.5"
                    >
                      <Icon name="x" className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {/* Date-Range Filter Toggle Button */}
                <button
                  type="button"
                  onClick={() => setIsDateFilterOpen(!isDateFilterOpen)}
                  className={`relative p-2 rounded-xl border flex items-center justify-center transition-all ios-btn-tap shrink-0 ${
                    hasActiveDateFilter
                      ? 'bg-brand text-white border-brand shadow-sm'
                      : isDateFilterOpen
                        ? 'bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 border-slate-300 dark:border-slate-600'
                        : 'bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-brand/40'
                  }`}
                  title="Filter Rentang Tanggal"
                  aria-label="Filter Rentang Tanggal"
                >
                  <Icon name="calendar" className="w-4 h-4" strokeWidth={2.2} />
                  {hasActiveDateFilter && (
                    <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-amber-400 border-2 border-white dark:border-slate-800 rounded-full" />
                  )}
                </button>

                {/* CSV Import Quick Action Button */}
                {onOpenCsvImport && (
                  <button
                    type="button"
                    onClick={onOpenCsvImport}
                    className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 hover:bg-sky-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-brand dark:hover:text-sky-400 hover:border-brand/40 flex items-center justify-center transition-all ios-btn-tap shrink-0"
                    title="Impor Transaksi dari File CSV"
                    aria-label="Impor Transaksi CSV"
                  >
                    <Icon name="file-text" className="w-4 h-4" strokeWidth={2.2} />
                  </button>
                )}
              </div>

              {/* Collapsible Date-Range Panel */}
              {isDateFilterOpen && (
                <div className="p-3 bg-slate-50 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-700 rounded-2xl space-y-2.5 shadow-sm animate-ios-sheet">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <Icon name="filter" className="w-3.5 h-3.5 text-brand" />
                      Rentang Periode Transaksi
                    </span>
                    {hasActiveDateFilter && (
                      <button
                        type="button"
                        onClick={() => {
                          applyDatePreset('ALL');
                        }}
                        className="text-[11px] font-semibold text-rose-500 hover:underline ios-btn-tap"
                      >
                        Reset Periode
                      </button>
                    )}
                  </div>

                  {/* Preset quick buttons */}
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      { id: 'ALL', label: 'Semua Waktu' },
                      { id: 'TODAY', label: 'Hari Ini' },
                      { id: 'THIS_WEEK', label: 'Minggu Ini' },
                      { id: 'THIS_MONTH', label: 'Bulan Ini' },
                      { id: 'LAST_MONTH', label: 'Bulan Lalu' }
                    ].map(p => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => applyDatePreset(p.id)}
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-colors ios-btn-tap ${
                          datePreset === p.id && !startDate && !endDate && p.id === 'ALL'
                            ? 'bg-brand text-white'
                            : datePreset === p.id && p.id !== 'ALL'
                              ? 'bg-brand text-white'
                              : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>

                  {/* Custom From & To Date Inputs */}
                  <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-200 dark:border-slate-700/60">
                    <div>
                      <label className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 block mb-1">
                        Dari Tanggal:
                      </label>
                      <input
                        type="date"
                        value={startDate}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => {
                          setStartDate(e.target.value);
                          setDatePreset('CUSTOM');
                        }}
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                      />
                    </div>
                    <div>
                      <label className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 block mb-1">
                        Sampai Tanggal:
                      </label>
                      <input
                        type="date"
                        value={endDate}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => {
                          setEndDate(e.target.value);
                          setDatePreset('CUSTOM');
                        }}
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-800 dark:text-slate-200 focus:outline-none focus:border-brand"
                      />
                    </div>
                  </div>

                  {/* Summary Indicator badge */}
                  {hasActiveDateFilter && (
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center justify-between pt-0.5">
                      <span>
                        Menampilkan transaksi:{' '}
                        <strong className="text-slate-700 dark:text-slate-200">
                          {startDate ? formatDateID(startDate) : 'Awal'} s/d {endDate ? formatDateID(endDate) : 'Sekarang'}
                        </strong>
                      </span>
                      <span className="text-xs font-bold text-brand">
                        ({filteredTransactions.length})
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Segmented Control for Mutasi Filter */}
              <SegmentedControl
                options={[
                  { value: 'ALL', label: 'Semua' },
                  { value: 'EXPENSE', label: 'Pengeluaran' },
                  { value: 'INCOME', label: 'Pemasukan' }
                ]}
                value={filterType}
                onChange={setFilterType}
                className="w-full"
              />

              {/* Horizontal Category Filter Chips */}
              <div className="flex gap-1.5 overflow-x-auto no-scrollbar py-1">
                <button
                  type="button"
                  onClick={() => setSelectedCategoryFilter('ALL')}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold whitespace-nowrap transition-colors ios-btn-tap ${
                    selectedCategoryFilter === 'ALL'
                      ? 'bg-brand text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                  }`}
                >
                  Semua Kategori
                </button>
                {allCategories.map(c => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setSelectedCategoryFilter(c.id)}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold whitespace-nowrap transition-colors ios-btn-tap flex items-center gap-1 ${
                      selectedCategoryFilter === c.id
                        ? 'bg-brand text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    <span>{c.icon}</span>
                    <span>{c.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* List with Swipe-to-Action & Long-Press */}
            {filteredTransactions.length === 0 ? (
              <div className="text-center py-8">
                <IconBadge icon="receipt" className="w-10 h-10 rounded-xl bg-slate-50 dark:bg-slate-900 text-slate-400 mx-auto mb-1.5" iconClass="w-5 h-5" />
                <p className="text-xs text-slate-400">Tidak ada transaksi ditemukan.</p>
              </div>
            ) : (
              <div className="divide-y divide-transparent">
                {filteredTransactions.slice(0, 40).map((tx, idx) => {
                  const cat = getCategoryById(tx.category, customCategories);
                  const acc = safeAccounts.find(a => a.id === tx.accountId);

                  return (
                    <SwipeableTransactionRow
                      key={tx.id}
                      tx={tx}
                      idx={idx}
                      isLast={idx === filteredTransactions.length - 1}
                      cat={cat}
                      acc={acc}
                      hideBalance={hideBalance}
                      onDelete={onDeleteTx}
                      onEdit={onEditTx}
                      onDuplicate={onDuplicateTx}
                      isNewlyAdded={newlyAddedTxIds ? newlyAddedTxIds.has(tx.id) : false}
                      isDeleting={deletingTxIds ? deletingTxIds.has(tx.id) : false}
                      onClearNewlyAdded={onClearNewlyAddedTx}
                    />
                  );
                })}
              </div>
            )}
          </div>
        </div>
      );
    });

    // =========================================================================
    // 11. ROOT APP COMPONENT WITH HORIZONTAL SWIPE NAVIGATION
    // =========================================================================
    const App = () => {
      const [showSplash, setShowSplash] = useState(true);
      const [isUnlocked, setIsUnlocked] = useState(false);
      const [pin, setPin] = useState(() => StorageService.getPin());
      const [name, setName] = useState(() => StorageService.getName());
      const [username, setUsername] = useState(() => StorageService.getUsername());
      const [avatar, setAvatar] = useState(() => StorageService.getAvatar());

      const [accounts, setAccounts] = useState(() => StorageService.getAccounts());
      const [transactions, setTransactions] = useState(() => StorageService.getTransactions());
      const [savingsGoals, setSavingsGoals] = useState(() => StorageService.getSavingsGoals());
      const [debts, setDebts] = useState(() => StorageService.getDebts());
      const [customCategories, setCustomCategories] = useState(() => StorageService.getCustomCategories());
      const [safeBudget, setSafeBudget] = useState(() => StorageService.getSafeBudget());
      const [hideBalance, setHideBalance] = useState(() => StorageService.getHideBalance());
      const [theme, setTheme] = useState(() => StorageService.getTheme());

      const [activeTab, setActiveTab] = useState('dashboard'); // dashboard | debts | savings | analytics
      const [toastMsg, setToastMsg] = useState('');

      // Layout animation state tracking
      const [deletingTxIds, setDeletingTxIds] = useState(() => new Set());
      const [newlyAddedTxIds, setNewlyAddedTxIds] = useState(() => new Set());

      const handleClearNewlyAddedTx = useCallback((txId) => {
        setNewlyAddedTxIds(prev => {
          if (!prev.has(txId)) return prev;
          const next = new Set(prev);
          next.delete(txId);
          return next;
        });
      }, []);

      // Modals
      const [isTxModalOpen, setIsTxModalOpen] = useState(false);
      const [txModalInitial, setTxModalInitial] = useState(null);
      const [isAccModalOpen, setIsAccModalOpen] = useState(false);
      const [isSavingsModalOpen, setIsSavingsModalOpen] = useState(false);
      const [savingsGoalToEdit, setSavingsGoalToEdit] = useState(null);
      const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
      const [isDebtModalOpen, setIsDebtModalOpen] = useState(false);
      const [isDevModalOpen, setIsDevModalOpen] = useState(false);
      const [isCsvImportModalOpen, setIsCsvImportModalOpen] = useState(false);
      const [isTutorialOpen, setIsTutorialOpen] = useState(false);

      // Auto-trigger tutorial on first run once unlocked
      useEffect(() => {
        if (isUnlocked) {
          const completed = StorageService.getTutorialCompleted();
          if (!completed) {
            const timer = setTimeout(() => {
              setIsTutorialOpen(true);
            }, 600);
            return () => clearTimeout(timer);
          }
        }
      }, [isUnlocked]);

      const handleDismissTutorial = useCallback(() => {
        setIsTutorialOpen(false);
        StorageService.setTutorialCompleted(true);
      }, []);

      const showToast = useCallback((msg) => {
        setToastMsg(msg);
      }, []);

      // Theme toggle with full DOM synchronization
      const toggleTheme = useCallback(() => {
        setTheme(prev => {
          const next = prev === 'dark' ? 'light' : 'dark';
          StorageService.setTheme(next);
          if (next === 'dark') {
            document.documentElement.classList.add('dark');
            if (document.body) document.body.classList.add('dark');
            const rootEl = document.getElementById('root');
            if (rootEl) rootEl.classList.add('dark');
          } else {
            document.documentElement.classList.remove('dark');
            if (document.body) document.body.classList.remove('dark');
            const rootEl = document.getElementById('root');
            if (rootEl) rootEl.classList.remove('dark');
          }
          showToast(next === 'dark' ? 'Mode Gelap diaktifkan 🌙' : 'Mode Terang diaktifkan ☀️');
          return next;
        });
      }, [showToast]);

      useEffect(() => {
        const isDark = theme === 'dark';
        if (isDark) {
          document.documentElement.classList.add('dark');
          if (document.body) document.body.classList.add('dark');
          const rootEl = document.getElementById('root');
          if (rootEl) rootEl.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
          if (document.body) document.body.classList.remove('dark');
          const rootEl = document.getElementById('root');
          if (rootEl) rootEl.classList.remove('dark');
        }
      }, [theme]);

      // Global Mobile Keyboard Handling
      useEffect(() => {
        // Anti-tamper environment & integrity verification
        if (typeof CryptoService !== 'undefined' && CryptoService.verifyIntegrity) {
          CryptoService.verifyIntegrity();
        }

        window.addEventListener('focusin', handleGlobalInputFocus);
        window.addEventListener('focusout', handleGlobalInputBlur);
        return () => {
          window.removeEventListener('focusin', handleGlobalInputFocus);
          window.removeEventListener('focusout', handleGlobalInputBlur);
        };
      }, []);

      // Horizontal Swipe Gesture Handling
      const tabsOrder = ['dashboard', 'cards', 'debts', 'savings', 'analytics'];
      const touchStartX = useRef(0);
      const touchStartY = useRef(0);

      const handleScreenTouchStart = (e) => {
        if (e.touches && e.touches[0]) {
          touchStartX.current = e.touches[0].clientX;
          touchStartY.current = e.touches[0].clientY;
        }
      };

      const handleScreenTouchEnd = (e) => {
        if (e.changedTouches && e.changedTouches[0]) {
          const deltaX = e.changedTouches[0].clientX - touchStartX.current;
          const deltaY = e.changedTouches[0].clientY - touchStartY.current;

          // Detect intentional horizontal swipe (distance > 70px and x > 1.8 * y)
          if (Math.abs(deltaX) > 70 && Math.abs(deltaX) > Math.abs(deltaY) * 1.8) {
            const curIdx = tabsOrder.indexOf(activeTab);
            if (deltaX < 0 && curIdx < tabsOrder.length - 1) {
              // Swipe left -> Next tab
              setActiveTab(tabsOrder[curIdx + 1]);
            } else if (deltaX > 0 && curIdx > 0) {
              // Swipe right -> Previous tab
              setActiveTab(tabsOrder[curIdx - 1]);
            }
          }
        }
      };

      // Handlers wrapped in useCallback for stable references across renders
      const handleToggleHideBalance = useCallback(() => {
        setHideBalance(prev => {
          const next = !prev;
          StorageService.setHideBalance(next);
          return next;
        });
      }, []);

      const handleSetBudget = useCallback((val) => {
        setSafeBudget(val);
        StorageService.setSafeBudget(val);
        showToast('Limit belanja bulanan diperbarui');
      }, []);

      const handleAddTransaction = useCallback((newTx) => {
        let isNew = false;
        setTransactions(prev => {
          const exists = prev.some(t => t.id === newTx.id);
          isNew = !exists;
          const next = exists
            ? prev.map(t => t.id === newTx.id ? newTx : t)
            : [newTx, ...prev];
          StorageService.setTransactions(next);
          return next;
        });

        // Trigger layout slide-in animation for newly added transaction
        if (isNew) {
          setNewlyAddedTxIds(prev => {
            const next = new Set(prev);
            next.add(newTx.id);
            return next;
          });
          // Fallback auto-clear after 1.2s in case animationend does not fire
          setTimeout(() => {
            handleClearNewlyAddedTx(newTx.id);
          }, 1200);
        }

        showToast(isNew ? 'Transaksi berhasil dicatat' : 'Transaksi diperbarui');
      }, [handleClearNewlyAddedTx, showToast]);

      const handleImportBatchTransactions = useCallback((newTxs) => {
        if (!Array.isArray(newTxs) || newTxs.length === 0) return;
        setTransactions(prev => {
          const combined = [...newTxs, ...prev];
          StorageService.setTransactions(combined);
          return combined;
        });

        setNewlyAddedTxIds(prev => {
          const next = new Set(prev);
          newTxs.slice(0, 10).forEach(t => next.add(t.id));
          return next;
        });

        setTimeout(() => {
          newTxs.forEach(t => handleClearNewlyAddedTx(t.id));
        }, 1200);

        showToast(`Berhasil mengimpor ${newTxs.length} mutasi baru!`);
      }, [handleClearNewlyAddedTx, showToast]);

      const handleDeleteTransaction = useCallback((txId) => {
        if (deletingTxIds.has(txId)) return;
        if (!confirm('Hapus mutasi ini?')) return;

        // Trigger layout fade-out & collapse animation
        setDeletingTxIds(prev => {
          const next = new Set(prev);
          next.add(txId);
          return next;
        });

        if (window.VoraletHaptics && typeof window.VoraletHaptics.delete === 'function') {
          window.VoraletHaptics.delete();
        }

        setTimeout(() => {
          setTransactions(prev => {
            const next = prev.filter(t => t.id !== txId);
            StorageService.setTransactions(next);
            return next;
          });
          setDeletingTxIds(prev => {
            const next = new Set(prev);
            next.delete(txId);
            return next;
          });
          showToast('Mutasi dihapus');
        }, 320);
      }, [deletingTxIds, showToast]);

      const handleEditTransaction = useCallback((tx) => {
        setTxModalInitial({
          id: tx.id,
          type: tx.type,
          amount: tx.amount,
          category: tx.category,
          accountId: tx.accountId,
          notes: tx.notes
        });
        setIsTxModalOpen(true);
      }, []);

      const handleDuplicateTransaction = useCallback((tx) => {
        const dupTx = {
          ...tx,
          id: 'tx_' + Date.now(),
          date: new Date().toISOString().split('T')[0],
          createdAt: new Date().toISOString()
        };
        handleAddTransaction(dupTx);
        showToast('Transaksi berhasil diduplikat');
      }, [handleAddTransaction]);

      const handleAddAccount = useCallback((acc) => {
        setAccounts(prev => {
          const next = [...prev, acc];
          StorageService.setAccounts(next);
          return next;
        });
        showToast('Dompet berhasil dibuat');
      }, []);

      const handleEditAccount = useCallback((accId, data) => {
        setAccounts(prev => {
          const next = prev.map(a => a.id === accId ? { ...a, ...data } : a);
          StorageService.setAccounts(next);
          return next;
        });
        showToast('Dompet diperbarui');
      }, []);

      const handleDeleteAccount = useCallback((accId) => {
        setAccounts(prev => {
          if (prev.length <= 1) {
            alert('Minimal harus menyisakan 1 dompet');
            return prev;
          }
          if (!confirm('Hapus dompet ini beserta seluruh transaksinya?')) return prev;
          const next = prev.filter(a => a.id !== accId);
          StorageService.setAccounts(next);
          setTransactions(tPrev => {
            const tNext = tPrev.filter(t => t.accountId !== accId);
            StorageService.setTransactions(tNext);
            return tNext;
          });
          showToast('Dompet dihapus');
          return next;
        });
      }, []);

      // Savings Goals
      const handleSaveGoal = useCallback((goalData) => {
        setSavingsGoals(prev => {
          const exists = prev.some(g => g.id === goalData.id);
          const next = exists
            ? prev.map(g => g.id === goalData.id ? goalData : g)
            : [...prev, goalData];
          StorageService.setSavingsGoals(next);
          return next;
        });
        showToast('Target impian disimpan');
      }, []);

      const handleDeleteGoal = useCallback((goalId) => {
        if (!confirm('Hapus target impian ini?')) return;
        setSavingsGoals(prev => {
          const next = prev.filter(g => g.id !== goalId);
          StorageService.setSavingsGoals(next);
          return next;
        });
        showToast('Target impian dihapus');
      }, []);

      const handleDepositGoal = useCallback((goalId, amount, mode) => {
        setSavingsGoals(prev => {
          const next = prev.map(g => {
            if (g.id === goalId) {
              const cur = Number(g.currentAmount) || 0;
              const nextAmt = mode === 'DEPOSIT' ? cur + amount : Math.max(0, cur - amount);
              return { ...g, currentAmount: nextAmt };
            }
            return g;
          });
          StorageService.setSavingsGoals(next);
          return next;
        });
        showToast(mode === 'DEPOSIT' ? 'Tabungan disetor' : 'Tabungan ditarik');
      }, []);

      // Debts
      const handleAddDebt = useCallback((debtData) => {
        if (!debtData) return;
        const isPaid = Boolean(debtData.isPaid || debtData.status === 'LUNAS');
        const note = debtData.note || debtData.notes || '';
        const normalized = {
          ...debtData,
          isPaid,
          status: isPaid ? 'LUNAS' : 'BELUM_LUNAS',
          note,
          notes: note
        };
        setDebts(prev => {
          const exists = prev.some(d => d.id === normalized.id);
          const next = exists
            ? prev.map(d => d.id === normalized.id ? normalized : d)
            : [normalized, ...prev];
          StorageService.setDebts(next);
          return next;
        });
        showToast('Catatan disimpan');
      }, [showToast]);

      const handleToggleDebtStatus = useCallback((debtId) => {
        setDebts(prev => {
          const next = prev.map(d => {
            if (d.id === debtId) {
              const currentPaid = Boolean(d.isPaid || d.status === 'LUNAS');
              const newPaid = !currentPaid;
              return {
                ...d,
                isPaid: newPaid,
                status: newPaid ? 'LUNAS' : 'BELUM_LUNAS'
              };
            }
            return d;
          });
          StorageService.setDebts(next);
          return next;
        });
        showToast('Status diperbarui');
      }, [showToast]);

      const handleDeleteDebt = useCallback((debtId) => {
        if (!confirm('Hapus catatan ini?')) return;
        setDebts(prev => {
          const next = prev.filter(d => d.id !== debtId);
          StorageService.setDebts(next);
          return next;
        });
        showToast('Catatan dihapus');
      }, []);

      // Quick Expense Preset
      const handleQuickExpenseSelect = useCallback((preset) => {
        setTxModalInitial({
          type: 'EXPENSE',
          amount: preset.amount,
          category: preset.category,
          notes: preset.label
        });
        setIsTxModalOpen(true);
      }, []);

      // Profile & Reset
      const handleUpdateProfile = useCallback((prof) => {
        setName(prof.name);
        setUsername(prof.username);
        setAvatar(prof.avatar);
        StorageService.setName(prof.name);
        StorageService.setUsername(prof.username);
        StorageService.setAvatar(prof.avatar);
        showToast('Profil berhasil disimpan');
      }, []);

      const handleResetPin = useCallback((newPin) => {
        if (!newPin) {
          showToast('Perangkat tidak mendukung penyimpanan PIN aman');
          return;
        }
        StorageService.clearAll();
        setPin(newPin);
        StorageService.setPin(newPin);
        setName('');
        setUsername('');
        setAvatar('');
        setAccounts([]);
        setTransactions([]);
        setSavingsGoals([]);
        setDebts([]);
        setSafeBudget(0);
        setIsUnlocked(false);
        showToast('PIN dibuat ulang dan data lama dihapus');
      }, []);

      const handleHardReset = useCallback(() => {
        StorageService.clearAll();
        setPin(null);
        setName('');
        setUsername('');
        setAvatar('');
        setAccounts([]);
        setTransactions([]);
        setSavingsGoals([]);
        setDebts([]);
        setCustomCategories([]);
        setSafeBudget(0);
        setIsUnlocked(false);
        setActiveTab('dashboard');
        setIsSettingsModalOpen(false);
        showToast('Semua data berhasil dibersihkan');
      }, []);

      const handleSaveCustomCategory = useCallback((cat) => {
        setCustomCategories(prev => {
          const safePrev = Array.isArray(prev) ? prev : [];
          const existingIdx = safePrev.findIndex(c => c.id === cat.id);
          let next;
          if (existingIdx >= 0) {
            next = [...safePrev];
            next[existingIdx] = cat;
          } else {
            next = [...safePrev, cat];
          }
          StorageService.setCustomCategories(next);
          return next;
        });
        showToast('Kategori kustom berhasil disimpan');
      }, []);

      const handleDeleteCustomCategory = useCallback((catId) => {
        setCustomCategories(prev => {
          const safePrev = Array.isArray(prev) ? prev : [];
          const next = safePrev.filter(c => c.id !== catId);
          StorageService.setCustomCategories(next);
          return next;
        });
        showToast('Kategori kustom berhasil dihapus');
      }, []);

      const handleExportData = useCallback(() => {
        const rawPayload = {
          voralet_version: '__VORALET_VERSION__',
          exported_at: new Date().toISOString(),
          name,
          username,
          accounts,
          transactions,
          savingsGoals,
          debts,
          customCategories,
          safeBudget
        };
        // Ultra-secure encrypted vault backup: non-verifiable & tamper-proof without Voralet
        const encryptedBackup = CryptoService.encryptBackup(rawPayload);
        const finalExport = encryptedBackup || rawPayload;
        const blob = new Blob([JSON.stringify(finalExport, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voralet_encrypted_vault_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('Cadangan brankas terenkripsi berhasil diunduh 🔒');
      }, [name, username, accounts, transactions, savingsGoals, debts, customCategories, safeBudget]);

      const handleImportData = useCallback((data) => {
        // Auto-decrypt if encrypted vault format
        let targetData = data;
        if (data && data.voralet_encrypted_vault) {
          const decrypted = CryptoService.decryptBackup(data);
          if (!decrypted) {
            alert('Enkripsi cadangan tidak valid atau file telah dimodifikasi.');
            return;
          }
          targetData = decrypted;
        }
        if (!targetData || !Array.isArray(targetData.accounts)) {
          alert('Format JSON tidak sesuai dengan standar Voralet');
          return;
        }
        if (targetData.name) { setName(targetData.name); StorageService.setName(targetData.name); }
        if (targetData.username) { setUsername(targetData.username); StorageService.setUsername(targetData.username); }
        if (Array.isArray(targetData.accounts)) { setAccounts(targetData.accounts); StorageService.setAccounts(targetData.accounts); }
        if (Array.isArray(targetData.transactions)) { setTransactions(targetData.transactions); StorageService.setTransactions(targetData.transactions); }
        if (Array.isArray(targetData.savingsGoals)) { setSavingsGoals(targetData.savingsGoals); StorageService.setSavingsGoals(targetData.savingsGoals); }
        if (Array.isArray(targetData.debts)) { setDebts(targetData.debts); StorageService.setDebts(targetData.debts); }
        if (Array.isArray(targetData.customCategories)) { setCustomCategories(targetData.customCategories); StorageService.setCustomCategories(targetData.customCategories); }
        if (targetData.safeBudget !== undefined) { setSafeBudget(targetData.safeBudget); StorageService.setSafeBudget(targetData.safeBudget); }
        showToast('Data terenkripsi berhasil dipulihkan! 🔓');
      }, []);

      // Stable modal openers and navigation callbacks wrapped in useCallback
      const handleOpenAddTx = useCallback(() => {
        setTxModalInitial(null);
        setIsTxModalOpen(true);
      }, []);

      const handleOpenAddIncome = useCallback(() => {
        setTxModalInitial({ type: 'INCOME' });
        setIsTxModalOpen(true);
      }, []);

      const handleOpenAddExpense = useCallback(() => {
        setTxModalInitial({ type: 'EXPENSE' });
        setIsTxModalOpen(true);
      }, []);

      const handleOpenAccounts = useCallback(() => {
        setIsAccModalOpen(true);
      }, []);

      const handleCloseAccounts = useCallback(() => {
        setIsAccModalOpen(false);
      }, []);

      const handleOpenSettings = useCallback(() => {
        setIsSettingsModalOpen(true);
      }, []);

      const handleCloseSettings = useCallback(() => {
        setIsSettingsModalOpen(false);
      }, []);

      const handleOpenDebtsTab = useCallback(() => {
        setActiveTab('debts');
      }, []);

      const handleOpenSavingsTab = useCallback(() => {
        setActiveTab('savings');
      }, []);

      const handleOpenNewSavingsGoal = useCallback(() => {
        setSavingsGoalToEdit(null);
        setIsSavingsModalOpen(true);
      }, []);

      const handleEditSavingsGoal = useCallback((g) => {
        setSavingsGoalToEdit(g);
        setIsSavingsModalOpen(true);
      }, []);

      const handleCloseSavingsModal = useCallback(() => {
        setIsSavingsModalOpen(false);
      }, []);

      const handleCloseTxModal = useCallback(() => {
        setIsTxModalOpen(false);
      }, []);

      const handleOpenAddTxFromAccount = useCallback((accId) => {
        setIsAccModalOpen(false);
        setTxModalInitial({ accountId: accId });
        setIsTxModalOpen(true);
      }, []);

      // Memoized user profile object to keep reference identity stable
      const memoizedUserProfile = useMemo(() => ({
        name,
        username,
        avatar
      }), [name, username, avatar]);

      if (showSplash) {
        return <SplashScreen onFinish={() => setShowSplash(false)} />;
      }

      if (!pin) {
        return (
          <OnboardingFlow
            onComplete={(initialData) => {
              setPin(initialData.pin);
              setName(initialData.name);
              setUsername(initialData.username);
              setAvatar(initialData.avatar);
              setAccounts(initialData.accounts);
              setTransactions(initialData.transactions);
              setSavingsGoals(initialData.savingsGoals);
              setDebts(initialData.debts);
              setIsUnlocked(true);
            }}
          />
        );
      }

      if (!isUnlocked) {
        return (
          <ReturningUserPinScreen
            storedPin={pin}
            userName={name}
            username={username}
            avatar={avatar}
            theme={theme}
            onToggleTheme={toggleTheme}
            onUnlock={() => setIsUnlocked(true)}
            onResetPin={handleResetPin}
          />
        );
      }

      const isAnyModalOpen = isTxModalOpen || isAccModalOpen || isSavingsModalOpen || isSettingsModalOpen || isDebtModalOpen || isDevModalOpen;

      return (
        <div className={`h-[100dvh] flex flex-col ${theme === 'dark' ? 'dark bg-[#0F172A] text-[#F8FAFC]' : 'bg-slate-50 text-[#0F172A]'} overflow-hidden select-none transition-colors duration-300 ease-in-out`}>
          {toastMsg && <Toast message={toastMsg} onClose={() => setToastMsg('')} />}

          {/* iOS Background Depth Stacking Layer */}
          <div className={`ios-modal-depth-layer flex-1 flex flex-col w-full h-full overflow-hidden ${
            isAnyModalOpen ? 'ios-modal-depth-stacked' : ''
          }`}>
            <main
              onTouchStart={handleScreenTouchStart}
              onTouchEnd={handleScreenTouchEnd}
              className="flex-1 w-full max-w-md mx-auto px-4 pt-3 pb-28 overflow-y-auto no-scrollbar"
            >
            <ErrorBoundary>
              {activeTab === 'dashboard' && (
                <MainDashboard
                  accounts={accounts}
                  transactions={transactions}
                  userProfile={memoizedUserProfile}
                  hideBalance={hideBalance}
                  onToggleHideBalance={handleToggleHideBalance}
                  onOpenAddTx={handleOpenAddTx}
                  onOpenAddIncome={handleOpenAddIncome}
                  onOpenAddExpense={handleOpenAddExpense}
                  onOpenAccounts={handleOpenAccounts}
                  onOpenSettings={handleOpenSettings}
                  onOpenDebts={handleOpenDebtsTab}
                  onOpenSavings={handleOpenSavingsTab}
                  onOpenNewSavingsGoal={handleOpenNewSavingsGoal}
                  onDeleteTx={handleDeleteTransaction}
                  onEditTx={handleEditTransaction}
                  onDuplicateTx={handleDuplicateTransaction}
                  safeBudget={safeBudget}
                  onSetBudget={handleSetBudget}
                  savingsGoals={savingsGoals}
                  debts={debts}
                  onSelectQuickExpense={handleQuickExpenseSelect}
                  customCategories={customCategories}
                  onSelectTab={setActiveTab}
                  onOpenCsvImport={() => setIsCsvImportModalOpen(true)}
                  deletingTxIds={deletingTxIds}
                  newlyAddedTxIds={newlyAddedTxIds}
                  onClearNewlyAddedTx={handleClearNewlyAddedTx}
                />
              )}

              {activeTab === 'cards' && (
                <CardsView
                  accounts={accounts}
                  transactions={transactions}
                  hideBalance={hideBalance}
                  onToggleHideBalance={handleToggleHideBalance}
                  onAddAccount={handleAddAccount}
                  onUpdateAccount={handleEditAccount}
                  onDeleteAccount={handleDeleteAccount}
                  onOpenAddTx={handleOpenAddTxFromAccount}
                />
              )}

              {activeTab === 'debts' && (
                <DebtsView
                  debts={debts}
                  onAddDebt={handleAddDebt}
                  onToggleStatus={handleToggleDebtStatus}
                  onDeleteDebt={handleDeleteDebt}
                  hideBalance={hideBalance}
                  onModalChange={setIsDebtModalOpen}
                />
              )}

              {activeTab === 'savings' && (
                <SavingsView
                  savingsGoals={savingsGoals}
                  onOpenNewGoal={handleOpenNewSavingsGoal}
                  onEditGoal={handleEditSavingsGoal}
                  onDeleteGoal={handleDeleteGoal}
                  onDepositGoal={handleDepositGoal}
                  hideBalance={hideBalance}
                />
              )}

              {activeTab === 'analytics' && (
                <AnalyticsView
                  transactions={transactions}
                  accounts={accounts}
                  debts={debts}
                  savingsGoals={savingsGoals}
                  hideBalance={hideBalance}
                  customCategories={customCategories}
                />
              )}
            </ErrorBoundary>
          </main>

          {/* Floating Capsule Bottom Navigation with Fluid Active Pill */}
          <FloatingCapsuleNav currentTab={activeTab} onSelectTab={setActiveTab} />
        </div>

          {/* Modals with Apple-style sheets and strict close icons */}
          <TransactionModal
            isOpen={isTxModalOpen}
            onClose={handleCloseTxModal}
            initialData={txModalInitial}
            accounts={accounts}
            onAddTransaction={handleAddTransaction}
            customCategories={customCategories}
            onSaveCustomCategory={handleSaveCustomCategory}
          />

          <AccountsManagerModal
            isOpen={isAccModalOpen}
            onClose={handleCloseAccounts}
            accounts={accounts}
            transactions={transactions}
            onAddAccount={handleAddAccount}
            onDeleteAccount={handleDeleteAccount}
            onEditAccount={handleEditAccount}
            hideBalance={hideBalance}
            onToggleHideBalance={handleToggleHideBalance}
            onOpenAddTx={handleOpenAddTxFromAccount}
          />

          <SavingsGoalModal
            isOpen={isSavingsModalOpen}
            onClose={handleCloseSavingsModal}
            onSaveGoal={handleSaveGoal}
            onDepositGoal={handleDepositGoal}
            goalToEdit={savingsGoalToEdit}
            accounts={accounts}
          />

          <SettingsModal
            isOpen={isSettingsModalOpen}
            onClose={handleCloseSettings}
            userProfile={memoizedUserProfile}
            onUpdateProfile={handleUpdateProfile}
            onHardReset={handleHardReset}
            onImportData={handleImportData}
            onExportData={handleExportData}
            onOpenCsvImport={() => setIsCsvImportModalOpen(true)}
            theme={theme}
            onToggleTheme={toggleTheme}
            customCategories={customCategories}
            onSaveCustomCategory={handleSaveCustomCategory}
            onDeleteCustomCategory={handleDeleteCustomCategory}
            onOpenDeveloperGate={() => setIsDevModalOpen(true)}
            onReplayTutorial={() => setIsTutorialOpen(true)}
          />

          <CsvImportModal
            isOpen={isCsvImportModalOpen}
            onClose={() => setIsCsvImportModalOpen(false)}
            accounts={accounts}
            customCategories={customCategories}
            onImportBatch={handleImportBatchTransactions}
          />

          <DeveloperSecurityModal
            isOpen={isDevModalOpen}
            onClose={() => setIsDevModalOpen(false)}
            onHardReset={handleHardReset}
            accounts={accounts}
            transactions={transactions}
            debts={debts}
            savingsGoals={savingsGoals}
          />

          <NonIntrusiveTutorialModal
            isOpen={isTutorialOpen}
            onDismiss={handleDismissTutorial}
          />
        </div>
      );
    };

    const mountApp = () => {
      const rootElement = document.getElementById('root');
      if (!rootElement) return;
      const root = ReactDOM.createRoot(rootElement);
      root.render(
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      );
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', mountApp);
    } else {
      mountApp();
    }
  </script>
</body>
</html>
"""
