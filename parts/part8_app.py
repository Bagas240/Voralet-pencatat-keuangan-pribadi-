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
      onDuplicate
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
        <div className="relative overflow-hidden select-none">
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
            isOpen={isMenuOpen}
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
    const MainDashboard = ({
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
      onSelectQuickExpense
    }) => {
      const [searchQuery, setSearchQuery] = useState('');
      const [filterType, setFilterType] = useState('ALL'); // ALL | EXPENSE | INCOME
      const [selectedAccountFilter, setSelectedAccountFilter] = useState('ALL');
      const [selectedCategoryFilter, setSelectedCategoryFilter] = useState('ALL');

      const safeAccounts = Array.isArray(accounts) ? accounts.filter(Boolean) : [];
      const safeTransactions = Array.isArray(transactions) ? transactions.filter(Boolean) : [];

      const totalBalance = useMemo(() => {
        return Ledger.getTotalBalance(safeAccounts, safeTransactions);
      }, [safeAccounts, safeTransactions]);

      const monthSummary = useMemo(() => {
        const now = new Date();
        const prefix = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        const thisMonthTx = safeTransactions.filter(t => t && t.date && t.date.startsWith(prefix));
        return Ledger.getSummaryTotals(thisMonthTx);
      }, [safeTransactions]);

      // Filtered transactions
      const filteredTransactions = useMemo(() => {
        return safeTransactions.filter(tx => {
          if (!tx) return false;
          if (filterType !== 'ALL' && tx.type !== filterType) return false;
          if (selectedAccountFilter !== 'ALL' && tx.accountId !== selectedAccountFilter) return false;
          if (selectedCategoryFilter !== 'ALL' && tx.category !== selectedCategoryFilter) return false;
          if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            const cat = (CATEGORIES.find(c => c.id === tx.category)?.label || '').toLowerCase();
            const notes = (tx.notes || '').toLowerCase();
            const amt = String(tx.amount || '');
            if (!cat.includes(q) && !notes.includes(q) && !amt.includes(q)) return false;
          }
          return true;
        });
      }, [safeTransactions, filterType, selectedAccountFilter, selectedCategoryFilter, searchQuery]);

      return (
        <div className="space-y-4 pb-28 animate-ios-tab-view">
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
                <p className="text-[11px] font-mono text-brand dark:text-sky-400 font-semibold truncate">
                  @{userProfile.username || 'voralet_user'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onOpenAccounts}
                className="p-2.5 rounded-2xl bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-slate-700 shadow-sm dark:shadow-[0_4px_12px_rgba(0,0,0,0.35)] text-slate-600 hover:text-slate-900 dark:text-slate-300 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                title="Kelola Dompet"
                aria-label="Kelola Dompet"
              >
                <Icon name="wallet" className="w-5 h-5" />
              </button>
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

          {/* Quick Shortcuts Bar: Dompet, Hutang, & Kantong Impian */}
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={onOpenAccounts}
              className="py-2.5 px-2 bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-2xl flex flex-col items-center justify-center gap-1 shadow-sm dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] transition-all ios-btn-tap hover:border-brand/40"
            >
              <Icon name="wallet" className="w-4 h-4 text-brand dark:text-sky-400" />
              <span className="text-[11px] font-bold whitespace-nowrap">Dompet</span>
            </button>
            <button
              type="button"
              onClick={onOpenDebts}
              className="py-2.5 px-2 bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-2xl flex flex-col items-center justify-center gap-1 shadow-sm dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] transition-all ios-btn-tap hover:border-brand/40"
            >
              <Icon name="receipt" className="w-4 h-4 text-amber-500" />
              <span className="text-[11px] font-bold whitespace-nowrap">Hutang</span>
            </button>
            <button
              type="button"
              onClick={onOpenSavings}
              className="py-2.5 px-2 bg-white dark:bg-slate-800 border border-slate-200/90 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-2xl flex flex-col items-center justify-center gap-1 shadow-sm dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] transition-all ios-btn-tap hover:border-brand/40"
            >
              <Icon name="target" className="w-4 h-4 text-emerald-500" />
              <span className="text-[11px] font-bold whitespace-nowrap">Impian</span>
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

            {/* Live Search & Filter */}
            <div className="space-y-2 mb-3">
              <div className="relative">
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
                {CATEGORIES.map(c => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setSelectedCategoryFilter(c.id)}
                    className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold whitespace-nowrap transition-colors ios-btn-tap ${
                      selectedCategoryFilter === c.id
                        ? 'bg-brand text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    {c.label}
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
                  const cat = CATEGORIES.find(c => c.id === tx.category) || { label: tx.category, icon: 'tag' };
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
                    />
                  );
                })}
              </div>
            )}
          </div>
        </div>
      );
    };

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
      const [safeBudget, setSafeBudget] = useState(() => StorageService.getSafeBudget());
      const [hideBalance, setHideBalance] = useState(() => StorageService.getHideBalance());
      const [theme, setTheme] = useState(() => localStorage.getItem('voralet_theme') || 'light');

      const [activeTab, setActiveTab] = useState('dashboard'); // dashboard | debts | savings | analytics
      const [toastMsg, setToastMsg] = useState('');

      // Modals
      const [isTxModalOpen, setIsTxModalOpen] = useState(false);
      const [txModalInitial, setTxModalInitial] = useState(null);
      const [isAccModalOpen, setIsAccModalOpen] = useState(false);
      const [isSavingsModalOpen, setIsSavingsModalOpen] = useState(false);
      const [savingsGoalToEdit, setSavingsGoalToEdit] = useState(null);
      const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
      const [isDebtModalOpen, setIsDebtModalOpen] = useState(false);

      const showToast = useCallback((msg) => {
        setToastMsg(msg);
      }, []);

      // Theme toggle with full DOM synchronization
      const toggleTheme = useCallback(() => {
        setTheme(prev => {
          const next = prev === 'dark' ? 'light' : 'dark';
          StorageService.setTheme(next);
          try {
            localStorage.setItem('voralet_theme', next);
          } catch (e) {}

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
        window.addEventListener('focusin', handleGlobalInputFocus);
        window.addEventListener('focusout', handleGlobalInputBlur);
        return () => {
          window.removeEventListener('focusin', handleGlobalInputFocus);
          window.removeEventListener('focusout', handleGlobalInputBlur);
        };
      }, []);

      // Horizontal Swipe Gesture Handling
      const tabsOrder = ['dashboard', 'debts', 'savings', 'analytics'];
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

      // Handlers
      const handleToggleHideBalance = () => {
        setHideBalance(prev => {
          const next = !prev;
          StorageService.setHideBalance(next);
          return next;
        });
      };

      const handleSetBudget = (val) => {
        setSafeBudget(val);
        StorageService.setSafeBudget(val);
        showToast('Limit belanja bulanan diperbarui');
      };

      const handleAddTransaction = (newTx) => {
        setTransactions(prev => {
          const exists = prev.some(t => t.id === newTx.id);
          const next = exists
            ? prev.map(t => t.id === newTx.id ? newTx : t)
            : [newTx, ...prev];
          StorageService.setTransactions(next);
          return next;
        });
        showToast('Transaksi berhasil dicatat');
      };

      const handleDeleteTransaction = (txId) => {
        if (!confirm('Hapus mutasi ini?')) return;
        setTransactions(prev => {
          const next = prev.filter(t => t.id !== txId);
          StorageService.setTransactions(next);
          return next;
        });
        showToast('Mutasi dihapus');
      };

      const handleEditTransaction = (tx) => {
        setTxModalInitial({
          id: tx.id,
          type: tx.type,
          amount: tx.amount,
          category: tx.category,
          accountId: tx.accountId,
          notes: tx.notes
        });
        setIsTxModalOpen(true);
      };

      const handleDuplicateTransaction = (tx) => {
        const dupTx = {
          ...tx,
          id: 'tx_' + Date.now(),
          date: new Date().toISOString().split('T')[0],
          createdAt: new Date().toISOString()
        };
        handleAddTransaction(dupTx);
        showToast('Transaksi berhasil diduplikat');
      };

      const handleAddAccount = (acc) => {
        setAccounts(prev => {
          const next = [...prev, acc];
          StorageService.setAccounts(next);
          return next;
        });
        showToast('Dompet berhasil dibuat');
      };

      const handleEditAccount = (accId, data) => {
        setAccounts(prev => {
          const next = prev.map(a => a.id === accId ? { ...a, ...data } : a);
          StorageService.setAccounts(next);
          return next;
        });
        showToast('Dompet diperbarui');
      };

      const handleDeleteAccount = (accId) => {
        if (accounts.length <= 1) {
          alert('Minimal harus menyisakan 1 dompet');
          return;
        }
        if (!confirm('Hapus dompet ini beserta seluruh transaksinya?')) return;
        setAccounts(prev => {
          const next = prev.filter(a => a.id !== accId);
          StorageService.setAccounts(next);
          return next;
        });
        setTransactions(prev => {
          const next = prev.filter(t => t.accountId !== accId);
          StorageService.setTransactions(next);
          return next;
        });
        showToast('Dompet dihapus');
      };

      // Savings Goals
      const handleSaveGoal = (goalData) => {
        setSavingsGoals(prev => {
          const exists = prev.some(g => g.id === goalData.id);
          const next = exists
            ? prev.map(g => g.id === goalData.id ? goalData : g)
            : [...prev, goalData];
          StorageService.setSavingsGoals(next);
          return next;
        });
        showToast('Target impian disimpan');
      };

      const handleDeleteGoal = (goalId) => {
        if (!confirm('Hapus target impian ini?')) return;
        setSavingsGoals(prev => {
          const next = prev.filter(g => g.id !== goalId);
          StorageService.setSavingsGoals(next);
          return next;
        });
        showToast('Target impian dihapus');
      };

      const handleDepositGoal = (goalId, amount, mode) => {
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
      };

      // Debts
      const handleAddDebt = (debtData) => {
        setDebts(prev => {
          const exists = prev.some(d => d.id === debtData.id);
          const next = exists
            ? prev.map(d => d.id === debtData.id ? debtData : d)
            : [debtData, ...prev];
          StorageService.setDebts(next);
          return next;
        });
        showToast('Catatan disimpan');
      };

      const handleToggleDebtStatus = (debtId) => {
        setDebts(prev => {
          const next = prev.map(d => {
            if (d.id === debtId) {
              const newStatus = d.status === 'LUNAS' ? 'BELUM_LUNAS' : 'LUNAS';
              return { ...d, status: newStatus };
            }
            return d;
          });
          StorageService.setDebts(next);
          return next;
        });
        showToast('Status diperbarui');
      };

      const handleDeleteDebt = (debtId) => {
        if (!confirm('Hapus catatan ini?')) return;
        setDebts(prev => {
          const next = prev.filter(d => d.id !== debtId);
          StorageService.setDebts(next);
          return next;
        });
        showToast('Catatan dihapus');
      };

      // Quick Expense Preset
      const handleQuickExpenseSelect = (preset) => {
        setTxModalInitial({
          type: 'EXPENSE',
          amount: preset.amount,
          category: preset.category,
          notes: preset.label
        });
        setIsTxModalOpen(true);
      };

      // Profile & Reset
      const handleUpdateProfile = (prof) => {
        setName(prof.name);
        setUsername(prof.username);
        setAvatar(prof.avatar);
        StorageService.setName(prof.name);
        StorageService.setUsername(prof.username);
        StorageService.setAvatar(prof.avatar);
        showToast('Profil berhasil disimpan');
      };

      const handleResetPin = (newPin) => {
        setPin(newPin);
        StorageService.setPin(newPin);
        setIsUnlocked(true);
        showToast('PIN berhasil diubah');
      };

      const handleHardReset = () => {
        StorageService.clearAll();
        setPin(null);
        setName('');
        setUsername('');
        setAvatar('');
        setAccounts([]);
        setTransactions([]);
        setSavingsGoals([]);
        setDebts([]);
        setSafeBudget(0);
        setIsUnlocked(false);
        setActiveTab('dashboard');
        setIsSettingsModalOpen(false);
        showToast('Semua data berhasil dibersihkan');
      };

      const handleExportData = () => {
        const payload = {
          voralet_version: '__VORALET_VERSION__',
          exported_at: new Date().toISOString(),
          name,
          username,
          accounts,
          transactions,
          savingsGoals,
          debts,
          safeBudget
        };
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `voralet_backup_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('File JSON cadangan berhasil diunduh');
      };

      const handleImportData = (data) => {
        if (!data || !Array.isArray(data.accounts)) {
          alert('Format JSON tidak sesuai dengan standar Voralet');
          return;
        }
        if (data.name) { setName(data.name); StorageService.setName(data.name); }
        if (data.username) { setUsername(data.username); StorageService.setUsername(data.username); }
        if (Array.isArray(data.accounts)) { setAccounts(data.accounts); StorageService.setAccounts(data.accounts); }
        if (Array.isArray(data.transactions)) { setTransactions(data.transactions); StorageService.setTransactions(data.transactions); }
        if (Array.isArray(data.savingsGoals)) { setSavingsGoals(data.savingsGoals); StorageService.setSavingsGoals(data.savingsGoals); }
        if (Array.isArray(data.debts)) { setDebts(data.debts); StorageService.setDebts(data.debts); }
        if (data.safeBudget) { setSafeBudget(data.safeBudget); StorageService.setSafeBudget(data.safeBudget); }
        showToast('Data berhasil dipulihkan!');
      };

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

      const isAnyModalOpen = isTxModalOpen || isAccModalOpen || isSavingsModalOpen || isSettingsModalOpen || isDebtModalOpen;

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
                  userProfile={{ name, username, avatar }}
                  hideBalance={hideBalance}
                  onToggleHideBalance={handleToggleHideBalance}
                  onOpenAddTx={() => {
                    setTxModalInitial(null);
                    setIsTxModalOpen(true);
                  }}
                  onOpenAddIncome={() => {
                    setTxModalInitial({ type: 'INCOME' });
                    setIsTxModalOpen(true);
                  }}
                  onOpenAddExpense={() => {
                    setTxModalInitial({ type: 'EXPENSE' });
                    setIsTxModalOpen(true);
                  }}
                  onOpenAccounts={() => setIsAccModalOpen(true)}
                  onOpenSettings={() => setIsSettingsModalOpen(true)}
                  onOpenDebts={() => setActiveTab('debts')}
                  onOpenSavings={() => setActiveTab('savings')}
                  onOpenNewSavingsGoal={() => {
                    setSavingsGoalToEdit(null);
                    setIsSavingsModalOpen(true);
                  }}
                  onDeleteTx={handleDeleteTransaction}
                  onEditTx={handleEditTransaction}
                  onDuplicateTx={handleDuplicateTransaction}
                  safeBudget={safeBudget}
                  onSetBudget={handleSetBudget}
                  savingsGoals={savingsGoals}
                  debts={debts}
                  onSelectQuickExpense={handleQuickExpenseSelect}
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
                  onOpenNewGoal={() => {
                    setSavingsGoalToEdit(null);
                    setIsSavingsModalOpen(true);
                  }}
                  onEditGoal={(g) => {
                    setSavingsGoalToEdit(g);
                    setIsSavingsModalOpen(true);
                  }}
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
            onClose={() => setIsTxModalOpen(false)}
            initialData={txModalInitial}
            accounts={accounts}
            onAddTransaction={handleAddTransaction}
          />

          <AccountsManagerModal
            isOpen={isAccModalOpen}
            onClose={() => setIsAccModalOpen(false)}
            accounts={accounts}
            transactions={transactions}
            onAddAccount={handleAddAccount}
            onDeleteAccount={handleDeleteAccount}
            onEditAccount={handleEditAccount}
          />

          <SavingsGoalModal
            isOpen={isSavingsModalOpen}
            onClose={() => setIsSavingsModalOpen(false)}
            onSaveGoal={handleSaveGoal}
            onDepositGoal={handleDepositGoal}
            goalToEdit={savingsGoalToEdit}
            accounts={accounts}
          />

          <SettingsModal
            isOpen={isSettingsModalOpen}
            onClose={() => setIsSettingsModalOpen(false)}
            userProfile={{ name, username, avatar }}
            onUpdateProfile={handleUpdateProfile}
            onHardReset={handleHardReset}
            onImportData={handleImportData}
            onExportData={handleExportData}
            theme={theme}
            onToggleTheme={toggleTheme}
          />
        </div>
      );
    };

    const rootElement = document.getElementById('root');
    ReactDOM.render(
      <ErrorBoundary>
        <App />
      </ErrorBoundary>,
      rootElement
    );
  </script>
</body>
</html>
"""
