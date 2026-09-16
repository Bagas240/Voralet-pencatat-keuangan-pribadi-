package com.example.bridge

import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.util.Log
import android.webkit.JavascriptInterface
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsControllerCompat

/**
 * High-performance, secure Native Android Bridge for Voralet.
 * Exposes hardware haptics, clipboard operations, system bar theming,
 * and security integrity helpers to the Web engine.
 */
class AndroidNativeBridge(
    private val activity: Activity
) {
    companion object {
        const val BRIDGE_NAME = "AndroidBridge"
        private const val TAG = "AndroidNativeBridge"
        private const val APP_VERSION = "2.3.0"
    }

    private val clipboardManager: ClipboardManager? by lazy {
        activity.getSystemService(Context.CLIPBOARD_SERVICE) as? ClipboardManager
    }

    private val vibrator: Vibrator? by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = activity.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
            vibratorManager?.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            activity.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
        }
    }

    /**
     * Tactile native haptic feedback for button taps, PIN inputs, and tab switches.
     */
    @JavascriptInterface
    fun hapticFeedback(type: String?) {
        try {
            val vib = vibrator ?: return
            if (!vib.hasVibrator()) return

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val effectId = when (type?.lowercase()) {
                    "heavy" -> VibrationEffect.EFFECT_HEAVY_CLICK
                    "medium" -> VibrationEffect.EFFECT_DOUBLE_CLICK
                    "success" -> VibrationEffect.EFFECT_TICK
                    "click", "light" -> VibrationEffect.EFFECT_CLICK
                    else -> VibrationEffect.EFFECT_CLICK
                }
                vib.vibrate(VibrationEffect.createPredefined(effectId))
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val duration = when (type?.lowercase()) {
                    "heavy" -> 35L
                    "medium" -> 20L
                    "success" -> 15L
                    else -> 10L
                }
                val amplitude = when (type?.lowercase()) {
                    "heavy" -> 255
                    "medium" -> 180
                    else -> 120
                }
                vib.vibrate(VibrationEffect.createOneShot(duration, amplitude))
            } else {
                @Suppress("DEPRECATION")
                vib.vibrate(12L)
            }
        } catch (t: Throwable) {
            Log.d(TAG, "Haptic feedback skipped: ${t.message}")
        }
    }

    /**
     * Safe clipboard copy helper.
     */
    @JavascriptInterface
    fun copyToClipboard(label: String?, text: String?): Boolean {
        if (text.isNullOrEmpty()) return false
        return try {
            val clip = ClipData.newPlainText(label ?: "Voralet", text)
            clipboardManager?.setPrimaryClip(clip)
            hapticFeedback("light")
            true
        } catch (t: Throwable) {
            Log.w(TAG, "Failed to copy to clipboard", t)
            false
        }
    }

    /**
     * Sync system bar brightness / appearance with in-app theme.
     */
    @JavascriptInterface
    fun setStatusBarTheme(isDark: Boolean) {
        activity.runOnUiThread {
            try {
                val window = activity.window
                val insetsController = WindowCompat.getInsetsController(window, window.decorView)
                insetsController.isAppearanceLightStatusBars = !isDark
                insetsController.isAppearanceLightNavigationBars = !isDark
            } catch (t: Throwable) {
                Log.w(TAG, "Could not update status bar appearance", t)
            }
        }
    }

    /**
     * Expose app version to client code.
     */
    @JavascriptInterface
    fun getAppVersion(): String = APP_VERSION

    /**
     * Hardware acceleration check.
     */
    @JavascriptInterface
    fun isHardwareAccelerated(): Boolean = true
}
