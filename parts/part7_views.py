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
        HapticFeedback.save();
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

          if (d.status === 'LUNAS' || d.isPaid) {
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
    // DEDICATED CARDS / WALLET VIEW (TAB 2 - KANTONG KEUANGAN)
    // =========================================================================
    const CardsView = ({
      accounts = [],
      transactions = [],
      hideBalance = false,
      onToggleHideBalance,
      onAddAccount,
      onUpdateAccount,
      onDeleteAccount,
      onReorderAccounts,
      onOpenAddTx,
      onToast
    }) => {
      const [isAdding, setIsAdding] = useState(false);
      const [editingAcc, setEditingAcc] = useState(null);
      const [name, setName] = useState('');
      const [type, setType] = useState('Bank');
      const [initialBalance, setInitialBalance] = useState('');
      const [color, setColor] = useState('#0284C7');
      const [expandedCardId, setExpandedCardId] = useState(null);

      // Drag and drop reordering state
      const [draggedId, setDraggedId] = useState(null);
      const [dragOverId, setDragOverId] = useState(null);
      const [dragPosition, setDragPosition] = useState(null); // 'before' | 'after'
      const isDraggingRef = useRef(false);
      const justDraggedRef = useRef(false);
      const cardRefs = useRef({});
      const touchStateRef = useRef(null);

      const safeAccounts = Array.isArray(accounts) ? accounts : [];
      const safeTransactions = Array.isArray(transactions) ? transactions : [];

      // Reorder account programmatically (e.g. Move up/down/top)
      const handleMoveAccount = useCallback((accId, direction) => {
        const idx = safeAccounts.findIndex(a => a.id === accId);
        if (idx === -1) return;
        const next = [...safeAccounts];
        const [moved] = next.splice(idx, 1);
        if (direction === 'top') {
          next.unshift(moved);
        } else if (direction === 'up' && idx > 0) {
          next.splice(idx - 1, 0, moved);
        } else if (direction === 'down' && idx < safeAccounts.length - 1) {
          next.splice(idx + 1, 0, moved);
        } else {
          return;
        }
        if (onReorderAccounts) {
          onReorderAccounts(next);
        }
        if (window.VoraletHaptics?.notification) {
          window.VoraletHaptics.notification('success');
        } else if (window.VoraletHaptics?.tap) {
          window.VoraletHaptics.tap();
        }
      }, [safeAccounts, onReorderAccounts]);

      // Pointer & Touch drag handler for mobile WebView and desktop
      const handleDragHandlePointerDown = useCallback((accId, e) => {
        if (e.button !== 0 && e.pointerType === 'mouse') return;
        e.stopPropagation();

        setExpandedCardId(null);
        const pointerId = e.pointerId;
        const startY = e.clientY;
        const startX = e.clientX;

        if (window.VoraletHaptics?.tap) {
          window.VoraletHaptics.tap();
        }

        touchStateRef.current = {
          accId,
          pointerId,
          startY,
          startX,
          isStarted: false
        };

        const handlePointerMove = (moveEv) => {
          if (!touchStateRef.current || touchStateRef.current.pointerId !== moveEv.pointerId) return;
          const deltaY = moveEv.clientY - touchStateRef.current.startY;
          const deltaX = moveEv.clientX - touchStateRef.current.startX;

          if (!touchStateRef.current.isStarted) {
            if (Math.abs(deltaY) > 6 || Math.abs(deltaX) > 6) {
              touchStateRef.current.isStarted = true;
              isDraggingRef.current = true;
              setDraggedId(accId);
              if (window.VoraletHaptics?.selection) {
                window.VoraletHaptics.selection();
              }
            } else {
              return;
            }
          }

          if (moveEv.cancelable) {
            moveEv.preventDefault();
          }

          const currentClientY = moveEv.clientY;
          let foundId = null;
          let foundPos = null;

          for (const a of safeAccounts) {
            const el = cardRefs.current[a.id];
            if (!el) continue;
            const rect = el.getBoundingClientRect();
            if (currentClientY >= rect.top && currentClientY <= rect.bottom) {
              foundId = a.id;
              const midY = rect.top + rect.height / 2;
              foundPos = currentClientY < midY ? 'before' : 'after';
              break;
            }
          }

          if (foundId) {
            setDragOverId(foundId);
            setDragPosition(foundPos);
          }
        };

        const handlePointerUp = (upEv) => {
          if (!touchStateRef.current || touchStateRef.current.pointerId !== upEv.pointerId) return;

          window.removeEventListener('pointermove', handlePointerMove);
          window.removeEventListener('pointerup', handlePointerUp);
          window.removeEventListener('pointercancel', handlePointerUp);

          const wasStarted = touchStateRef.current.isStarted;
          touchStateRef.current = null;

          if (wasStarted) {
            justDraggedRef.current = true;
            setTimeout(() => {
              justDraggedRef.current = false;
            }, 300);

            setDraggedId(currDragged => {
              setDragOverId(currOver => {
                setDragPosition(currPos => {
                  if (currDragged && currOver && currDragged !== currOver) {
                    const fromIdx = safeAccounts.findIndex(a => a.id === currDragged);
                    const toIdx = safeAccounts.findIndex(a => a.id === currOver);
                    if (fromIdx !== -1 && toIdx !== -1) {
                      const next = [...safeAccounts];
                      const [moved] = next.splice(fromIdx, 1);
                      const finalIdx = next.findIndex(a => a.id === currOver);
                      const insertIdx = currPos === 'after' ? finalIdx + 1 : finalIdx;
                      next.splice(insertIdx, 0, moved);

                      if (onReorderAccounts) {
                        onReorderAccounts(next);
                      }
                      if (window.VoraletHaptics?.notification) {
                        window.VoraletHaptics.notification('success');
                      } else if (window.VoraletHaptics?.tap) {
                        window.VoraletHaptics.tap();
                      }
                    }
                  }
                  return null;
                });
                return null;
              });
              return null;
            });
            isDraggingRef.current = false;
          }
        };

        window.addEventListener('pointermove', handlePointerMove, { passive: false });
        window.addEventListener('pointerup', handlePointerUp);
        window.addEventListener('pointercancel', handlePointerUp);
      }, [safeAccounts, onReorderAccounts]);

      // HTML5 Drag and Drop handlers for desktop
      const handleHtmlDragStart = (e, accId) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', accId);
        setDraggedId(accId);
        isDraggingRef.current = true;
        setExpandedCardId(null);
      };

      const handleHtmlDragOver = (e, accId) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const el = cardRefs.current[accId];
        if (el) {
          const rect = el.getBoundingClientRect();
          const midY = rect.top + rect.height / 2;
          const pos = e.clientY < midY ? 'before' : 'after';
          setDragOverId(accId);
          setDragPosition(pos);
        }
      };

      const handleHtmlDrop = (e, targetAccId) => {
        e.preventDefault();
        const sourceAccId = e.dataTransfer.getData('text/plain') || draggedId;
        if (sourceAccId && targetAccId && sourceAccId !== targetAccId) {
          const fromIdx = safeAccounts.findIndex(a => a.id === sourceAccId);
          const toIdx = safeAccounts.findIndex(a => a.id === targetAccId);
          if (fromIdx !== -1 && toIdx !== -1) {
            const next = [...safeAccounts];
            const [moved] = next.splice(fromIdx, 1);
            const finalIdx = next.findIndex(a => a.id === targetAccId);
            const insertIdx = dragPosition === 'after' ? finalIdx + 1 : finalIdx;
            next.splice(insertIdx, 0, moved);
            if (onReorderAccounts) {
              onReorderAccounts(next);
            }
            if (window.VoraletHaptics?.notification) {
              window.VoraletHaptics.notification('success');
            }
          }
        }
        setDraggedId(null);
        setDragOverId(null);
        setDragPosition(null);
        isDraggingRef.current = false;
      };

      const handleHtmlDragEnd = () => {
        setDraggedId(null);
        setDragOverId(null);
        setDragPosition(null);
        isDraggingRef.current = false;
      };

      // Calculate total balance across all pockets
      const totalBalance = useMemo(() => {
        return safeAccounts.reduce((acc, a) => {
          return acc + Ledger.getAccountBalance(a.id, safeAccounts, safeTransactions);
        }, 0);
      }, [safeAccounts, safeTransactions]);

      const handleStartEdit = (acc, e) => {
        if (e) e.stopPropagation();
        setEditingAcc(acc);
        setName(acc.name || '');
        setType(acc.type || 'Bank');
        setInitialBalance(String(acc.initialBalance || '0'));
        setColor(acc.color || '#0284C7');
        setIsAdding(true);
      };

      const handleSave = (e) => {
        if (e) e.preventDefault();
        const cleanName = Validators.sanitizeText(name, 40);
        if (!cleanName) return;

        const numInit = Math.max(0, Validators.sanitizeNumber(initialBalance, 0));

        if (editingAcc) {
          onUpdateAccount({
            ...editingAcc,
            name: cleanName,
            type,
            initialBalance: numInit,
            color
          });
        } else {
          onAddAccount({
            id: 'acc_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
            name: cleanName,
            type,
            initialBalance: numInit,
            color
          });
        }

        setIsAdding(false);
        setEditingAcc(null);
        setName('');
        setInitialBalance('');
      };

      return (
        <div className="space-y-4 pb-24 animate-ios-tab-view">
          {/* Header Title Bar */}
          <div className="flex items-center justify-between pt-1">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">Kantong Keuangan</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Atur rekening bank, e-wallet, dan kas tunai</p>
            </div>
            {!isAdding && (
              <button
                type="button"
                onClick={() => {
                  setEditingAcc(null);
                  setName('');
                  setType('Bank');
                  setInitialBalance('');
                  setColor('#0284C7');
                  setIsAdding(true);
                }}
                className="px-3.5 py-2 bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors ios-btn-tap shadow-xs"
              >
                <Icon name="plus" className="w-3.5 h-3.5" strokeWidth={2.5} />
                <span>Tambah</span>
              </button>
            )}
          </div>

          {/* Total Saldo Semua Kantong Banner (Strict Flat Design) */}
          <div className="bg-[#F0F9FF] dark:bg-slate-800 rounded-2xl border border-sky-100 dark:border-slate-700 p-4 select-none">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-bold tracking-wider text-slate-500 dark:text-slate-400 uppercase">
                TOTAL SALDO SEMUA KANTONG
              </span>
              {onToggleHideBalance && (
                <button
                  type="button"
                  onClick={onToggleHideBalance}
                  className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 rounded-lg ios-btn-tap"
                  title={hideBalance ? 'Tampilkan Saldo' : 'Sembunyikan Saldo'}
                >
                  <Icon name={hideBalance ? 'eye-off' : 'eye'} className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            <div className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              {hideBalance ? 'Rp ••••••••' : formatIDR(totalBalance)}
            </div>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1">
              Terdistribusi di {safeAccounts.length} kantong aktif
            </p>
          </div>

          {/* Inline Add / Edit Form */}
          {isAdding && (
            <form onSubmit={handleSave} className="bg-[#F0F9FF] dark:bg-slate-800 rounded-2xl border border-sky-200 dark:border-slate-700 p-4 space-y-3.5 animate-ios-spring-pop">
              <div className="flex items-center justify-between pb-2 border-b border-sky-100 dark:border-slate-700">
                <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                  {editingAcc ? 'Edit Kantong' : 'Tambah Kantong Baru'}
                </h3>
                <button
                  type="button"
                  onClick={() => {
                    setIsAdding(false);
                    setEditingAcc(null);
                  }}
                  className="text-xs font-semibold text-slate-500 hover:text-slate-700 dark:text-slate-400"
                >
                  Batal
                </button>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">
                  Nama Kantong
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Contoh: BCA Utama, Gopay, Dompet Fisik"
                  className="w-full px-3.5 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#0284C7]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">
                    Jenis Kantong
                  </label>
                  <select
                    value={type}
                    onChange={(e) => setType(e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#0284C7]"
                  >
                    <option value="Bank">Rekening Bank</option>
                    <option value="E-Wallet">E-Wallet</option>
                    <option value="Cash">Kas Tunai</option>
                    <option value="Investasi">Investasi</option>
                  </select>
                </div>

                <div>
                  <label className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 block mb-1">
                    {editingAcc ? 'Saldo Pokok Awal' : 'Saldo Awal'}
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={initialBalance}
                    onChange={(e) => setInitialBalance(e.target.value)}
                    placeholder="0"
                    className="w-full px-3 py-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-[#0284C7]"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-bold rounded-xl transition-colors ios-btn-tap"
              >
                {editingAcc ? 'Simpan Perubahan' : 'Buat Kantong'}
              </button>
            </form>
          )}

          {/* Simplified Pocket Cards List */}
          <div className="space-y-2.5">
            <div className="flex items-center justify-between px-1">
              <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Daftar Kantong ({safeAccounts.length})
              </span>
              {safeAccounts.length > 1 ? (
                <span className="text-[10px] text-slate-400 flex items-center gap-1 font-medium">
                  <Icon name="grip-vertical" className="w-3 h-3 text-sky-500" />
                  <span>Tahan & geser untuk atur prioritas</span>
                </span>
              ) : (
                <span className="text-[10px] text-slate-400">Ketuk kantong untuk mutasi & opsi</span>
              )}
            </div>

            {safeAccounts.length === 0 ? (
              <div className="p-8 text-center bg-[#F0F9FF] dark:bg-slate-800 rounded-2xl border border-sky-100 dark:border-slate-700">
                <Icon name="credit-card" className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-600 dark:text-slate-300">Belum ada kantong</p>
                <p className="text-[11px] text-slate-400 mt-1">Tambahkan kantong pertama Anda untuk mulai mengelola dana.</p>
              </div>
            ) : (
              safeAccounts.map((acc, index) => {
                const bal = Ledger.getAccountBalance(acc.id, safeAccounts, safeTransactions);
                const isExpanded = expandedCardId === acc.id;
                const hasAnySelected = expandedCardId !== null;
                const isDragging = draggedId === acc.id;
                const isDragTarget = dragOverId === acc.id && draggedId !== acc.id;
                const showIndicatorBefore = isDragTarget && dragPosition === 'before';
                const showIndicatorAfter = isDragTarget && dragPosition === 'after';

                const normType = String(acc.type || '').toUpperCase();
                const isCash = normType === 'CASH' || normType === 'TUNAI';
                const isEWallet = normType.includes('WALLET') || normType === 'EWALLET';
                const isInvest = normType === 'INVESTASI';
                const iconName = isCash ? 'cash' : isEWallet ? 'smartphone' : isInvest ? 'award' : 'bank';
                const typeLabel = isCash ? 'Kas Tunai' : isEWallet ? 'E-Wallet' : isInvest ? 'Investasi' : 'Rekening Bank';

                // Get last 4 mutations for this account
                const accountTxs = safeTransactions
                  .filter(tx => tx.accountId === acc.id)
                  .slice(0, 4);

                const maskedNumber = (acc.accountNumber && String(acc.accountNumber).trim())
                  ? `•••• ${String(acc.accountNumber).replace(/\s/g, '').slice(-4)}`
                  : `•••• ${String(acc.id || '8829').replace(/\D/g, '').slice(-4) || '8829'}`;

                return (
                  <React.Fragment key={acc.id}>
                    {showIndicatorBefore && (
                      <div className="ios-card-drop-indicator" />
                    )}
                    <div
                      ref={el => { cardRefs.current[acc.id] = el; }}
                      draggable={safeAccounts.length > 1}
                      onDragStart={(e) => handleHtmlDragStart(e, acc.id)}
                      onDragOver={(e) => handleHtmlDragOver(e, acc.id)}
                      onDrop={(e) => handleHtmlDrop(e, acc.id)}
                      onDragEnd={handleHtmlDragEnd}
                      onClick={() => {
                        if (justDraggedRef.current || isDraggingRef.current) return;
                        if (window.VoraletHaptics) {
                          window.VoraletHaptics.tap();
                        }
                        setExpandedCardId(isExpanded ? null : acc.id);
                      }}
                      className={`relative w-full rounded-2xl bg-[#0284C7] dark:bg-[#0369A1] p-4 text-white select-none cursor-pointer ios-card-stack-item ${
                        isDragging
                          ? 'is-dragging'
                          : isDragTarget
                          ? 'is-drag-target'
                          : isExpanded
                          ? 'is-lifted'
                          : hasAnySelected
                          ? 'is-dimmed'
                          : 'shadow-md hover:shadow-lg'
                      }`}
                    >
                      {/* Top row: Type chip/badge, priority indicator, and drag handle */}
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-xl bg-white/20 border border-white/25 flex items-center justify-center text-white">
                            <Icon name={iconName} className="w-4 h-4" />
                          </div>
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-sky-100 block">
                                {typeLabel}
                              </span>
                              {index === 0 ? (
                                <span className="px-1.5 py-0.5 rounded-full bg-amber-400 text-slate-950 text-[9px] font-extrabold tracking-wide flex items-center gap-0.5 shadow-xs">
                                  <span>★</span>
                                  <span>Utama</span>
                                </span>
                              ) : (
                                <span className="px-1.5 py-0.2 rounded-md bg-white/15 text-sky-100 text-[9px] font-semibold">
                                  #{index + 1}
                                </span>
                              )}
                            </div>
                            <h4 className="text-sm font-extrabold text-white truncate leading-tight">
                              {acc.name}
                            </h4>
                          </div>
                        </div>

                        {/* Right elements: Card number & Drag handle */}
                        <div className="flex items-center gap-2">
                          <div className="px-2 py-0.5 rounded-md bg-white/15 border border-white/20 text-[9px] font-mono font-bold tracking-wider text-sky-100">
                            {maskedNumber}
                          </div>
                          {safeAccounts.length > 1 && (
                            <div
                              role="button"
                              tabIndex={0}
                              title="Tahan & geser untuk mengatur urutan prioritas"
                              aria-label={`Geser untuk atur urutan ${acc.name}`}
                              onPointerDown={(e) => handleDragHandlePointerDown(acc.id, e)}
                              onClick={(e) => e.stopPropagation()}
                              className="p-1.5 -mr-1 rounded-lg text-white/70 hover:text-white hover:bg-white/20 active:bg-white/30 cursor-grab active:cursor-grabbing transition-colors touch-none select-none flex items-center justify-center"
                              style={{ touchAction: 'none' }}
                            >
                              <Icon name="grip-vertical" className="w-4 h-4" />
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Bottom row: Saldo and status */}
                      <div className="pt-2 border-t border-white/15 flex items-end justify-between">
                        <div>
                          <span className="text-[9px] font-semibold uppercase tracking-wider text-sky-200/90 block mb-0.5">
                            Saldo Tersedia
                          </span>
                          <div className="text-lg sm:text-xl font-black tracking-tight text-white">
                            {hideBalance ? 'Rp ••••••••' : formatIDR(bal)}
                          </div>
                        </div>

                        <div className="text-right flex items-center gap-1.5">
                          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-sky-100 bg-white/15 px-2 py-0.5 rounded-lg">
                            <span>{isExpanded ? 'Tutup Opsi' : 'Kelola'}</span>
                            <Icon name={isExpanded ? 'chevron-up' : 'chevron-down'} className="w-3 h-3" />
                          </span>
                        </div>
                      </div>

                      {/* Expanded Pocket Actions & Recent Mutations */}
                      {isExpanded && (
                        <div className="mt-3.5 pt-3 border-t border-white/20 space-y-3 animate-ios-spring-pop text-slate-800 dark:text-slate-100" onClick={(e) => e.stopPropagation()}>
                          {/* Quick Action Buttons */}
                          <div className="flex gap-2">
                            <button
                              type="button"
                              onClick={() => {
                                if (onOpenAddTx) onOpenAddTx(acc.id);
                              }}
                              className="flex-1 py-2 px-2 bg-white text-[#0284C7] text-[11px] font-bold rounded-xl flex items-center justify-center gap-1 shadow-xs hover:bg-sky-50 transition-colors ios-btn-tap"
                            >
                              <Icon name="plus" className="w-3.5 h-3.5" />
                              <span>Catat Mutasi</span>
                            </button>
                            <button
                              type="button"
                              onClick={(e) => handleStartEdit(acc, e)}
                              className="py-2 px-3 bg-white/20 hover:bg-white/30 text-white text-[11px] font-bold rounded-xl flex items-center gap-1 border border-white/30 transition-colors ios-btn-tap"
                            >
                              <Icon name="edit" className="w-3.5 h-3.5" />
                              <span>Edit</span>
                            </button>
                            {safeAccounts.length > 1 && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onDeleteAccount(acc.id);
                                }}
                                className="py-2 px-2.5 bg-rose-500/80 hover:bg-rose-600 text-white text-[11px] font-bold rounded-xl flex items-center gap-1 border border-rose-400/40 transition-colors ios-btn-tap"
                              >
                                <Icon name="trash" className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </div>

                          {/* Priority Reordering Controls (Quick Tap Alternative) */}
                          {safeAccounts.length > 1 && (
                            <div className="flex items-center justify-between py-1 px-1.5 bg-white/10 rounded-xl text-white">
                              <div className="text-[10px] font-bold text-sky-100 uppercase tracking-wider pl-1 flex items-center gap-1">
                                <Icon name="grip-vertical" className="w-3 h-3 text-sky-200" />
                                <span>Prioritas: {index === 0 ? 'Akun Utama' : `Urutan #${index + 1}`}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                {index > 0 && (
                                  <button
                                    type="button"
                                    onClick={() => handleMoveAccount(acc.id, 'top')}
                                    className="px-2 py-1 bg-amber-400 hover:bg-amber-300 text-slate-950 text-[10px] font-black rounded-lg shadow-xs transition-colors flex items-center gap-1 ios-btn-tap"
                                    title="Jadikan akun utama di posisi teratas"
                                  >
                                    <span>★ Jadikan Utama</span>
                                  </button>
                                )}
                                {index > 0 && (
                                  <button
                                    type="button"
                                    onClick={() => handleMoveAccount(acc.id, 'up')}
                                    className="p-1.5 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors ios-btn-tap"
                                    title="Naikkan urutan"
                                    aria-label="Naikkan urutan"
                                  >
                                    <Icon name="arrow-up" className="w-3 h-3" strokeWidth={2.5} />
                                  </button>
                                )}
                                {index < safeAccounts.length - 1 && (
                                  <button
                                    type="button"
                                    onClick={() => handleMoveAccount(acc.id, 'down')}
                                    className="p-1.5 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors ios-btn-tap"
                                    title="Turunkan urutan"
                                    aria-label="Turunkan urutan"
                                  >
                                    <Icon name="arrow-down" className="w-3 h-3" strokeWidth={2.5} />
                                  </button>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Recent Mutations for this account */}
                          <div className="space-y-1.5 pt-1">
                            <p className="text-[10px] font-bold text-sky-100 uppercase tracking-wider">
                              Mutasi Terakhir
                            </p>
                            {accountTxs.length === 0 ? (
                              <p className="text-[11px] text-sky-200/80 py-1 italic">Belum ada mutasi di kantong ini.</p>
                            ) : (
                              accountTxs.map(tx => (
                                <div key={tx.id} className="flex items-center justify-between py-1.5 px-2.5 rounded-xl bg-black/15 text-xs text-white">
                                  <span className="truncate max-w-[150px] font-medium text-sky-50">
                                    {tx.notes || tx.category || 'Mutasi'}
                                  </span>
                                  <span className="font-bold text-white">
                                    {tx.type === 'INCOME' ? '+' : '-'}{formatIDR(tx.amount)}
                                  </span>
                                </div>
                              ))
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    {showIndicatorAfter && (
                      <div className="ios-card-drop-indicator" />
                    )}
                  </React.Fragment>
                );
              })
            )}
          </div>
        </div>
      );
    };

    // =========================================================================
    // 8. FLOATING CAPSULE NAVIGATION (ICON-ONLY 5 TABS WITH TOUCH DRAG MECHANICS)
    // =========================================================================
    // =========================================================================
    // 8. FLOATING CAPSULE NAVIGATION (ICON-ONLY 5 TABS WITH FLUID iOS DRAG & DUAL MASK)
    // =========================================================================
    const FloatingCapsuleNav = ({ currentTab, onSelectTab }) => {
      const tabs = [
        { id: 'dashboard', label: 'Ringkasan', icon: 'home' },
        { id: 'cards', label: 'Kantong', icon: 'credit-card' },
        { id: 'debts', label: 'Hutang', icon: 'receipt' },
        { id: 'savings', label: 'Impian', icon: 'target' },
        { id: 'analytics', label: 'Statistik', icon: 'pie-chart' }
      ];

      const navRef = useRef(null);
      const isDraggingRef = useRef(false);
      const activeIndex = Math.max(0, tabs.findIndex(t => t.id === currentTab));

      // Continuous float position for real-time drag (0.0 to 4.0)
      const [dragPos, setDragPos] = useState(activeIndex);
      const [isDragging, setIsDragging] = useState(false);

      // Sync dragPos with activeIndex when not actively dragging
      useEffect(() => {
        if (!isDraggingRef.current) {
          setDragPos(activeIndex);
        }
      }, [activeIndex]);

      const updatePosFromCoord = (clientX) => {
        if (!navRef.current) return;
        const rect = navRef.current.getBoundingClientRect();
        const padding = 6;
        const availableW = rect.width - (padding * 2);
        const relX = clientX - (rect.left + padding);
        const fraction = Math.max(0, Math.min(0.9999, relX / availableW));
        const continuousPos = fraction * tabs.length;
        setDragPos(continuousPos);
      };

      const handlePointerDown = (clientX) => {
        isDraggingRef.current = true;
        setIsDragging(true);
        if (window.VoraletHaptics) window.VoraletHaptics.tap();
        else if (window.navigator?.vibrate) window.navigator.vibrate(10);
        updatePosFromCoord(clientX);
      };

      const handlePointerMove = (clientX) => {
        if (!isDraggingRef.current) return;
        updatePosFromCoord(clientX);
      };

      const handlePointerUp = () => {
        if (!isDraggingRef.current) return;
        isDraggingRef.current = false;
        setIsDragging(false);

        // Snap to nearest tab
        const finalIdx = Math.max(0, Math.min(tabs.length - 1, Math.round(dragPos - 0.5)));
        setDragPos(finalIdx);
        if (tabs[finalIdx] && tabs[finalIdx].id !== currentTab) {
          onSelectTab(tabs[finalIdx].id);
          if (window.VoraletHaptics) window.VoraletHaptics.tap();
          else if (window.navigator?.vibrate) window.navigator.vibrate(15);
        }
      };

      const currentPos = isDragging ? Math.max(0, Math.min(tabs.length - 1, dragPos - 0.5)) : activeIndex;
      const pillLeftPercent = (currentPos / tabs.length) * 100;
      const pillWidthPercent = 100 / tabs.length;

      return (
        <nav
          ref={navRef}
          onTouchStart={(e) => { if (e.touches?.[0]) handlePointerDown(e.touches[0].clientX); }}
          onTouchMove={(e) => { if (e.touches?.[0]) handlePointerMove(e.touches[0].clientX); }}
          onTouchEnd={handlePointerUp}
          onTouchCancel={handlePointerUp}
          onMouseDown={(e) => handlePointerDown(e.clientX)}
          onMouseMove={(e) => handlePointerMove(e.clientX)}
          onMouseUp={handlePointerUp}
          onMouseLeave={() => { if (isDraggingRef.current) handlePointerUp(); }}
          className="fixed bottom-5 left-0 right-0 z-50 w-[92%] max-w-[360px] h-14 mx-auto rounded-full bg-[#FFFFFF] dark:bg-[#1E293B] border border-slate-200 dark:border-[#334155] shadow-[0_12px_32px_rgba(15,23,42,0.18)] dark:shadow-[0_16px_36px_rgba(0,0,0,0.6)] select-none touch-none overflow-hidden p-1.5"
          style={{ willChange: 'transform' }}
        >
          {/* Inner relative container for precise pixel positioning */}
          <div className="relative w-full h-full">

            {/* BASE LAYER: Inactive Grey / Slate Icons */}
            <div className="absolute inset-0 flex items-center justify-around pointer-events-none">
              {tabs.map((t) => (
                <div
                  key={t.id}
                  className="flex-1 h-full flex items-center justify-center text-slate-400 dark:text-slate-500"
                >
                  <Icon
                    name={t.icon}
                    className="w-5 h-5 flex-shrink-0 aspect-square"
                    strokeWidth={1.8}
                  />
                </div>
              ))}
            </div>

            {/* SLIDING PILL BACKGROUND - Smooth spring when releasing, instantaneous when dragging */}
            <div
              className={`absolute top-0 bottom-0 rounded-full bg-[#0284C7] dark:bg-[#38BDF8] shadow-sm pointer-events-none ${
                isDragging ? 'transition-none' : 'transition-all duration-300'
              }`}
              style={{
                left: `${pillLeftPercent}%`,
                width: `${pillWidthPercent}%`,
                transitionTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)'
              }}
            />

            {/* TOP MASKED LAYER: Brilliant White Icons revealed EXACTLY where the pill is */}
            <div
              className={`absolute inset-0 pointer-events-none overflow-hidden ${
                isDragging ? 'transition-none' : 'transition-all duration-300'
              }`}
              style={{
                clipPath: `inset(0 ${Math.max(0, 100 - (pillLeftPercent + pillWidthPercent))}% 0 ${pillLeftPercent}% round 9999px)`,
                WebkitClipPath: `inset(0 ${Math.max(0, 100 - (pillLeftPercent + pillWidthPercent))}% 0 ${pillLeftPercent}% round 9999px)`,
                transitionTimingFunction: 'cubic-bezier(0.16, 1, 0.3, 1)'
              }}
            >
              <div className="w-full h-full flex items-center justify-around">
                {tabs.map((t) => (
                  <div
                    key={t.id}
                    className="flex-1 h-full flex items-center justify-center text-white dark:text-[#0F172A]"
                  >
                    <Icon
                      name={t.icon}
                      className="w-5 h-5 flex-shrink-0 aspect-square"
                      strokeWidth={2.4}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* CLICKABLE HIT TARGETS - 48x48dp touch accessibility */}
            <div className="absolute inset-0 flex items-center justify-around z-20">
              {tabs.map((t, idx) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => {
                    setDragPos(idx);
                    onSelectTab(t.id);
                  }}
                  title={t.label}
                  aria-label={t.label}
                  className="flex-1 h-full flex items-center justify-center rounded-full ios-btn-tap focus:outline-none cursor-pointer"
                />
              ))}
            </div>

          </div>
        </nav>
      );
    };

    // =========================================================================
    // 9. NON-INTRUSIVE SKIPPABLE ONBOARDING TUTORIAL MODAL
    // =========================================================================
    const NonIntrusiveTutorialModal = ({ isOpen, onDismiss }) => {
      const [step, setStep] = useState(0);

      const tutorialSteps = [
        {
          title: 'Selamat Datang di Voralet!',
          desc: 'Brankas keuangan pribadi yang 100% offline, terenkripsi, dan dirancang elegan dengan sensasi iOS.',
          icon: 'shield-check',
          badge: 'v2.6.0 Private Vault',
          color: 'from-sky-500 to-blue-600',
          detail: 'Semua mutasi, kantong, dan impian Anda tersimpan secara lokal dan aman di perangkat ini.'
        },
        {
          title: 'Kantong Terpisah & Multi-Akun',
          desc: 'Kelola dompet fisik, rekening bank, e-wallet, atau pos pengeluaran dalam tab Kantong Keuangan.',
          icon: 'credit-card',
          badge: 'Tab Kantong',
          color: 'from-blue-600 to-indigo-600',
          detail: 'Setiap kantong memiliki riwayat saldo mandiri sehingga arus kas Anda selalu tertib.'
        },
        {
          title: 'Navigasi Fluid & Geser Halus',
          desc: 'Sentuh atau tahan lalu geser kapsul navigasi di bagian bawah layar untuk beralih menu secepat kilat.',
          icon: 'navigation',
          badge: 'iOS Gestures',
          color: 'from-indigo-500 to-purple-600',
          detail: 'Efek visual masking interaktif akan mengikuti gerakan jari Anda secara real-time.'
        },
        {
          title: 'Cadangan Terenkripsi Ultra-Aman',
          desc: 'Unduh file cadangan brankas terenkripsi dengan perlindungan enkripsi berlapis dan kunci keamanan tingkat tinggi.',
          icon: 'lock',
          badge: 'Enkripsi Penuh',
          color: 'from-emerald-500 to-teal-600',
          detail: 'Data tidak dapat dibaca oleh pihak ketiga tanpa verifikasi aplikasi Voralet asli.'
        }
      ];

      if (!isOpen) return null;

      const current = tutorialSteps[step];
      const isLast = step === tutorialSteps.length - 1;

      const handleSkip = () => {
        if (window.VoraletHaptics) window.VoraletHaptics.tap();
        onDismiss();
      };

      const handleNext = () => {
        if (window.VoraletHaptics) window.VoraletHaptics.tap();
        if (isLast) {
          onDismiss();
        } else {
          setStep(s => s + 1);
        }
      };

      return (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-ios-backdrop">
          <div className="w-full max-w-sm bg-white dark:bg-slate-800 rounded-3xl shadow-[0_20px_50px_rgba(15,23,42,0.25)] border border-slate-200/80 dark:border-slate-700 p-5 space-y-4 animate-ios-sheet">
            
            {/* Header with Skip Pill Button */}
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full bg-sky-50 dark:bg-slate-700/80 text-[#0284C7] dark:text-[#38BDF8] border border-sky-100 dark:border-slate-600">
                {current.badge}
              </span>
              <button
                type="button"
                onClick={handleSkip}
                className="text-xs font-semibold text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 px-2 py-1 rounded-lg ios-btn-tap"
              >
                Lewati (Skip)
              </button>
            </div>

            {/* Icon Graphic */}
            <div className="flex items-center gap-3.5 pt-1">
              <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${current.color} text-white flex items-center justify-center shadow-md flex-shrink-0`}>
                <Icon name={current.icon} className="w-6 h-6" strokeWidth={2.2} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                  {current.title}
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                  Langkah {step + 1} dari {tutorialSteps.length}
                </p>
              </div>
            </div>

            {/* Description Text */}
            <div className="p-3 bg-slate-50 dark:bg-slate-900/70 rounded-2xl border border-slate-100 dark:border-slate-700/80 text-xs text-slate-600 dark:text-slate-300 space-y-1">
              <p className="font-medium leading-relaxed">{current.desc}</p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 leading-normal">{current.detail}</p>
            </div>

            {/* Progress Indicators & Action Buttons */}
            <div className="flex items-center justify-between pt-1">
              {/* Dots */}
              <div className="flex items-center gap-1.5">
                {tutorialSteps.map((_, idx) => (
                  <span
                    key={idx}
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      idx === step ? 'w-5 bg-[#0284C7] dark:bg-[#38BDF8]' : 'w-1.5 bg-slate-300 dark:bg-slate-600'
                    }`}
                  />
                ))}
              </div>

              {/* Next / Selesai Button */}
              <button
                type="button"
                onClick={handleNext}
                className="px-4 py-2 bg-[#0284C7] hover:bg-[#0369A1] dark:bg-[#38BDF8] dark:hover:bg-[#0284C7] text-white dark:text-[#0F172A] text-xs font-bold rounded-xl shadow-sm ios-btn-tap flex items-center gap-1.5"
              >
                <span>{isLast ? 'Mulai Pakai' : 'Lanjut'}</span>
                <Icon name="chevron-right" className="w-3.5 h-3.5" strokeWidth={2.5} />
              </button>
            </div>

          </div>
        </div>
      );
    };
"""
