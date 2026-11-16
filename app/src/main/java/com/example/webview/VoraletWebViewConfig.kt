package com.example.webview

import android.annotation.SuppressLint
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.webkit.WebSettings
import android.webkit.WebView

/**
 * Standardized, security-hardened WebView configurator.
 * 100% offline local engine using virtual origin https://appassets.androidplatform.net/
 * with strict file-access lockdown and anti-inspection hardening.
 */
object VoraletWebViewConfig {

    const val VIRTUAL_HOST = "appassets.androidplatform.net"
    const val ENTRY_URL = "https://$VIRTUAL_HOST/index.html"

    val isEmulator: Boolean by lazy {
        val fingerprint = Build.FINGERPRINT.lowercase()
        val model = Build.MODEL.lowercase()
        val hardware = Build.HARDWARE.lowercase()
        val product = Build.PRODUCT.lowercase()

        fingerprint.startsWith("generic")
            || fingerprint.startsWith("unknown")
            || model.contains("google_sdk")
            || model.contains("emulator")
            || hardware.contains("goldfish")
            || hardware.contains("ranchu")
            || product.contains("sdk")
            || product.contains("emulator")
    }

    @Suppress("DEPRECATION")
    @SuppressLint("SetJavaScriptEnabled")
    fun applySettings(
        webView: WebView,
        backgroundColor: Int
    ) {
        // Strictly disable remote DevTools / USB WebView inspection
        try {
            WebView.setWebContentsDebuggingEnabled(false)
        } catch (_: Throwable) {}

        webView.apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(backgroundColor)
            overScrollMode = View.OVER_SCROLL_IF_CONTENT_SCROLLS
            isVerticalScrollBarEnabled = false
            isHorizontalScrollBarEnabled = false
            isNestedScrollingEnabled = true
            isLongClickable = false
            isHapticFeedbackEnabled = false
            setOnLongClickListener { true }

            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true

                // Security Hardening: Disable file:// & content:// access completely;
                // all local assets are served via shouldInterceptRequest over virtual HTTPS origin.
                allowFileAccess = false
                allowContentAccess = false
                allowFileAccessFromFileURLs = false
                allowUniversalAccessFromFileURLs = false
                // Offline isolation is enforced by VoraletWebViewClient + zero INTERNET permission
                blockNetworkLoads = false

                // Security: Block mixed HTTP/HTTPS content
                mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    safeBrowsingEnabled = true
                }

                cacheMode = WebSettings.LOAD_NO_CACHE
                useWideViewPort = true
                loadWithOverviewMode = true
                setSupportMultipleWindows(false)
                setGeolocationEnabled(false)
                textZoom = 100
            }
        }
    }
}
