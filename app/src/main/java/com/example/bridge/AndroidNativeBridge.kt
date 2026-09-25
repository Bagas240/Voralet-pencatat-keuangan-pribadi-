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
import android.webkit.WebView
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
        private const val APP_VERSION = "2.8.0"
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
     * Tactile native haptic feedback - Disabled per user request for silent interaction.
     */
    @JavascriptInterface
    fun hapticFeedback(type: String?) {
        // Disabled per user preference
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

    /**
     * Check if camera permission is granted.
     */
    @JavascriptInterface
    fun hasCameraPermission(): Boolean {
        return androidx.core.content.ContextCompat.checkSelfPermission(
            activity,
            android.Manifest.permission.CAMERA
        ) == android.content.pm.PackageManager.PERMISSION_GRANTED
    }

    /**
     * Request camera permission from the system.
     */
    @JavascriptInterface
    fun requestCameraPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            activity.runOnUiThread {
                activity.requestPermissions(
                    arrayOf(android.Manifest.permission.CAMERA),
                    1001
                )
            }
        }
    }

    /**
     * Print or export HTML report to PDF via Android PrintManager.
     */
    @JavascriptInterface
    fun printHtml(htmlContent: String?, jobTitle: String?) {
        if (htmlContent.isNullOrBlank()) return
        val title = jobTitle ?: "Laporan Keuangan Voralet"
        activity.runOnUiThread {
            try {
                val tempWebView = WebView(activity)
                tempWebView.webViewClient = object : android.webkit.WebViewClient() {
                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        try {
                            val printManager = activity.getSystemService(Context.PRINT_SERVICE) as? android.print.PrintManager
                            if (printManager != null && view != null) {
                                val printAdapter = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                                    view.createPrintDocumentAdapter(title)
                                } else {
                                    @Suppress("DEPRECATION")
                                    view.createPrintDocumentAdapter()
                                }
                                val printAttributes = android.print.PrintAttributes.Builder()
                                    .setMediaSize(android.print.PrintAttributes.MediaSize.ISO_A4)
                                    .setMinMargins(android.print.PrintAttributes.Margins.NO_MARGINS)
                                    .build()
                                printManager.print(title, printAdapter, printAttributes)
                            }
                        } catch (t: Throwable) {
                            Log.e(TAG, "Print error in onPageFinished", t)
                        }
                    }
                }
                tempWebView.loadDataWithBaseURL(null, htmlContent, "text/html", "UTF-8", null)
            } catch (t: Throwable) {
                Log.e(TAG, "Failed to initialize print webview", t)
            }
        }
    }
}
