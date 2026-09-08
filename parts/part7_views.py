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
        <div className="space-y-4 pb-28">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Kantong Impian</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Wujudkan target tabungan kamu</p>
            </div>
            <button
              type="button"
              onClick={onOpenNewGoal}
              className="px-3.5 py-1.5 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover flex items-center gap-1.5 shadow-sm ios-btn-tap"
            >
              <Icon name="plus" className="w-4 h-4" />
              <span>Target Baru</span>
            </button>
          </div>

          {safeGoals.length === 0 ? (
            <div className="ios-inset-group text-center py-10">
              <IconBadge icon="target" className="w-12 h-12 rounded-2xl bg-sky-50 dark:bg-slate-800 text-brand mx-auto mb-2" iconClass="w-6 h-6" />
              <h3 className="text-sm font-bold text-slate-800 dark:text-white">Belum Ada Target Impian</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-xs mx-auto">
                Beli gadget baru, liburan, atau dana darurat? Buat target impian pertamamu sekarang.
              </p>
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
        <div className="space-y-4 pb-28">
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

      const navRef = useRef(null);
      const isDraggingRef = useRef(false);
      const [isDragging, setIsDragging] = useState(false);
      const tabRefs = useRef({});
      const [pillBounds, setPillBounds] = useState({ left: 8, width: 80 });

      const updatePillPosition = useCallback(() => {
        const activeEl = tabRefs.current[currentTab];
        if (activeEl && navRef.current) {
          const navRect = navRef.current.getBoundingClientRect();
          const tabRect = activeEl.getBoundingClientRect();
          setPillBounds({
            left: tabRect.left - navRect.left,
            width: tabRect.width
          });
        }
      }, [currentTab]);

      useEffect(() => {
        updatePillPosition();
        const timer = setTimeout(updatePillPosition, 50);
        window.addEventListener('resize', updatePillPosition);
        return () => {
          clearTimeout(timer);
          window.removeEventListener('resize', updatePillPosition);
        };
      }, [updatePillPosition]);

      const handlePointerMove = (clientX) => {
        if (!navRef.current) return;
        const rect = navRef.current.getBoundingClientRect();
        if (rect.width <= 0) return;
        const relativeX = clientX - rect.left;
        const fraction = Math.max(0, Math.min(0.999, relativeX / rect.width));
        const index = Math.floor(fraction * tabs.length);
        const targetTab = tabs[index];
        if (targetTab && targetTab.id !== currentTab) {
          onSelectTab(targetTab.id);
        }
      };

      const handleTouchStart = (e) => {
        isDraggingRef.current = true;
        setIsDragging(true);
        if (e.touches && e.touches[0]) {
          handlePointerMove(e.touches[0].clientX);
        }
      };

      const handleTouchMove = (e) => {
        if (!isDraggingRef.current) return;
        if (e.cancelable) {
          e.preventDefault();
        }
        if (e.touches && e.touches[0]) {
          handlePointerMove(e.touches[0].clientX);
        }
      };

      const handleTouchEnd = () => {
        isDraggingRef.current = false;
        setIsDragging(false);
      };

      const handleMouseDown = (e) => {
        isDraggingRef.current = true;
        setIsDragging(true);
        handlePointerMove(e.clientX);
      };

      const handleMouseMove = (e) => {
        if (!isDraggingRef.current) return;
        handlePointerMove(e.clientX);
      };

      const handleMouseUp = () => {
        isDraggingRef.current = false;
        setIsDragging(false);
      };

      useEffect(() => {
        const onGlobalMouseUp = () => {
          if (isDraggingRef.current) {
            isDraggingRef.current = false;
            setIsDragging(false);
          }
        };
        window.addEventListener('mouseup', onGlobalMouseUp);
        return () => window.removeEventListener('mouseup', onGlobalMouseUp);
      }, []);

      return (
        <nav
          ref={navRef}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          onTouchCancel={handleTouchEnd}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className={`relative w-[88%] max-w-[360px] h-14 rounded-full mx-auto fixed bottom-5 left-0 right-0 z-50 bg-white dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] shadow-md flex items-center justify-around px-2 select-none cursor-grab active:cursor-grabbing transition-transform duration-200 ${
            isDragging ? 'scale-[0.98]' : ''
          }`}
          style={{ touchAction: 'none' }}
        >
          {/* Liquid Physics Gliding Active Pill */}
          <div
            className="absolute top-2 bottom-2 rounded-full bg-[#E0F2FE] dark:bg-[#334155] pointer-events-none transition-all duration-300"
            style={{
              left: `${pillBounds.left}px`,
              width: `${pillBounds.width}px`,
              transitionTimingFunction: 'cubic-bezier(0.32, 0.72, 0, 1)'
            }}
          />

          {tabs.map((t) => {
            const isActive = currentTab === t.id;
            return (
              <button
                key={t.id}
                ref={(el) => { tabRefs.current[t.id] = el; }}
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectTab(t.id);
                }}
                className={`relative z-10 transition-colors duration-200 ios-btn-tap ${
                  isActive
                    ? 'text-[#0284C7] dark:text-[#38BDF8] rounded-full px-3 py-1.5 font-bold text-xs flex items-center gap-1.5'
                    : 'text-[#64748B] dark:text-[#94A3B8] hover:text-[#0F172A] dark:hover:text-[#F8FAFC] p-2 rounded-full flex items-center gap-1'
                }`}
              >
                <Icon name={t.icon} className="w-5 h-5 flex-shrink-0 aspect-square" strokeWidth={2} />
                {isActive && <span className="whitespace-nowrap font-bold text-xs">{t.label}</span>}
              </button>
            );
          })}
        </nav>
      );
    };
"""
