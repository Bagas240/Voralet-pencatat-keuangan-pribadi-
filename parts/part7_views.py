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
              className="px-4 py-2.5 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-2xl flex items-center gap-2 shadow-sm transition-all ios-btn-tap"
            >
              <Icon name="plus" className="w-4 h-4" strokeWidth={2.4} />
              <span>Target Baru</span>
            </button>
          </div>

          {safeGoals.length === 0 ? (
            <div className="ios-inset-group text-center py-10">
              <IconBadge icon="target" className="w-14 h-14 rounded-2xl bg-sky-50 dark:bg-slate-800 text-brand mx-auto mb-3" iconClass="w-7 h-7" />
              <h3 className="text-sm font-bold text-slate-800 dark:text-white">Belum Ada Target Impian</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xs mx-auto mb-4">
                Beli gadget baru, liburan, motor, atau dana darurat? Buat target impian pertamamu sekarang.
              </p>
              <button
                type="button"
                onClick={onOpenNewGoal}
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand hover:bg-brand-hover text-white text-xs font-bold rounded-xl shadow-sm transition-colors ios-btn-tap mx-auto"
              >
                <Icon name="plus" className="w-4 h-4" />
                <span>Buat Target Impian Baru</span>
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
                      className="flex-1 py-2.5 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover ios-btn-tap"
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
    // ANALYTICS VIEW WITH RESPONSIVE INLINE SVG LINE GRAPH & TREND CHARTS
    // =========================================================================
    const AnalyticsView = ({ transactions, accounts, hideBalance }) => {
      const [trendMode, setTrendMode] = useState('MONTHLY'); // MONTHLY (last 6 months) | YEARLY
      const safeTxs = Array.isArray(transactions) ? transactions : [];

      // Compute Trend Data for last 6 months or 5 years
      const trendData = useMemo(() => {
        const now = new Date();
        const periods = [];

        if (trendMode === 'MONTHLY') {
          // Last 6 months
          for (let i = 5; i >= 0; i--) {
            const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
            const prefix = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            const label = d.toLocaleDateString('id-ID', { month: 'short' });
            periods.push({ key: prefix, label, income: 0, expense: 0 });
          }
        } else {
          // Last 4 years
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

      // SVG dimensions
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

      // Category breakdown for current selected period
      const categoryBreakdown = useMemo(() => {
        const map = {};
        let sumExpense = 0;

        safeTxs.forEach(t => {
          if (!t || t.type !== 'EXPENSE') return;
          const amt = Number(t.amount) || 0;
          sumExpense += amt;
          map[t.category] = (map[t.category] || 0) + amt;
        });

        const list = Object.entries(map).map(([catId, amount]) => {
          const catInfo = CATEGORIES.find(c => c.id === catId) || { label: catId, icon: 'tag' };
          const pct = sumExpense > 0 ? Math.round((amount / sumExpense) * 100) : 0;
          return {
            id: catId,
            label: catInfo.label,
            icon: catInfo.icon,
            amount,
            percentage: pct
          };
        });

        return list.sort((a, b) => b.amount - a.amount);
      }, [safeTxs]);

      const totals = useMemo(() => Ledger.getSummaryTotals(safeTxs), [safeTxs]);

      return (
        <div className="space-y-4 pb-28 animate-ios-tab-view">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Analisis & Tren Keuangan</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Pantau arus kas dan pertumbuhan saldo</p>
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
                Grafik Arus Kas (Pemasukan vs Pengeluaran)
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

            {/* Inline SVG Chart */}
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
                      {/* Label */}
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
              <span className="text-[10px] font-bold uppercase tracking-wider text-brand block mb-1">Arus Bersih</span>
              <div className={`text-xs font-bold ${totals.net >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                {hideBalance ? 'Rp ••••••' : formatIDR(totals.net)}
              </div>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="ios-inset-group">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
              Rincian Kategori Pengeluaran
            </h3>

            {categoryBreakdown.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-6">Belum ada data pengeluaran.</p>
            ) : (
              <div className="space-y-3">
                {categoryBreakdown.map(item => (
                  <div key={item.id} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-lg bg-sky-50 dark:bg-slate-700 text-brand dark:text-sky-400 flex items-center justify-center">
                          <Icon name={item.icon} className="w-3.5 h-3.5" />
                        </div>
                        <span className="font-semibold text-slate-800 dark:text-slate-200">{item.label}</span>
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-slate-900 dark:text-white">
                          {hideBalance ? 'Rp ••••••' : formatIDR(item.amount)}
                        </span>
                        <span className="text-slate-400 text-[10px] ml-1.5">({item.percentage}%)</span>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-brand rounded-full transition-all duration-300"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      );
    };

    // =========================================================================
    // 8. FLOATING CAPSULE NAVIGATION (APPLE-STYLE FIXED CAPSULE NAV BAR)
    // =========================================================================
    const FloatingCapsuleNav = ({ currentTab, onSelectTab }) => {
      const tabs = [
        { id: 'dashboard', label: 'Ringkasan', icon: 'wallet' },
        { id: 'debts', label: 'Hutang', icon: 'receipt' },
        { id: 'savings', label: 'Impian', icon: 'target' },
        { id: 'analytics', label: 'Statistik', icon: 'pie-chart' }
      ];

      const activeIndex = Math.max(0, tabs.findIndex(t => t.id === currentTab));

      return (
        <nav
          className="fixed bottom-5 left-0 right-0 z-50 w-[92%] max-w-[360px] h-14 mx-auto rounded-full bg-white/95 backdrop-blur-md dark:bg-[#1E293B]/95 border border-slate-200/90 dark:border-[#334155] shadow-[0_8px_30px_rgba(15,23,42,0.12)] flex items-center p-1.5 select-none"
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
