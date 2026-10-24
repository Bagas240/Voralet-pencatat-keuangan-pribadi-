PART4_AUTH_PIN = """
    // =========================================================================
    // 3. AUTHENTICATION & PIN SECURITY (APPLE HIG LOCK & ONBOARDING)
    // =========================================================================

    // =========================================================================
    // PIXEL PET RENDERER (Retro 8-Bit Pixel Art Puppy & Kitty with 7 Animations)
    // Animations: idle, makan (eat), minum (drink), menggonggong (bark),
    // mengeong (meow), sedih (sad), happy (senang)
    // =========================================================================
    const PixelPetSprite = ({
      type = 'DOG',
      outfit = 'NONE',
      action = 'idle',
      isEating = false,
      isSad = false,
      size = 110,
      showBubble = true,
      onClick = null
    }) => {
      const isDog = type === 'DOG';

      // Compute effective animation state
      let effectiveAction = action;
      if (isEating) {
        effectiveAction = 'eat';
      } else if (action === 'idle' && isSad) {
        effectiveAction = 'sad';
      }
      if (effectiveAction === 'bark' && !isDog) effectiveAction = 'meow';
      if (effectiveAction === 'meow' && isDog) effectiveAction = 'bark';

      // Map action to CSS animation class
      let animClass = 'animate-pet-idle';
      if (effectiveAction === 'eat') animClass = 'animate-pet-eat';
      else if (effectiveAction === 'drink') animClass = 'animate-pet-drink';
      else if (effectiveAction === 'bark') animClass = 'animate-pet-bark';
      else if (effectiveAction === 'meow') animClass = 'animate-pet-meow';
      else if (effectiveAction === 'sad') animClass = 'animate-pet-sad';
      else if (effectiveAction === 'happy') animClass = 'animate-pet-happy';

      return (
        <div
          onClick={onClick}
          className={`relative inline-block ${animClass} pixelated select-none ${onClick ? 'cursor-pointer active:scale-95 transition-transform' : ''}`}
          style={{ width: size, height: size }}
        >
          {/* Action Speech Bubble / Floating Reaction */}
          {showBubble && effectiveAction === 'bark' && (
            <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-amber-500 text-white font-black text-[11px] px-2 py-0.5 rounded-full shadow-md animate-pet-bubble whitespace-nowrap z-20 pointer-events-none border border-white/60">
              Guk! Guk! 🦴 🐶
            </div>
          )}
          {showBubble && effectiveAction === 'meow' && (
            <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-rose-500 text-white font-black text-[11px] px-2 py-0.5 rounded-full shadow-md animate-pet-bubble whitespace-nowrap z-20 pointer-events-none border border-white/60">
              Meow~ 🐾 🎵 🐱
            </div>
          )}
          {showBubble && effectiveAction === 'eat' && (
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex items-center gap-0.5 text-xs animate-heart-float pointer-events-none z-20">
              <span>❤️</span>
              <span className="text-[10px] font-bold text-amber-500 dark:text-amber-400 bg-white/95 dark:bg-slate-800 px-1.5 py-0.5 rounded-md shadow-xs border border-amber-200/60 dark:border-amber-800/60 whitespace-nowrap">
                {isDog ? 'Nyam! 🍖' : 'Nyam! 🐟'}
              </span>
            </div>
          )}
          {showBubble && effectiveAction === 'drink' && (
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex items-center gap-0.5 text-xs animate-heart-float pointer-events-none z-20">
              <span>💧</span>
              <span className="text-[10px] font-bold text-sky-500 dark:text-sky-400 bg-white/95 dark:bg-slate-800 px-1.5 py-0.5 rounded-md shadow-xs border border-sky-200/60 dark:border-sky-800/60 whitespace-nowrap">
                Slurp! 💧 Segar!
              </span>
            </div>
          )}
          {showBubble && effectiveAction === 'happy' && (
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex items-center gap-0.5 text-xs animate-heart-float pointer-events-none z-20">
              <span>✨</span>
              <span>❤️</span>
              <span className="text-[10px] font-bold text-rose-500 bg-white/95 dark:bg-slate-800 px-1.5 py-0.5 rounded-md shadow-xs border border-rose-200 whitespace-nowrap">
                Sayang! 🥰
              </span>
            </div>
          )}
          {showBubble && effectiveAction === 'sad' && (
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs animate-pet-tear pointer-events-none z-20 flex items-center gap-1 bg-white/90 dark:bg-slate-800/90 px-1.5 py-0.5 rounded-full shadow-xs border border-sky-200 dark:border-slate-700 text-[10px] font-bold text-sky-500 whitespace-nowrap">
              <span>💧</span>
              <span>🥺 Sedih... Lapar</span>
            </div>
          )}

          <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            className="drop-shadow-md overflow-visible"
            style={{ shapeRendering: 'crispEdges' }}
          >
            {isDog ? (
              // ==================== PIXEL DOGGY (MILO) ====================
              <g>
                {/* Body & Belly */}
                <rect x="7" y="14" width="10" height="7" fill="#F59E0B" />
                <rect x="9" y="15" width="6" height="5" fill="#FEF3C7" />

                {/* Paws */}
                <rect x="7" y="20" width="2" height="3" fill="#D97706" />
                <rect x="15" y="20" width="2" height="3" fill="#D97706" />

                {/* Tail (Wagging fast when happy, gentle sway in idle, droopy when sad) */}
                {effectiveAction === 'sad' ? (
                  <g>
                    <rect x="17" y="17" width="2" height="3" fill="#B45309" />
                    <rect x="18" y="19" width="2" height="2" fill="#B45309" />
                  </g>
                ) : (
                  <g className={effectiveAction === 'happy' ? 'animate-pet-tail' : 'animate-pet-tail-idle'}>
                    <rect x="17" y="13" width="2" height="3" fill="#F59E0B" />
                    <rect x="18" y="11" width="2" height="2" fill="#F59E0B" />
                  </g>
                )}

                {/* Head */}
                <rect x="5" y="6" width="14" height="9" fill="#F59E0B" />

                {/* Ears: Drooped down when sad, perked up when normal/bark/happy */}
                {effectiveAction === 'sad' ? (
                  <g>
                    <rect x="3" y="7" width="3" height="5" fill="#B45309" />
                    <rect x="18" y="7" width="3" height="5" fill="#B45309" />
                  </g>
                ) : (
                  <g>
                    <rect x="4" y="3" width="3" height="4" fill="#B45309" />
                    <rect x="17" y="3" width="3" height="4" fill="#B45309" />
                  </g>
                )}

                {/* Snout */}
                <rect x="5" y="11" width="3" height="3" fill="#FEF3C7" />
                <rect x="16" y="11" width="3" height="3" fill="#FEF3C7" />
                <rect x="8" y="11" width="8" height="4" fill="#FEF3C7" />

                {/* Eyes according to state */}
                {effectiveAction === 'happy' ? (
                  // Smiling Curved Eyes ^^
                  <g>
                    <rect x="7" y="8" width="3" height="1" fill="#1F2937" />
                    <rect x="6" y="9" width="1" height="1" fill="#1F2937" />
                    <rect x="14" y="8" width="3" height="1" fill="#1F2937" />
                    <rect x="17" y="9" width="1" height="1" fill="#1F2937" />
                    {/* Pink Rosy Cheeks */}
                    <rect x="5" y="11" width="2" height="1" fill="#FDA4AF" />
                    <rect x="17" y="11" width="2" height="1" fill="#FDA4AF" />
                  </g>
                ) : effectiveAction === 'sad' ? (
                  // Tearful Sad Eyes
                  <g>
                    <rect x="7" y="8" width="2" height="2" fill="#1F2937" />
                    <rect x="15" y="8" width="2" height="2" fill="#1F2937" />
                    {/* Tears */}
                    <g className="animate-pet-tear">
                      <rect x="7" y="10" width="1" height="2" fill="#38BDF8" />
                      <rect x="15" y="10" width="1" height="2" fill="#38BDF8" />
                    </g>
                  </g>
                ) : (
                  // Alert Cute Eyes with natural Blinking
                  <g className="animate-pet-blink">
                    <rect x="7" y="8" width="2" height="2" fill="#1F2937" />
                    <rect x="7" y="8" width="1" height="1" fill="#FFFFFF" />
                    <rect x="15" y="8" width="2" height="2" fill="#1F2937" />
                    <rect x="15" y="8" width="1" height="1" fill="#FFFFFF" />
                  </g>
                )}

                {/* Nose */}
                <rect x="11" y="11" width="2" height="1" fill="#1F2937" />

                {/* Mouth according to state */}
                {effectiveAction === 'bark' ? (
                  // Wide Barking Mouth
                  <g>
                    <rect x="10" y="12" width="4" height="3" fill="#991B1B" />
                    <rect x="11" y="13" width="2" height="2" fill="#F43F5E" />
                    {/* Bark wave marks */}
                    <rect x="2" y="9" width="1" height="2" fill="#F59E0B" />
                    <rect x="1" y="8" width="1" height="4" fill="#F59E0B" />
                    <rect x="21" y="9" width="1" height="2" fill="#F59E0B" />
                    <rect x="22" y="8" width="1" height="4" fill="#F59E0B" />
                  </g>
                ) : effectiveAction === 'eat' ? (
                  // Munching Mouth with Crumb
                  <g>
                    <rect x="10" y="12" width="4" height="2" fill="#B91C1C" />
                    <rect x="11" y="12" width="2" height="2" fill="#FDE047" />
                    <rect x="6" y="13" width="1" height="1" fill="#D97706" />
                    <rect x="17" y="14" width="1" height="1" fill="#D97706" />
                  </g>
                ) : effectiveAction === 'drink' ? (
                  // Lapping Tongue
                  <g>
                    <rect x="11" y="12" width="2" height="3" fill="#F43F5E" />
                  </g>
                ) : effectiveAction === 'sad' ? (
                  // Sad Frown
                  <g>
                    <rect x="10" y="13" width="4" height="1" fill="#92400E" />
                    <rect x="10" y="14" width="1" height="1" fill="#92400E" />
                    <rect x="13" y="14" width="1" height="1" fill="#92400E" />
                  </g>
                ) : effectiveAction === 'happy' ? (
                  // Cheerful Smile with Tongue
                  <g>
                    <rect x="10" y="12" width="4" height="2" fill="#B91C1C" />
                    <rect x="11" y="13" width="2" height="2" fill="#F43F5E" />
                  </g>
                ) : (
                  // Calm Tongue Stick Out
                  <rect x="11" y="12" width="2" height="2" fill="#F43F5E" />
                )}
              </g>
            ) : (
              // ==================== PIXEL CAT (LUNA) ====================
              <g>
                {/* Body & Belly */}
                <rect x="7" y="14" width="10" height="7" fill="#64748B" />
                <rect x="9" y="15" width="6" height="5" fill="#F1F5F9" />

                {/* Paws */}
                <rect x="7" y="20" width="2" height="3" fill="#475569" />
                <rect x="15" y="20" width="2" height="3" fill="#475569" />

                {/* Tail (Swishing or Low) */}
                {effectiveAction === 'sad' ? (
                  <g>
                    <rect x="17" y="18" width="4" height="2" fill="#475569" />
                    <rect x="20" y="17" width="2" height="2" fill="#475569" />
                  </g>
                ) : (
                  <g className={effectiveAction === 'happy' ? 'animate-pet-tail' : 'animate-pet-tail-idle'}>
                    <rect x="17" y="12" width="2" height="6" fill="#64748B" />
                    <rect x="19" y="10" width="2" height="3" fill="#64748B" />
                  </g>
                )}

                {/* Head */}
                <rect x="5" y="7" width="14" height="8" fill="#64748B" />

                {/* Pointy Cat Ears: Flattened/drooped when sad */}
                {effectiveAction === 'sad' ? (
                  <g>
                    <rect x="4" y="6" width="3" height="3" fill="#475569" />
                    <rect x="5" y="7" width="1" height="1" fill="#FDA4AF" />
                    <rect x="17" y="6" width="3" height="3" fill="#475569" />
                    <rect x="18" y="7" width="1" height="1" fill="#FDA4AF" />
                  </g>
                ) : (
                  <g>
                    <rect x="5" y="3" width="3" height="4" fill="#475569" />
                    <rect x="6" y="4" width="1" height="2" fill="#FDA4AF" />
                    <rect x="16" y="3" width="3" height="4" fill="#475569" />
                    <rect x="17" y="4" width="1" height="2" fill="#FDA4AF" />
                  </g>
                )}

                {/* Muzzle */}
                <rect x="8" y="11" width="8" height="3" fill="#F1F5F9" />

                {/* Whiskers with twitching animation */}
                <g className={effectiveAction === 'meow' || effectiveAction === 'happy' ? 'animate-pet-whiskers' : ''}>
                  <rect x="4" y="11" width="3" height="1" fill="#94A3B8" />
                  <rect x="4" y="13" width="3" height="1" fill="#94A3B8" />
                  <rect x="17" y="11" width="3" height="1" fill="#94A3B8" />
                  <rect x="17" y="13" width="3" height="1" fill="#94A3B8" />
                </g>

                {/* Eyes according to state */}
                {effectiveAction === 'happy' ? (
                  // Smiling Curved Eyes ^^
                  <g>
                    <rect x="7" y="8" width="3" height="1" fill="#047857" />
                    <rect x="6" y="9" width="1" height="1" fill="#047857" />
                    <rect x="14" y="8" width="3" height="1" fill="#047857" />
                    <rect x="17" y="9" width="1" height="1" fill="#047857" />
                    {/* Pink Blush */}
                    <rect x="5" y="10" width="2" height="1" fill="#FDA4AF" />
                    <rect x="17" y="10" width="2" height="1" fill="#FDA4AF" />
                  </g>
                ) : effectiveAction === 'sad' ? (
                  // Sad Cat Eyes with Tear
                  <g>
                    <rect x="7" y="8" width="2" height="3" fill="#10B981" />
                    <rect x="15" y="8" width="2" height="3" fill="#10B981" />
                    <g className="animate-pet-tear">
                      <rect x="7" y="11" width="1" height="2" fill="#38BDF8" />
                      <rect x="15" y="11" width="1" height="2" fill="#38BDF8" />
                    </g>
                  </g>
                ) : (
                  // Classic Emerald Eyes with Pupils & natural blink
                  <g className="animate-pet-blink">
                    <rect x="7" y="8" width="2" height="3" fill="#10B981" />
                    <rect x="7" y="8" width="1" height="1" fill="#FFFFFF" />
                    <rect x="15" y="8" width="2" height="3" fill="#10B981" />
                    <rect x="15" y="8" width="1" height="1" fill="#FFFFFF" />
                  </g>
                )}

                {/* Pink Nose */}
                <rect x="11" y="11" width="2" height="1" fill="#FB7185" />

                {/* Mouth according to state */}
                {effectiveAction === 'meow' ? (
                  // Wide Open Meow Mouth
                  <g>
                    <rect x="10" y="12" width="4" height="2" fill="#E11D48" />
                    <rect x="11" y="13" width="2" height="1" fill="#FDA4AF" />
                  </g>
                ) : effectiveAction === 'eat' ? (
                  // Eating Fish Nibble
                  <g>
                    <rect x="10" y="12" width="4" height="2" fill="#BE123C" />
                    <rect x="11" y="12" width="2" height="1" fill="#38BDF8" />
                  </g>
                ) : effectiveAction === 'drink' ? (
                  // Lapping Tongue
                  <g>
                    <rect x="11" y="12" width="2" height="2" fill="#FB7185" />
                  </g>
                ) : effectiveAction === 'sad' ? (
                  // Downward Pout
                  <rect x="10" y="13" width="4" height="1" fill="#475569" />
                ) : effectiveAction === 'happy' ? (
                  // Sweet Smile
                  <g>
                    <rect x="10" y="12" width="4" height="1" fill="#E11D48" />
                    <rect x="11" y="13" width="2" height="1" fill="#FB7185" />
                  </g>
                ) : null}
              </g>
            )}

            {/* Food Bowl overlay during 'eat' */}
            {effectiveAction === 'eat' && (
              <g>
                {/* Bowl */}
                <rect x="8" y="21" width="8" height="2" fill={isDog ? '#EF4444' : '#F59E0B'} />
                <rect x="7" y="22" width="10" height="2" fill={isDog ? '#DC2626' : '#D97706'} />
                {/* Treat in bowl */}
                {isDog ? (
                  <rect x="10" y="20" width="4" height="1" fill="#FEF3C7" />
                ) : (
                  <rect x="10" y="20" width="4" height="1" fill="#38BDF8" />
                )}
                {/* Flying crumbs */}
                <g className="animate-pet-splash">
                  <rect x="6" y="18" width="1" height="1" fill={isDog ? '#F59E0B' : '#38BDF8'} />
                  <rect x="17" y="18" width="1" height="1" fill={isDog ? '#D97706' : '#0284C7'} />
                </g>
              </g>
            )}

            {/* Water Bowl overlay during 'drink' */}
            {effectiveAction === 'drink' && (
              <g>
                {/* Bowl */}
                <rect x="8" y="21" width="8" height="2" fill="#0284C7" />
                <rect x="7" y="22" width="10" height="2" fill="#0369A1" />
                {/* Water surface & droplets */}
                <rect x="9" y="21" width="6" height="1" fill="#BAE6FD" />
                <g className="animate-pet-splash">
                  <rect x="6" y="19" width="1" height="1" fill="#38BDF8" />
                  <rect x="17" y="19" width="1" height="1" fill="#38BDF8" />
                  <rect x="12" y="18" width="1" height="1" fill="#BAE6FD" />
                </g>
              </g>
            )}

            {/* OUTFITS */}
            {outfit === 'CROWN' && (
              <g>
                <rect x="7" y="1" width="10" height="4" fill="#F59E0B" />
                <rect x="7" y="0" width="2" height="2" fill="#FBBF24" />
                <rect x="11" y="0" width="2" height="2" fill="#FBBF24" />
                <rect x="15" y="0" width="2" height="2" fill="#FBBF24" />
                <rect x="9" y="2" width="2" height="2" fill="#EF4444" />
                <rect x="13" y="2" width="2" height="2" fill="#3B82F6" />
              </g>
            )}
            {outfit === 'HAT' && (
              <g>
                <rect x="8" y="0" width="8" height="5" fill="#1E1B4B" />
                <rect x="8" y="4" width="8" height="1" fill="#DC2626" />
                <rect x="6" y="5" width="12" height="1" fill="#1E1B4B" />
              </g>
            )}
            {outfit === 'GLASSES' && (
              <g>
                <rect x="6" y="8" width="4" height="3" fill="#1E293B" />
                <rect x="14" y="8" width="4" height="3" fill="#1E293B" />
                <rect x="10" y="8" width="4" height="1" fill="#1E293B" />
                <rect x="7" y="9" width="1" height="1" fill="#38BDF8" />
                <rect x="15" y="9" width="1" height="1" fill="#38BDF8" />
              </g>
            )}
            {outfit === 'BOWTIE' && (
              <g>
                <rect x="10" y="14" width="4" height="2" fill="#EF4444" />
                <rect x="9" y="13" width="2" height="4" fill="#DC2626" />
                <rect x="13" y="13" width="2" height="4" fill="#DC2626" />
                <rect x="11" y="14" width="2" height="2" fill="#FEF08A" />
              </g>
            )}
            {outfit === 'SCARF' && (
              <g>
                <rect x="7" y="13" width="10" height="2" fill="#0284C7" />
                <rect x="13" y="15" width="3" height="4" fill="#0284C7" />
                <rect x="8" y="13" width="2" height="2" fill="#F8FAFC" />
                <rect x="12" y="13" width="2" height="2" fill="#F8FAFC" />
              </g>
            )}
            {outfit === 'CAP' && (
              <g>
                <rect x="6" y="3" width="12" height="4" fill="#DC2626" />
                <rect x="14" y="5" width="6" height="2" fill="#B91C1C" />
                <rect x="10" y="3" width="4" height="2" fill="#FFFFFF" />
              </g>
            )}
          </svg>
        </div>
      );
    };
    const SplashScreen = ({ onFinish }) => {
      const [isFadingOut, setIsFadingOut] = useState(false);

      useEffect(() => {
        const timerHold = setTimeout(() => setIsFadingOut(true), 1300);
        const timerDone = setTimeout(() => onFinish(), 1700);
        return () => {
          clearTimeout(timerHold);
          clearTimeout(timerDone);
        };
      }, [onFinish]);

      return (
        <div className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#0099FF] transition-all duration-400 ease-out select-none ${
          isFadingOut ? 'opacity-0 scale-95 pointer-events-none' : 'opacity-100 scale-100'
        }`}>
          <div className="flex flex-col items-center text-center px-6 animate-ios-spring-pop">
            <VoraletLogo size="splash" />
          </div>
        </div>
      );
    };

    const PinDots = ({ count = 6, filled = 0, isError = false }) => {
      return (
        <div className={`flex justify-center items-center gap-4 my-6 select-none ${isError ? 'animate-ios-pin-shake' : ''}`}>
          {Array.from({ length: count }).map((_, idx) => {
            const isFilled = idx < filled;
            const isLatest = idx === filled - 1;
            return (
              <div
                key={idx}
                className={`relative w-4 h-4 rounded-full flex items-center justify-center transition-all duration-200 ${
                  isError
                    ? 'border-2 border-rose-500 bg-rose-500/10 scale-105'
                    : isFilled
                      ? 'border-2 border-[#0284C7] dark:border-[#38BDF8] bg-transparent'
                      : 'border-2 border-slate-300 dark:border-slate-700 bg-slate-100/90 dark:bg-slate-800'
                }`}
              >
                {isFilled && (
                  <div
                    className={`w-2.5 h-2.5 rounded-full transition-all duration-200 ${
                      isError
                        ? 'bg-rose-500'
                        : 'bg-[#0284C7] dark:bg-[#38BDF8]'
                    } ${isLatest && !isError ? 'animate-ios-pin-pop' : ''}`}
                  />
                )}
              </div>
            );
          })}
        </div>
      );
    };

    const Keypad = ({ onKeyPress, onBackspace }) => {
      const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', 'back'];

      return (
        <div className="grid grid-cols-3 gap-3.5 w-full max-w-xs mx-auto mt-2 select-none">
          {keys.map((k, i) => {
            if (k === '') return <div key={i} className="h-14" />;
            if (k === 'back') {
              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    onBackspace();
                  }}
                  className="h-14 rounded-2xl flex items-center justify-center text-slate-600 dark:text-[#94A3B8] hover:bg-slate-100 dark:hover:bg-[#1E293B] active:bg-slate-200 dark:active:bg-[#334155] transition-colors ios-keypad-btn"
                  aria-label="Hapus"
                >
                  <Icon name="backspace" className="w-6 h-6" strokeWidth={1.8} />
                </button>
              );
            }
            return (
              <button
                key={i}
                type="button"
                onClick={() => {
                  onKeyPress(k);
                }}
                className="h-14 rounded-2xl flex items-center justify-center text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] bg-white dark:bg-[#1E293B] border border-slate-200 dark:border-[#334155] hover:bg-slate-50 dark:hover:bg-[#273549] transition-colors shadow-sm ios-keypad-btn"
              >
                {k}
              </button>
            );
          })}
        </div>
      );
    };

    // Forgot PIN recovery is destructive because username-only verification cannot protect old data.
    const ForgotPinModal = ({ storedUsername, storedName, onClose, onResetPin }) => {
      const [step, setStep] = useState(1);
      const [inputUsername, setInputUsername] = useState('');
      const [verifyError, setVerifyError] = useState('');
      const [newPin, setNewPin] = useState('');
      const [confirmPin, setConfirmPin] = useState('');
      const [pinError, setPinError] = useState('');
      const [isClosing, setIsClosing] = useState(false);

      const handleClose = () => {
        setIsClosing(true);
        setTimeout(() => {
          setIsClosing(false);
          onClose();
        }, 380);
      };

      const handleVerifyUsername = (e) => {
        e.preventDefault();
        const trimmedInput = inputUsername.trim().toLowerCase().replace(/^@/, '');
        const targetUsername = (storedUsername || '').trim().toLowerCase();
        const targetName = (storedName || '').trim().toLowerCase();

        if (!trimmedInput) {
          setVerifyError('Harap masukkan username terdaftar');
          return;
        }

        const isMatch = targetUsername ? (trimmedInput === targetUsername) : (trimmedInput === targetName);
        if (isMatch) {
          setVerifyError('');
          setStep(2);
        } else {
          setVerifyError('Username tidak cocok dengan brankas akun Voralet.');
        }
      };

      const handleSaveNewPin = (e) => {
        e.preventDefault();
        if (newPin.length !== 6 || !/^\\d{6}$/.test(newPin)) {
          setPinError('PIN harus berupa 6 angka');
          return;
        }
        if (newPin !== confirmPin) {
          setPinError('Konfirmasi PIN tidak cocok');
          return;
        }
        CryptoService.hashPin(newPin).then(hashed => {
          onResetPin(hashed);
        });
      };

      return (
        <div className={`ios-modal-backdrop ${isClosing ? 'animate-ios-backdrop-exit' : 'animate-ios-backdrop'}`}
             onClick={(e) => { if (e.target === e.currentTarget) handleClose(); }}>
          <div className={`ios-modal-card bg-white dark:bg-[#121212] border border-slate-200 dark:border-[#27272A] p-5 ${isClosing ? 'animate-ios-sheet-exit' : 'animate-ios-sheet'}`}>
            <ModalDragHandle onDismiss={handleClose} />
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-[#27272A]">
              <div className="flex items-center gap-2">
                <IconBadge icon="lock" className="p-2 rounded-xl bg-sky-100 dark:bg-[#1C1C1E] text-brand dark:text-sky-400" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                  {step === 1 ? 'Verifikasi Lupa PIN' : 'Buat PIN Baru'}
                </h3>
              </div>
              <ModalCloseButton onClick={handleClose} />
            </div>

            {step === 1 ? (
              <form onSubmit={handleVerifyUsername} className="pt-4 space-y-4">
                <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed">
                  Masukkan <strong>Username (@id)</strong> akun Voralet kamu. Karena PIN lama tidak dapat dipulihkan, membuat PIN baru akan menghapus data lokal lama.
                </p>
                <div>
                  <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 block mb-1">
                    Username Akun (@id)
                  </label>
                  <div className="relative">
                    <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs font-mono font-bold">@</span>
                    <input
                      type="text"
                      value={inputUsername}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => {
                        setInputUsername(e.target.value);
                        setVerifyError('');
                      }}
                      placeholder="username_kamu"
                      className="w-full pl-8 pr-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-[#27272A] bg-slate-50 dark:bg-[#181818] text-slate-900 dark:text-white text-xs font-mono focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors"
                      autoFocus
                    />
                  </div>
                  {verifyError && (
                    <p className="text-[11px] text-rose-500 font-semibold mt-1">{verifyError}</p>
                  )}
                </div>
                <div className="flex gap-2 pt-2">
                  <button
                    type="button"
                    onClick={handleClose}
                    className="flex-1 py-2.5 bg-slate-100 dark:bg-[#1E1E1E] text-slate-700 dark:text-zinc-300 text-xs font-semibold rounded-xl ios-btn-tap"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-2.5 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover transition-colors ios-btn-tap"
                  >
                    Verifikasi
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleSaveNewPin} className="pt-4 space-y-4">
                <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed">
                  Identitas terverifikasi! Masukkan 6-digit PIN baru. Data lokal lama akan dihapus setelah PIN baru dibuat.
                </p>
                <div>
                  <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 block mb-1">
                    6-Digit PIN Baru
                  </label>
                  <input
                    type="password"
                    maxLength={6}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={newPin}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => {
                      const val = e.target.value.replace(/\\D/g, '').slice(0, 6);
                      setNewPin(val);
                      setPinError('');
                    }}
                    placeholder="••••••"
                    className="w-full px-3.5 py-2.5 rounded-xl border-2 border-slate-300 dark:border-zinc-700 bg-white dark:bg-[#181818] text-slate-900 dark:text-white text-center tracking-widest text-sm font-bold focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors"
                    autoFocus
                  />
                </div>
                <div>
                  <label className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 block mb-1">
                    Konfirmasi PIN Baru
                  </label>
                  <input
                    type="password"
                    maxLength={6}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={confirmPin}
                    onFocus={handleGlobalInputFocus}
                    onBlur={handleGlobalInputBlur}
                    onChange={(e) => {
                      const val = e.target.value.replace(/\\D/g, '').slice(0, 6);
                      setConfirmPin(val);
                      setPinError('');
                    }}
                    placeholder="••••••"
                    className="w-full px-3.5 py-2.5 rounded-xl border-2 border-slate-300 dark:border-zinc-700 bg-white dark:bg-[#181818] text-slate-900 dark:text-white text-center tracking-widest text-sm font-bold focus:outline-none focus:border-brand dark:focus:border-sky-400 transition-colors"
                  />
                  {pinError && (
                    <p className="text-[11px] text-rose-500 font-semibold mt-1">{pinError}</p>
                  )}
                </div>
                <div className="flex gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 py-2.5 bg-slate-100 dark:bg-[#1E1E1E] text-slate-700 dark:text-zinc-300 text-xs font-semibold rounded-xl ios-btn-tap"
                  >
                    Kembali
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-2.5 bg-brand text-white text-xs font-semibold rounded-xl hover:bg-brand-hover transition-colors ios-btn-tap"
                  >
                    Simpan PIN
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      );
    };

    const ReturningUserPinScreen = ({ storedPin, userName, username, avatar, theme, onToggleTheme, onUnlock, onResetPin }) => {
      const [pin, setPin] = useState('');
      const [error, setError] = useState(false);
      const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);

      const handlePress = (digit) => {
        if (pin.length < 6) {
          const next = pin + digit;
          setPin(next);
          setError(false);

          if (next.length === 6) {
            CryptoService.verifyPin(next, storedPin).then(isValid => {
              if (isValid) {
                setTimeout(() => onUnlock(), 120);
              } else {
                setError(true);
                setTimeout(() => setPin(''), 400);
              }
            });
          }
        }
      };

      const handleBackspace = () => {
        setPin(prev => prev.slice(0, -1));
        setError(false);
      };

      return (
        <div className="pin-keypad-screen flex flex-col justify-between p-6 bg-white dark:bg-[#0F172A] max-w-md mx-auto transition-colors duration-300 ease-in-out">
          <div>
            <div className="flex items-center justify-between pt-2">
              <AppLogo size="sm" showText={true} />
              <button
                type="button"
                onClick={onToggleTheme}
                className="w-9 h-9 rounded-full flex items-center justify-center text-[#64748B] dark:text-[#94A3B8] hover:bg-slate-100 dark:hover:bg-[#1E293B] transition-colors ios-btn-tap"
                aria-label="Mode Gelap / Terang"
              >
                <Icon name={theme === 'dark' ? 'sun' : 'moon'} className="w-5 h-5" />
              </button>
            </div>

            <div className="pt-8 text-center flex flex-col items-center">
              {avatar ? (
                <div className="mb-3">
                  <Avatar avatar={avatar} name={userName} size="w-16 h-16" textSize="text-xl" />
                </div>
              ) : (
                <div className="w-16 h-16 rounded-[22px] bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] flex items-center justify-center mb-3 text-[#0284C7] dark:text-[#38BDF8]">
                  <Icon name="lock" className="w-7 h-7" strokeWidth={1.8} />
                </div>
              )}
              <h1 className="text-xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">
                {userName ? `Hai, ${userName}` : 'Kunci Brankas'}
              </h1>
              <p className="text-xs text-[#64748B] dark:text-[#94A3B8] mt-1">Masukkan 6-digit PIN untuk akses brankas</p>

              <PinDots count={6} filled={pin.length} isError={error} />
              {error && (
                <p className="text-xs font-semibold text-rose-500">PIN salah. Silakan coba kembali.</p>
              )}
            </div>
          </div>

          <div className="pb-8">
            <Keypad onKeyPress={handlePress} onBackspace={handleBackspace} />
            <div className="mt-4 text-center">
              <button
                type="button"
                onClick={() => setIsForgotModalOpen(true)}
                className="text-xs font-medium text-[#64748B] hover:text-[#0284C7] dark:text-[#94A3B8] dark:hover:text-[#38BDF8] transition-colors py-1 px-3"
              >
                Lupa PIN?
              </button>
            </div>
          </div>

          {isForgotModalOpen && (
            <ForgotPinModal
              storedUsername={username}
              storedName={userName}
              onClose={() => setIsForgotModalOpen(false)}
              onResetPin={(newPin) => {
                onResetPin(newPin);
                setIsForgotModalOpen(false);
                setPin('');
              }}
            />
          )}
        </div>
      );
    };

    const OnboardingFlow = ({ onComplete }) => {
      const [onboardingStep, setOnboardingStep] = useState(1);
      const [newPin, setNewPin] = useState('');
      const [pinError, setPinError] = useState('');

      const [name, setName] = useState('');
      const [username, setUsername] = useState('');
      const [avatar, setAvatar] = useState('');
      const [identityError, setIdentityError] = useState('');

      // STEP 3: PET SELECTION & NAMING
      const [petType, setPetType] = useState('DOG'); // 'DOG' | 'CAT'
      const [petName, setPetName] = useState('Milo');
      const [petPreviewAction, setPetPreviewAction] = useState('idle');

      // STEP 4: WALLET CREATION
      const [walletName, setWalletName] = useState('BCA Utama');
      const [walletType, setWalletType] = useState('Bank'); // Tunai | Bank | E-Wallet
      const [initialBalance, setInitialBalance] = useState('');

      // STEP 1 PIN Handlers
      const handleDigitPress = (digit) => {
        if (newPin.length < 6) {
          const next = newPin + digit;
          setNewPin(next);
          setPinError('');
        }
      };

      const handleBackspace = () => {
        setNewPin(prev => prev.slice(0, -1));
        setPinError('');
      };

      const handleStep1Next = () => {
        if (newPin.length !== 6) {
          setPinError('PIN harus terdiri dari 6 digit angka');
          return;
        }
        setPinError('');
        setOnboardingStep(2);
      };

      // STEP 2 PROFILE HANDLER
      const handleStep2Next = (e) => {
        e?.preventDefault();
        const trimmedName = name.trim();
        if (!trimmedName) {
          setIdentityError('Harap masukkan nama panggilan');
          return;
        }
        let cleanUsername = username.trim().toLowerCase().replace(/^@/, '').replace(/[^a-z0-9_]/g, '');
        if (!cleanUsername) {
          cleanUsername = trimmedName.toLowerCase().replace(/[^a-z0-9_]/g, '') || 'voralet_user';
          setUsername(cleanUsername);
        }
        setIdentityError('');
        setOnboardingStep(3);
      };

      // STEP 3 PET SELECTION HANDLER
      const handleStep3Next = (e) => {
        e?.preventDefault();
        const trimmedPetName = petName.trim() || (petType === 'CAT' ? 'Luna' : 'Milo');
        setPetName(trimmedPetName);
        setOnboardingStep(4);
      };

      // STEP 4 FINISH ONBOARDING
      const handleFinishOnboarding = (e) => {
        e?.preventDefault();
        const trimmedName = name.trim() || 'Sahabat Voralet';
        const cleanUsername = (username.trim().toLowerCase().replace(/^@/, '').replace(/[^a-z0-9_]/g, '') || trimmedName.toLowerCase().replace(/[^a-z0-9_]/g, '') || 'voralet_user');
        const rawBalance = parseRawNumber(initialBalance);
        const trimmedWallet = walletName.trim() || 'BCA Utama';
        const finalPetName = petName.trim() || (petType === 'CAT' ? 'Luna' : 'Milo');

        const firstAccount = {
          id: 'acc_' + Date.now(),
          name: trimmedWallet,
          type: walletType,
          initialBalance: rawBalance,
          createdAt: new Date().toISOString()
        };

        const initialPet = {
          type: petType,
          name: finalPetName,
          fullness: 80,
          happiness: 85,
          outfit: 'NONE',
          unlockedOutfits: ['NONE'],
          foodCount: 5,
          drinkCount: 5,
          coins: 50,
          lastFedDate: new Date().toISOString().split('T')[0]
        };

        const initialStreak = {
          currentStreak: 1,
          lastActivityTimestamp: Date.now(),
          maxStreak: 1,
          level: 1,
          lastRecordedDate: new Date().toISOString().split('T')[0],
          isExpired: false
        };

        CryptoService.hashPin(newPin).then(hashedPin => {
          StorageService.setPin(hashedPin);
          StorageService.setName(trimmedName);
          StorageService.setUsername(cleanUsername);
          if (avatar) StorageService.setAvatar(avatar);
          StorageService.setAccounts([firstAccount]);
          StorageService.setTransactions([]);
          StorageService.setSavingsGoals([]);
          StorageService.setDebts([]);
          StorageService.setPetData(initialPet);
          StorageService.setStreakData(initialStreak);

          onComplete({
            pin: hashedPin,
            name: trimmedName,
            username: cleanUsername,
            avatar: avatar,
            accounts: [firstAccount],
            transactions: [],
            savingsGoals: [],
            debts: [],
            pet: initialPet,
            streak: initialStreak
          });
        });
      };

      return (
        <div className="min-h-[100dvh] w-full flex flex-col justify-between p-6 bg-white dark:bg-[#0F172A] max-w-md mx-auto transition-colors duration-300 ease-in-out text-[#0F172A] dark:text-[#F8FAFC]">
          {/* STEP 1: Buat 6-Digit PIN Security */}
          {onboardingStep === 1 && (
            <div className="pin-keypad-screen flex flex-col justify-between w-full">
              <div className="pt-6 text-center">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E0F2FE] dark:bg-[#1E293B] border border-[#BAE6FD] dark:border-[#334155] text-[#0284C7] dark:text-[#38BDF8] text-xs font-bold mb-4">
                  <span>Langkah 1 dari 4</span>
                </div>
                <div className="w-16 h-16 rounded-[22px] bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] flex items-center justify-center mx-auto mb-3 text-[#0284C7] dark:text-[#38BDF8]">
                  <Icon name="lock" className="w-7 h-7" strokeWidth={1.8} />
                </div>
                <h1 className="text-xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">
                  Buat 6-Digit PIN Security
                </h1>
                <p className="text-xs text-[#64748B] dark:text-[#94A3B8] mt-1">
                  PIN digunakan untuk mengamankan brankas lokal kamu
                </p>

                <PinDots
                  count={6}
                  filled={newPin.length}
                  isError={Boolean(pinError)}
                />

                {pinError && (
                  <p className="text-xs font-semibold text-rose-500 mt-2">{pinError}</p>
                )}
              </div>

              {/* Elevated Button Container */}
              <div className="pb-10 mb-8 pt-2 space-y-4">
                <Keypad
                  onKeyPress={handleDigitPress}
                  onBackspace={handleBackspace}
                />
                <button
                  type="button"
                  onClick={handleStep1Next}
                  disabled={newPin.length < 6}
                  className={`w-full py-4 rounded-2xl font-bold text-sm transition-all ios-btn-tap ${
                    newPin.length === 6
                      ? 'bg-[#0284C7] hover:bg-[#0369A1] text-white shadow-md cursor-pointer'
                      : 'bg-slate-100 dark:bg-[#1E293B] border border-transparent dark:border-[#334155] text-[#64748B] dark:text-[#94A3B8] opacity-60 cursor-not-allowed'
                  }`}
                >
                  Lanjutkan
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: Atur Profil Kamu */}
          {onboardingStep === 2 && (
            <div className="flex-1 flex flex-col justify-between w-full py-4 overflow-y-auto no-scrollbar">
              <div className="pt-4">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E0F2FE] dark:bg-[#1E293B] border border-[#BAE6FD] dark:border-[#334155] text-[#0284C7] dark:text-[#38BDF8] text-xs font-bold mb-3">
                    <span>Langkah 2 dari 4</span>
                  </div>
                  <h1 className="text-xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">Atur Profil Kamu</h1>
                  <p className="text-xs text-[#64748B] dark:text-[#94A3B8] mt-1">
                    Atur nama dan username untuk brankas keuanganmu
                  </p>
                </div>

                <div className="flex flex-col items-center mb-6">
                  <div className="relative">
                    <Avatar avatar={avatar} name={name} size="w-20 h-20" textSize="text-2xl" />
                    <label
                      htmlFor="onboarding-avatar-upload"
                      className="absolute bottom-0 right-0 w-7 h-7 bg-[#0284C7] text-white rounded-full flex items-center justify-center cursor-pointer shadow hover:bg-[#0369A1] transition-colors ios-btn-tap"
                      title="Unggah Foto Profil"
                    >
                      <Icon name="camera" className="w-4 h-4" />
                    </label>
                    <input
                      id="onboarding-avatar-upload"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) compressImage(file, (dataUrl) => setAvatar(dataUrl));
                      }}
                    />
                  </div>
                  <span className="text-[11px] text-[#64748B] dark:text-[#94A3B8] mt-2">Foto Profil (Opsional)</span>
                </div>

                <form id="step2-form" onSubmit={handleStep2Next} className="space-y-4 ios-inset-group bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] rounded-[22px] p-4">
                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-1.5">
                      Nama Panggilan <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={30}
                      value={name}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => {
                        const val = e.target.value;
                        setName(val);
                        setIdentityError('');
                        if (!username) {
                          setUsername(val.toLowerCase().replace(/[^a-z0-9_]/g, ''));
                        }
                      }}
                      placeholder="Misal: Bagas"
                      className="w-full px-3.5 py-3 bg-white dark:bg-[#0F172A] border border-slate-200 dark:border-[#334155] rounded-xl text-sm font-medium text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:border-[#0284C7] dark:focus:border-[#38BDF8] transition-colors"
                      autoFocus
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-1.5">
                      Username
                    </label>
                    <div className="relative">
                      <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#64748B] dark:text-[#94A3B8] font-mono text-sm font-bold">@</span>
                      <input
                        type="text"
                        required
                        maxLength={20}
                        value={username}
                        onFocus={handleGlobalInputFocus}
                        onBlur={handleGlobalInputBlur}
                        onChange={(e) => {
                          setUsername(e.target.value.toLowerCase().replace(/^@/, '').replace(/[^a-z0-9_]/g, ''));
                          setIdentityError('');
                        }}
                        placeholder="bagas"
                        className="w-full pl-8 pr-3.5 py-3 bg-white dark:bg-[#0F172A] border border-slate-200 dark:border-[#334155] rounded-xl text-sm font-mono text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:border-[#0284C7] dark:focus:border-[#38BDF8] transition-colors"
                      />
                    </div>
                    <span className="text-[11px] text-[#64748B] dark:text-[#94A3B8] mt-1 block">
                      Contoh: @bagas (digunakan untuk verifikasi pemulihan PIN)
                    </span>
                  </div>

                  {identityError && (
                    <p className="text-xs font-semibold text-rose-500">{identityError}</p>
                  )}
                </form>
              </div>

              <div className="flex gap-3 pt-6 pb-2">
                <button
                  type="button"
                  onClick={() => setOnboardingStep(1)}
                  className="py-3 px-4 bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] text-[#0F172A] dark:text-[#F8FAFC] text-sm font-semibold rounded-xl hover:bg-sky-50 dark:hover:bg-[#273549] transition-colors ios-btn-tap shrink-0"
                >
                  Kembali
                </button>
                <button
                  type="button"
                  onClick={handleStep2Next}
                  className="flex-1 py-3 bg-[#0284C7] hover:bg-[#0369A1] text-white text-sm font-bold rounded-xl shadow-sm transition-colors ios-btn-tap"
                >
                  Lanjut
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: Pilih Hewan Teman Keuangan (Dog vs Cat) */}
          {onboardingStep === 3 && (
            <div className="flex-1 flex flex-col justify-between w-full py-4 overflow-y-auto no-scrollbar">
              <div className="pt-2">
                <div className="text-center mb-4">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E0F2FE] dark:bg-[#1E293B] border border-[#BAE6FD] dark:border-[#334155] text-[#0284C7] dark:text-[#38BDF8] text-xs font-bold mb-2">
                    <span>Langkah 3 dari 4</span>
                  </div>
                  <h1 className="text-xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">Pilih Teman Keuanganmu</h1>
                  <p className="text-xs text-[#64748B] dark:text-[#94A3B8] mt-0.5">
                    Peliharaan yang akan menemanimu disiplin menabung & mencatat keuangan
                  </p>
                </div>

                {/* Live Pet Animated Preview Card */}
                <div className="bg-gradient-to-b from-amber-50/80 via-sky-50/50 to-indigo-50/60 dark:from-slate-800 dark:via-slate-800 dark:to-slate-800 border border-amber-200/60 dark:border-slate-700 rounded-2xl p-4 flex flex-col items-center justify-center text-center shadow-xs mb-4">
                  <div className="py-2 cursor-pointer hover:scale-105 active:scale-95 transition-transform" onClick={() => {
                    setPetPreviewAction('happy');
                    setTimeout(() => setPetPreviewAction('idle'), 2500);
                  }}>
                    <PixelPetSprite
                      type={petType}
                      outfit="NONE"
                      action={petPreviewAction}
                      size={108}
                    />
                  </div>
                  <p className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 mt-1">
                    Tampilan interaktif {petType === 'DOG' ? 'Dog (Anjing)' : 'Cat (Kucing)'} kamu
                  </p>
                </div>

                {/* Pet Selection (Buttons labeled strictly "Dog" and "Cat") */}
                <div className="space-y-3.5 ios-inset-group bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] rounded-[22px] p-4">
                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-2">
                      Pilih Jenis Hewan Peliharaan <span className="text-rose-500">*</span>
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={() => {
                          setPetType('DOG');
                          if (petName === 'Luna') setPetName('Milo');
                          setPetPreviewAction('bark');
                          setTimeout(() => setPetPreviewAction('idle'), 2000);
                        }}
                        className={`py-3 px-3 rounded-2xl border text-center flex flex-col items-center justify-center gap-1.5 transition-all ios-btn-tap ${
                          petType === 'DOG'
                            ? 'bg-[#E0F2FE] dark:bg-slate-700/80 border-[#0284C7] dark:border-[#38BDF8] text-[#0284C7] dark:text-[#38BDF8] font-bold shadow-sm'
                            : 'bg-white dark:bg-[#0F172A] border-slate-200 dark:border-[#334155] text-slate-600 dark:text-[#94A3B8] hover:bg-slate-50'
                        }`}
                      >
                        <span className="text-2xl">🐶</span>
                        <span className="text-xs font-bold">Dog</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          setPetType('CAT');
                          if (petName === 'Milo') setPetName('Luna');
                          setPetPreviewAction('meow');
                          setTimeout(() => setPetPreviewAction('idle'), 2000);
                        }}
                        className={`py-3 px-3 rounded-2xl border text-center flex flex-col items-center justify-center gap-1.5 transition-all ios-btn-tap ${
                          petType === 'CAT'
                            ? 'bg-[#E0F2FE] dark:bg-slate-700/80 border-[#0284C7] dark:border-[#38BDF8] text-[#0284C7] dark:text-[#38BDF8] font-bold shadow-sm'
                            : 'bg-white dark:bg-[#0F172A] border-slate-200 dark:border-[#334155] text-slate-600 dark:text-[#94A3B8] hover:bg-slate-50'
                        }`}
                      >
                        <span className="text-2xl">🐱</span>
                        <span className="text-xs font-bold">Cat</span>
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-1.5">
                      Nama Peliharaan <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={20}
                      value={petName}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => setPetName(e.target.value)}
                      placeholder={petType === 'DOG' ? 'Milo' : 'Luna'}
                      className="w-full px-3.5 py-3 bg-white dark:bg-[#0F172A] border border-slate-200 dark:border-[#334155] rounded-xl text-sm font-bold text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:border-[#0284C7] dark:focus:border-[#38BDF8] transition-colors"
                    />
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 block">
                      Nama peliharaan akan disimpan permanen untuk pet ini
                    </span>
                  </div>

                  {/* Starter Pack Badge */}
                  <div className="p-3 bg-amber-50/90 dark:bg-amber-950/40 border border-amber-200/80 dark:border-amber-700/60 rounded-xl text-left">
                    <span className="text-[11px] font-black uppercase text-amber-700 dark:text-amber-300 block mb-1">
                      🎁 Starter Pack Peliharaan Baru:
                    </span>
                    <div className="flex items-center gap-3 text-xs font-bold text-slate-800 dark:text-slate-200">
                      <span>{petType === 'CAT' ? '🐟' : '🍖'} 5 Makanan</span>
                      <span>•</span>
                      <span>💧 5 Minuman Segar</span>
                      <span>•</span>
                      <span>🪙 50 Koin</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-6 pb-2">
                <button
                  type="button"
                  onClick={() => setOnboardingStep(2)}
                  className="py-3 px-4 bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] text-[#0F172A] dark:text-[#F8FAFC] text-sm font-semibold rounded-xl hover:bg-sky-50 dark:hover:bg-[#273549] transition-colors ios-btn-tap shrink-0"
                >
                  Kembali
                </button>
                <button
                  type="button"
                  onClick={handleStep3Next}
                  className="flex-1 py-3 bg-[#0284C7] hover:bg-[#0369A1] text-white text-sm font-bold rounded-xl shadow-sm transition-colors ios-btn-tap"
                >
                  Lanjut ke Dompet
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: Setup Dompet Pertama */}
          {onboardingStep === 4 && (
            <div className="flex-1 flex flex-col justify-between w-full py-4 overflow-y-auto no-scrollbar">
              <div className="pt-4">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#E0F2FE] dark:bg-[#1E293B] border border-[#BAE6FD] dark:border-[#334155] text-[#0284C7] dark:text-[#38BDF8] text-xs font-bold mb-3">
                    <span>Langkah 4 dari 4</span>
                  </div>
                  <h1 className="text-xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">Buat Dompet Pertama</h1>
                  <p className="text-xs text-[#64748B] dark:text-[#94A3B8] mt-1">
                    Atur sumber dana awal untuk mencatat keuanganmu
                  </p>
                </div>

                <form id="step4-form" onSubmit={handleFinishOnboarding} className="space-y-4 ios-inset-group bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] rounded-[22px] p-4">
                  {/* Field 1: Nama Dompet */}
                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-1.5">
                      Nama Dompet <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={walletName}
                      onFocus={handleGlobalInputFocus}
                      onBlur={handleGlobalInputBlur}
                      onChange={(e) => setWalletName(e.target.value)}
                      placeholder="e.g. BCA Utama, Cash"
                      className="w-full px-3.5 py-3 bg-white dark:bg-[#0F172A] border border-slate-200 dark:border-[#334155] rounded-xl text-sm font-medium text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:border-[#0284C7] dark:focus:border-[#38BDF8] transition-colors"
                      autoFocus
                    />
                  </div>

                  {/* Field 2: Kategori */}
                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-1.5">
                      Kategori
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'Cash', label: 'Tunai', icon: 'cash' },
                        { id: 'Bank', label: 'Bank', icon: 'bank' },
                        { id: 'E-Wallet', label: 'E-Wallet', icon: 'smartphone' }
                      ].map(item => {
                        const isSelected = walletType === item.id;
                        return (
                          <button
                            key={item.id}
                            type="button"
                            onClick={() => setWalletType(item.id)}
                            className={`py-2.5 px-2 text-center rounded-xl border text-xs font-medium flex flex-col items-center gap-1.5 transition-all ios-btn-tap ${
                              isSelected
                                ? 'bg-[#E0F2FE] dark:bg-[#1E293B] border-[#0284C7] dark:border-[#38BDF8] text-[#0284C7] dark:text-[#38BDF8] font-bold shadow-sm'
                                : 'bg-white dark:bg-[#0F172A] border-slate-200 dark:border-[#334155] text-[#64748B] dark:text-[#94A3B8] hover:bg-slate-50 dark:hover:bg-[#1E293B]'
                            }`}
                          >
                            <Icon name={item.icon} className="w-5 h-5 flex-shrink-0 aspect-square" />
                            <span className="whitespace-nowrap">{item.label}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Field 3: Saldo Awal */}
                  <div>
                    <label className="block text-xs font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-1.5">
                      Saldo Awal
                    </label>
                    <div className="relative">
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
                        className="w-full px-3.5 py-3 bg-white dark:bg-[#0F172A] border border-slate-200 dark:border-[#334155] rounded-xl text-base font-bold text-[#0F172A] dark:text-[#F8FAFC] focus:outline-none focus:border-[#0284C7] dark:focus:border-[#38BDF8] transition-colors"
                      />
                    </div>
                    <span className="text-[11px] text-[#64748B] dark:text-[#94A3B8] mt-1 block">
                      Jumlah saldo yang kamu miliki saat ini
                    </span>
                  </div>
                </form>
              </div>

              {/* CTA Button: Mulai Gunakan Voralet */}
              <div className="flex gap-3 pt-6 pb-2">
                <button
                  type="button"
                  onClick={() => setOnboardingStep(3)}
                  className="py-3 px-4 bg-[#F0F9FF] dark:bg-[#1E293B] border border-[#E0F2FE] dark:border-[#334155] text-[#0F172A] dark:text-[#F8FAFC] text-sm font-semibold rounded-xl hover:bg-sky-50 dark:hover:bg-[#273549] transition-colors ios-btn-tap shrink-0"
                >
                  Kembali
                </button>
                <button
                  type="button"
                  onClick={handleFinishOnboarding}
                  className="flex-1 py-3.5 bg-[#0099FF] hover:bg-[#008CE8] text-white text-sm font-bold rounded-xl shadow-md transition-all active:scale-95 ios-btn-tap text-center"
                >
                  Mulai Gunakan Voralet
                </button>
              </div>
            </div>
          )}
        </div>
      );
    };
"""
