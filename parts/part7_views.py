PART7_VIEWS = """
    // =========================================================================
    // 7. VIEWS: SAVINGS GOALS, ANALYTICS & FLOATING CAPSULE NAVIGATION
    // =========================================================================
    const SavingsView = ({ savingsGoals, onOpenNewGoal, onEditGoal, onDeleteGoal, onDepositGoal, hideBalance }) => {
      const [depositGoal, setDepositGoal] = useState(null);
      const [depositAmount, setDepositAmount] = useState('');
      const [depositMode, setDepositMode] = useState('DEPOSIT'); // DEPOSIT | WITHDRAW

      const safeGoals = Array.isArray(savingsGoals) ? savingsGoals : [];

      const handleDepositSubmit = (e) => {
        e.preventDefault();
        const amt = parseRawNumber(depositAmount);
        if (amt <= 0 || !depositGoal) return;
        onDepositGoal(depositGoal.id, amt, depositMode);
        setDepositGoal(null);
        setDepositAmount('');
      };

      return (
        <div className="space-y-4 pb-28 animate-ios-tab-view">
          <div className="flex items-center justify-between pt-1">
            <div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">Kantong Impian</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Wujudkan target tabungan kamu</p>
            </div>
            <button
              type="button"
              onClick={onOpenNewGoal}
              className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-2xl flex items-center gap-1.5 shadow-sm ios-btn-tap"
            >
              <Icon name="plus" className="w-4 h-4" strokeWidth={2.6} />
              <span>Tambah Kantong</span>
            </button>
          </div>

          {safeGoals.length === 0 ? (
            <div className="ios-inset-group text-center py-10">
              <IconBadge icon="target" className="w-14 h-14 rounded-2xl bg-emerald-50 dark:bg-slate-800 text-emerald-600 mx-auto mb-3 shadow-sm" iconClass="w-7 h-7" />
              <h3 className="text-sm font-bold text-slate-800 dark:text-white">Belum Ada Kantong Impian</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xs mx-auto mb-4">
                Beli gadget baru, liburan, motor, atau dana darurat? Buat target impian pertamamu sekarang.
              </p>
              <button
                type="button"
                onClick={onOpenNewGoal}
                className="inline-flex items-center gap-2 px-5 py-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition-all ios-btn-tap mx-auto"
              >
                <Icon name="plus" className="w-4 h-4" strokeWidth={2.5} />
                <span>+ Tambah Kantong Impian Pertama</span>
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {safeGoals.map(goal => {
                const target = Number(goal.targetAmount) || 1;
                const current = Number(goal.currentAmount) || 0;
                const pct = Math.min(100, Math.round((current / target) * 100));

                return (
                  <div key={goal.id} className="ios-inset-group">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2.5">
                        <IconBadge icon="target" className="p-2 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400" />
                        <div>
                          <h3 className="text-xs font-bold text-slate-900 dark:text-white">{goal.title}</h3>
                          <p className="text-[11px] text-slate-400">
                            {goal.targetDate ? `Target: ${formatDateID(goal.targetDate)}` : 'Target fleksibel'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => onEditGoal(goal)}
                          className="p-1.5 text-slate-400 hover:text-brand rounded-lg ios-btn-tap"
                          title="Edit"
                        >
                          <Icon name="edit" className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => onDeleteGoal(goal.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg ios-btn-tap"
                          title="Hapus"
                        >
                          <Icon name="trash" className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <div className="flex items-baseline justify-between mb-1.5">
                      <span className="text-sm font-bold text-brand dark:text-sky-400">
                        {hideBalance ? 'Rp ••••••' : formatIDR(current)}
                      </span>
                      <span className="text-xs text-slate-400">
                        dari {hideBalance ? 'Rp ••••••' : formatIDR(target)} ({pct}%)
                      </span>
                    </div>

                    <div className="w-full h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden mb-3">
                      <div
                        className="h-full bg-brand rounded-full transition-all duration-300"
                        style={{ width: `${pct}%` }}
                      />
                    </div>

                    <div className="flex gap-2 pt-1 border-t border-slate-100 dark:border-slate-700">
                      <button
                        type="button"
                        onClick={() => {
                          setDepositGoal(goal);
                          setDepositMode('DEPOSIT');
                          setDepositAmount('');
                        }}
                        className="flex-1 py-1.5 rounded-xl bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400 text-xs font-semibold hover:bg-sky-100 dark:hover:bg-slate-600 transition-colors ios-btn-tap"
                      >
                        + Setor Tabungan
                      </button>
                      {current > 0 && (
                        <button
                          type="button"
                          onClick={() => {
                            setDepositGoal(goal);
                            setDepositMode('WITHDRAW');
                            setDepositAmount('');
                          }}
                          className="flex-1 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-xs font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors ios-btn-tap"
                        >
                          - Tarik Saldo
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}

              {/* Explicit button to add more goals at the bottom of the list */}
              <button
                type="button"
                onClick={onOpenNewGoal}
                className="w-full py-3.5 border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand rounded-2xl flex items-center justify-center gap-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-brand transition-all ios-btn-tap bg-white/60 dark:bg-slate-850/60 shadow-sm"
              >
                <Icon name="plus" className="w-4 h-4" strokeWidth={2.5} />
                <span>+ Tambah Kantong Impian Baru</span>
              </button>
            </div>
          )}

          {/* Deposit/Withdraw Mini Modal */}
          {depositGoal && (
            <div className="ios-modal-backdrop animate-ios-backdrop" onClick={(e) => { if (e.target === e.currentTarget) setDepositGoal(null); }}>
              <div className="ios-modal-card bg-white dark:bg-slate-800 p-5 animate-ios-sheet max-w-sm mx-auto rounded-[24px]">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    {depositMode === 'DEPOSIT' ? 'Setor Tabungan' : 'Tarik Saldo Impian'}
                  </h3>
                  <button
                    type="button"
                    onClick={() => setDepositGoal(null)}
                    className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors ios-btn-tap shrink-0"
                    aria-label="Tutup"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 flex-shrink-0 aspect-square">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>

                <form onSubmit={handleDepositSubmit} className="space-y-4 pt-3">
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Target: <span className="font-semibold text-slate-800 dark:text-slate-200">{depositGoal.title}</span>
                  </p>

                  <div>
                    <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 block mb-1">Nominal (Rp)</label>
                    <input
                      type="text"
                      inputMode="numeric"
                      required
                      value={depositAmount ? formatIDR(parseRawNumber(depositAmount)) : ''}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => {
                        const num = parseRawNumber(e.target.value);
                        setDepositAmount(num ? num.toString() : '');
                      }}
                      placeholder="Rp 0"
                      className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-bold text-slate-900 dark:text-white focus:outline-none focus:border-brand"
                      autoFocus
                    />
                  </div>

                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => setDepositGoal(null)}
                      className="flex-1 py-2.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-xs font-semibold rounded-xl ios-btn-tap"
                    >
                      Batal
                    </button>
                    <button
                      type="submit"
                      className="flex-1 py-2.5 bg-[#0284C7] text-white text-xs font-semibold rounded-xl hover:bg-[#0369A1] ios-btn-tap"
                    >
                      Konfirmasi
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      );
    };

    // =========================================================================
    // ANALYTICS VIEW WITH RESPONSIVE INLINE SVG CHARTS & COMPREHENSIVE STATS
    // =========================================================================
    const DONUT_COLORS = [
      '#0284C7', // Sky brand
      '#38BDF8', // Light sky
      '#0D9488', // Teal
      '#F59E0B', // Amber
      '#6366F1', // Indigo
      '#EC4899', // Pink
      '#8B5CF6', // Purple
      '#10B981', // Emerald
      '#64748B'  // Slate
    ];

    const AnalyticsView = ({ transactions = [], accounts = [], debts = [], savingsGoals = [], hideBalance, customCategories = [] }) => {
      const [trendMode, setTrendMode] = useState('MONTHLY'); // MONTHLY (last 6 months) | YEARLY
      const [selectedCatId, setSelectedCatId] = useState(null);
      const safeTxs = Array.isArray(transactions) ? transactions : [];
      const safeDebts = Array.isArray(debts) ? debts : [];
      const safeGoals = Array.isArray(savingsGoals) ? savingsGoals : [];

      // Compute Trend Data for last 6 months or 4 years
      const trendData = useMemo(() => {
        const now = new Date();
        const periods = [];

        if (trendMode === 'MONTHLY') {
          for (let i = 5; i >= 0; i--) {
            const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const prefix = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            const label = d.toLocaleDateString('id-ID', { month: 'short' });
            periods.push({ key: prefix, label, income: 0, expense: 0 });
          }
        } else {
          for (let i = 3; i >= 0; i--) {
            const yr = now.getFullYear() - i;
            const prefix = String(yr);
            periods.push({ key: prefix, label: String(yr), income: 0, expense: 0 });
          }
        }

        safeTxs.forEach(t => {
          if (!t || !t.date) return;
          periods.forEach(p => {
            if (t.date.startsWith(p.key)) {
              const amt = Number(t.amount) || 0;
              if (t.type === 'INCOME') p.income += amt;
              else if (t.type === 'EXPENSE') p.expense += amt;
            }
          });
        });

        return periods;
      }, [safeTxs, trendMode]);

      // Max value for chart scaling
      const maxVal = useMemo(() => {
        let m = 0;
        trendData.forEach(p => {
          if (p.income > m) m = p.income;
          if (p.expense > m) m = p.expense;
        });
        return m > 0 ? m * 1.15 : 100000;
      }, [trendData]);

      // SVG line chart dimensions
      const chartW = 320;
      const chartH = 140;
      const padX = 24;
      const padY = 20;
      const innerW = chartW - padX * 2;
      const innerH = chartH - padY * 2;

      const getPoints = useCallback((key) => {
        const n = trendData.length;
        if (n === 0) return '';
        return trendData.map((d, i) => {
          const x = padX + (i / (n - 1 || 1)) * innerW;
          const y = chartH - padY - ((d[key] || 0) / maxVal) * innerH;
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        }).join(' ');
      }, [trendData, maxVal, innerW, innerH]);

      const incomePoints = useMemo(() => getPoints('income'), [getPoints]);
      const expensePoints = useMemo(() => getPoints('expense'), [getPoints]);

      // Category breakdown for current transactions
      const { categoryBreakdown, totalExpense } = useMemo(() => {
        const map = {};
        let sum = 0;

        safeTxs.forEach(t => {
          if (!t || t.type !== 'EXPENSE') return;
          const amt = Number(t.amount) || 0;
          sum += amt;
          map[t.category] = (map[t.category] || 0) + amt;
        });

        const list = Object.entries(map).map(([catId, amount], idx) => {
          const catInfo = getCategoryById(catId, customCategories);
          const pct = sum > 0 ? Math.round((amount / sum) * 100) : 0;
          return {
            id: catId,
            label: catInfo.label,
            icon: catInfo.icon,
            amount,
            percentage: pct,
            color: DONUT_COLORS[idx % DONUT_COLORS.length]
          };
        });

        return {
          categoryBreakdown: list.sort((a, b) => b.amount - a.amount),
          totalExpense: sum
        };
      }, [safeTxs, customCategories]);

      // Donut Chart SVG Segments
      const donutSegments = useMemo(() => {
        const r = 38;
        const circumference = 2 * Math.PI * r;
        let cumulativePct = 0;

        return categoryBreakdown.map(item => {
          const strokeDasharray = `${(item.percentage / 100) * circumference} ${circumference}`;
          const strokeDashoffset = -((cumulativePct / 100) * circumference);
          cumulativePct += item.percentage;

          return {
            ...item,
            strokeDasharray,
            strokeDashoffset,
            r
          };
        });
      }, [categoryBreakdown]);

      // Selected or Top Category for Donut Center
      const activeDonutInfo = useMemo(() => {
        if (selectedCatId) {
          const found = categoryBreakdown.find(c => c.id === selectedCatId);
          if (found) return { label: found.label, amount: found.amount, percentage: found.percentage, color: found.color };
        }
        return { label: 'Total Keluar', amount: totalExpense, percentage: 100, color: '#0284C7' };
      }, [selectedCatId, categoryBreakdown, totalExpense]);

      // Cashflow Summary Totals
      const totals = useMemo(() => Ledger.getSummaryTotals(safeTxs), [safeTxs]);

      // Debt & Receivable Statistics
      const debtStats = useMemo(() => {
        let totalHutang = 0;
        let totalPiutang = 0;
        let settledCount = 0;
        let pendingCount = 0;
        let settledAmount = 0;
        let pendingAmount = 0;

        safeDebts.forEach(d => {
          const amt = Number(d.amount) || 0;
          if (d.type === 'HUTANG') totalHutang += amt;
          else if (d.type === 'PIUTANG') totalPiutang += amt;

          if (d.status === 'LUNAS') {
            settledCount++;
            settledAmount += amt;
          } else {
            pendingCount++;
            pendingAmount += amt;
          }
        });

        const totalAll = totalHutang + totalPiutang;
        const repaymentRate = totalAll > 0 ? Math.round((settledAmount / totalAll) * 100) : 0;

        return {
          totalHutang,
          totalPiutang,
          settledCount,
          pendingCount,
          settledAmount,
          pendingAmount,
          totalCount: safeDebts.length,
          repaymentRate
        };
      }, [safeDebts]);

      // Savings & Goals Statistics
      const savingsStats = useMemo(() => {
        let totalSaved = 0;
        let totalTarget = 0;
        let completedCount = 0;
        let earliestDate = Date.now();

        safeGoals.forEach(g => {
          const cur = Number(g.currentAmount) || 0;
          const tgt = Number(g.targetAmount) || 0;
          totalSaved += cur;
          totalTarget += tgt;
          if (tgt > 0 && cur >= tgt) completedCount++;

          if (g.createdAt) {
            const t = new Date(g.createdAt).getTime();
            if (!isNaN(t) && t < earliestDate) earliestDate = t;
          }
        });

        const overallRate = totalTarget > 0 ? Math.min(100, Math.round((totalSaved / totalTarget) * 100)) : 0;
        const daysElapsed = Math.max(1, Math.round((Date.now() - earliestDate) / (1000 * 60 * 60 * 24)));
        const monthsElapsed = Math.max(1, Math.round(daysElapsed / 30.4));
        const monthlyVelocity = totalSaved > 0 ? Math.round(totalSaved / monthsElapsed) : 0;

        return {
          totalSaved,
          totalTarget,
          completedCount,
          activeCount: safeGoals.length - completedCount,
          overallRate,
          monthlyVelocity
        };
      }, [safeGoals]);

      return (
        <div className="space-y-4 pb-28 animate-ios-tab-view select-none">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Analisis & Tren Keuangan</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Statistik arus kas, hutang, dan impian</p>
            </div>
          </div>

          {/* Segmented Control for Trend Period */}
          <SegmentedControl
            options={[
              { value: 'MONTHLY', label: '6 Bulan Terakhir' },
              { value: 'YEARLY', label: 'Tren Tahunan' }
            ]}
            value={trendMode}
            onChange={setTrendMode}
            className="w-full"
          />

          {/* SVG Trend Line Chart */}
          <div className="ios-inset-group">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Tren Pemasukan vs Pengeluaran
              </span>
              <div className="flex items-center gap-3 text-[11px] font-semibold">
                <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  Masuk
                </span>
                <span className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  Keluar
                </span>
              </div>
            </div>

            {/* Inline SVG Line Chart */}
            <div className="w-full overflow-hidden">
              <svg viewBox={`0 0 ${chartW} ${chartH}`} className="w-full h-40 overflow-visible">
                {/* Baseline Grid lines */}
                <line x1={padX} y1={chartH - padY} x2={chartW - padX} y2={chartH - padY} stroke="#E2E8F0" strokeWidth="1" strokeDasharray="3 3" />
                <line x1={padX} y1={chartH - padY - innerH / 2} x2={chartW - padX} y2={chartH - padY - innerH / 2} stroke="#E2E8F0" strokeWidth="1" strokeDasharray="3 3" />
                <line x1={padX} y1={padY} x2={chartW - padX} y2={padY} stroke="#E2E8F0" strokeWidth="1" strokeDasharray="3 3" />

                {/* Income Polyline */}
                {incomePoints && (
                  <polyline
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={incomePoints}
                  />
                )}

                {/* Expense Polyline */}
                {expensePoints && (
                  <polyline
                    fill="none"
                    stroke="#F43F5E"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={expensePoints}
                  />
                )}

                {/* Data Points */}
                {trendData.map((d, i) => {
                  const n = trendData.length;
                  const x = padX + (i / (n - 1 || 1)) * innerW;
                  const yInc = chartH - padY - ((d.income || 0) / maxVal) * innerH;
                  const yExp = chartH - padY - ((d.expense || 0) / maxVal) * innerH;

                  return (
                    <g key={d.key}>
                      <circle cx={x} cy={yInc} r="3.5" fill="#10B981" stroke="#FFFFFF" strokeWidth="1.5" />
                      <circle cx={x} cy={yExp} r="3.5" fill="#F43F5E" stroke="#FFFFFF" strokeWidth="1.5" />
                      <text
                        x={x}
                        y={chartH - 4}
                        textAnchor="middle"
                        fontSize="9"
                        fill="#94A3B8"
                        fontWeight="600"
                      >
                        {d.label}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Cashflow Summary Card */}
          <div className="ios-inset-group grid grid-cols-3 gap-2 text-center">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-500 block mb-1">Pemasukan</span>
              <div className="text-xs font-bold text-slate-900 dark:text-white">
                {hideBalance ? 'Rp ••••••' : formatIDR(totals.income)}
              </div>
            </div>
            <div className="border-x border-slate-100 dark:border-slate-700">
              <span className="text-[10px] font-bold uppercase tracking-wider text-rose-500 block mb-1">Pengeluaran</span>
              <div className="text-xs font-bold text-slate-900 dark:text-white">
                {hideBalance ? 'Rp ••••••' : formatIDR(totals.expense)}
              </div>
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#0284C7] dark:text-[#38BDF8] block mb-1">Arus Bersih</span>
              <div className={`text-xs font-bold ${totals.net >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                {hideBalance ? 'Rp ••••••' : formatIDR(totals.net)}
              </div>
            </div>
          </div>

          {/* INTERACTIVE SVG PIE / DONUT CHART FOR EXPENSES */}
          <div className="ios-inset-group">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Proporsi Kategori Pengeluaran
              </h3>
              {selectedCatId && (
                <button
                  type="button"
                  onClick={() => setSelectedCatId(null)}
                  className="text-[11px] font-semibold text-[#0284C7] dark:text-[#38BDF8] hover:underline"
                >
                  Lihat Semua
                </button>
              )}
            </div>

            {categoryBreakdown.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-8">Belum ada pengeluaran yang tercatat.</p>
            ) : (
              <div>
                {/* Inline SVG Donut Chart */}
                <div className="relative flex items-center justify-center my-3">
                  <svg viewBox="0 0 100 100" className="w-44 h-44 -rotate-90 transform">
                    {/* Background Track */}
                    <circle
                      cx="50"
                      cy="50"
                      r="38"
                      fill="none"
                      stroke="#E2E8F0"
                      strokeWidth="12"
                      className="dark:stroke-slate-700"
                    />
                    {/* Donut Segments */}
                    {donutSegments.map(seg => {
                      const isSelected = selectedCatId === seg.id;
                      return (
                        <circle
                          key={seg.id}
                          cx="50"
                          cy="50"
                          r="38"
                          fill="none"
                          stroke={seg.color}
                          strokeWidth={isSelected ? "14" : "12"}
                          strokeDasharray={seg.strokeDasharray}
                          strokeDashoffset={seg.strokeDashoffset}
                          className="cursor-pointer transition-all duration-300 hover:opacity-90"
                          onClick={() => setSelectedCatId(seg.id === selectedCatId ? null : seg.id)}
                        />
                      );
                    })}
                  </svg>

                  {/* Donut Center Display */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none p-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 line-clamp-1">
                      {activeDonutInfo.label}
                    </span>
                    <span className="text-xs font-black text-slate-900 dark:text-white mt-0.5">
                      {hideBalance ? 'Rp ••••••' : formatIDR(activeDonutInfo.amount)}
                    </span>
                    <span className="text-[10px] font-bold text-[#0284C7] dark:text-[#38BDF8] mt-0.5">
                      {activeDonutInfo.percentage}%
                    </span>
                  </div>
                </div>

                {/* Category Breakdown List */}
                <div className="space-y-2.5 mt-4 pt-3 border-t border-slate-100 dark:border-slate-700/60">
                  {categoryBreakdown.map(item => {
                    const isSelected = selectedCatId === item.id;
                    return (
                      <div
                        key={item.id}
                        onClick={() => setSelectedCatId(isSelected ? null : item.id)}
                        className={`p-2 rounded-xl transition-all cursor-pointer ${
                          isSelected ? 'bg-sky-50 dark:bg-slate-700/80 border border-sky-200 dark:border-sky-500/50' : 'hover:bg-slate-50 dark:hover:bg-slate-700/40'
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs mb-1.5">
                          <div className="flex items-center gap-2">
                            <span
                              className="w-3 h-3 rounded-full flex-shrink-0"
                              style={{ backgroundColor: item.color }}
                            />
                            <span className="font-bold text-slate-800 dark:text-slate-200">{item.label}</span>
                          </div>
                          <div className="text-right flex items-center gap-2">
                            <span className="font-extrabold text-slate-900 dark:text-white">
                              {hideBalance ? 'Rp ••••••' : formatIDR(item.amount)}
                            </span>
                            <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded-full">
                              {item.percentage}%
                            </span>
                          </div>
                        </div>
                        <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all duration-300"
                            style={{ width: `${item.percentage}%`, backgroundColor: item.color }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* STATISTIK HUTANG & PIUTANG (DEBTS & RECEIVABLES SUITE) */}
          <div className="ios-inset-group space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Statistik Hutang & Piutang
              </h3>
              <span className="text-[10px] font-bold text-slate-400">
                {debtStats.totalCount} Catatan Total
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="p-2.5 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/50">
                <span className="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400 block mb-0.5">
                  Total Hutang
                </span>
                <div className="text-xs font-extrabold text-rose-700 dark:text-rose-300">
                  {hideBalance ? 'Rp ••••••' : formatIDR(debtStats.totalHutang)}
                </div>
              </div>
              <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/50">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 block mb-0.5">
                  Total Piutang
                </span>
                <div className="text-xs font-extrabold text-emerald-700 dark:text-emerald-300">
                  {hideBalance ? 'Rp ••••••' : formatIDR(debtStats.totalPiutang)}
                </div>
              </div>
            </div>

            {/* Repayment Breakdown Card */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-700/60 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-600 dark:text-slate-300">Tingkat Kelunasan</span>
                <span className="font-bold text-[#0284C7] dark:text-[#38BDF8]">{debtStats.repaymentRate}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#0284C7] dark:bg-[#38BDF8] rounded-full transition-all duration-300"
                  style={{ width: `${debtStats.repaymentRate}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-0.5">
                <span>{debtStats.settledCount} Lunas ({hideBalance ? '••••' : formatIDR(debtStats.settledAmount)})</span>
                <span>{debtStats.pendingCount} Belum Lunas ({hideBalance ? '••••' : formatIDR(debtStats.pendingAmount)})</span>
              </div>
            </div>
          </div>

          {/* STATISTIK KANTONG IMPIAN (SAVINGS & GOALS VELOCITY) */}
          <div className="ios-inset-group space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Statistik Kantong Impian
              </h3>
              <span className="text-[10px] font-bold text-slate-400">
                {savingsStats.completedCount} / {safeGoals.length} Tercapai
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-center">
              <div className="p-2.5 rounded-xl bg-sky-50 dark:bg-slate-700/60 border border-sky-100 dark:border-slate-600">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#0284C7] dark:text-[#38BDF8] block mb-0.5">
                  Terkumpul
                </span>
                <div className="text-xs font-extrabold text-slate-900 dark:text-white">
                  {hideBalance ? 'Rp ••••••' : formatIDR(savingsStats.totalSaved)}
                </div>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-700/60 border border-slate-200/80 dark:border-slate-600">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 block mb-0.5">
                  Target Total
                </span>
                <div className="text-xs font-extrabold text-slate-900 dark:text-white">
                  {hideBalance ? 'Rp ••••••' : formatIDR(savingsStats.totalTarget)}
                </div>
              </div>
            </div>

            {/* Overall Progress Meter */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-700/60 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-600 dark:text-slate-300">Pencapaian Target Keseluruhan</span>
                <span className="font-bold text-[#0284C7] dark:text-[#38BDF8]">{savingsStats.overallRate}%</span>
              </div>
              <div className="w-full h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#0284C7] dark:bg-[#38BDF8] rounded-full transition-all duration-300"
                  style={{ width: `${savingsStats.overallRate}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-0.5">
                <span>{savingsStats.activeCount} Impian Aktif Berjalan</span>
                <span>{savingsStats.completedCount} Target Tercapai</span>
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-700/50">
                <span>Kecepatan Setoran Rata-rata:</span>
                <span className="font-bold text-[#0284C7] dark:text-[#38BDF8]">
                  {hideBalance ? '••••' : formatIDR(savingsStats.monthlyVelocity)} / bulan
                </span>
              </div>
            </div>
          </div>
        </div>
      );
    };

    // =========================================================================
    // 8. FLOATING CAPSULE NAVIGATION (WITH TOUCH DRAG MECHANICS)
    // =========================================================================
    const FloatingCapsuleNav = ({ currentTab, onSelectTab }) => {
      const tabs = [
        { id: 'dashboard', label: 'Ringkasan', icon: 'wallet' },
        { id: 'debts', label: 'Hutang', icon: 'receipt' },
        { id: 'savings', label: 'Impian', icon: 'target' },
        { id: 'analytics', label: 'Statistik', icon: 'pie-chart' }
      ];

      const navRef = useRef(null);
      const isDragging = useRef(false);
      const activeIndex = Math.max(0, tabs.findIndex(t => t.id === currentTab));

      const updateTabFromCoord = (clientX) => {
        if (!navRef.current) return;
        const rect = navRef.current.getBoundingClientRect();
        const relX = clientX - rect.left;
        const fraction = Math.max(0, Math.min(0.999, relX / rect.width));
        const tabIndex = Math.floor(fraction * tabs.length);
        if (tabs[tabIndex] && tabs[tabIndex].id !== currentTab) {
          onSelectTab(tabs[tabIndex].id);
        }
      };

      const handleTouchStart = (e) => {
        if (!e.touches || e.touches.length === 0) return;
        isDragging.current = true;
        updateTabFromCoord(e.touches[0].clientX);
      };

      const handleTouchMove = (e) => {
        if (!isDragging.current || !e.touches || e.touches.length === 0) return;
        updateTabFromCoord(e.touches[0].clientX);
      };

      const handleTouchEnd = () => {
        isDragging.current = false;
      };

      const handleMouseDown = (e) => {
        isDragging.current = true;
        updateTabFromCoord(e.clientX);
      };

      const handleMouseMove = (e) => {
        if (!isDragging.current) return;
        updateTabFromCoord(e.clientX);
      };

      const handleMouseUp = () => {
        isDragging.current = false;
      };

      return (
        <nav
          ref={navRef}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="fixed bottom-5 left-0 right-0 z-50 w-[92%] max-w-[360px] h-14 mx-auto rounded-full bg-[#FFFFFF] dark:bg-[#1E293B] border border-slate-200 dark:border-[#334155] shadow-[0_12px_32px_rgba(15,23,42,0.18)] dark:shadow-[0_16px_36px_rgba(0,0,0,0.6)] flex items-center p-1.5 select-none touch-none"
        >
          {/* Active Sliding Pill - Smooth Apple Spring Curve */}
          <div
            className="absolute top-1.5 bottom-1.5 rounded-full bg-[#0284C7] dark:bg-[#38BDF8] shadow-sm pointer-events-none transition-all duration-300"
            style={{
              left: `calc(${activeIndex * 25}% + 4px)`,
              width: 'calc(25% - 8px)',
              transitionTimingFunction: 'cubic-bezier(0.32, 0.72, 0, 1)'
            }}
          />

          {tabs.map((t, idx) => {
            const isActive = idx === activeIndex;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => onSelectTab(t.id)}
                className="flex-1 h-full relative z-10 flex items-center justify-center rounded-full transition-colors duration-200 ios-btn-tap"
              >
                <Icon
                  name={t.icon}
                  className={`w-5 h-5 flex-shrink-0 aspect-square ${isActive ? 'text-white dark:text-[#0F172A]' : 'text-slate-500 dark:text-slate-400'}`}
                  strokeWidth={isActive ? 2.4 : 1.8}
                />
                {isActive && (
                  <span className="whitespace-nowrap font-bold text-xs text-white dark:text-[#0F172A] ml-1.5 hidden min-[320px]:inline">
                    {t.label}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      );
    };
"""
