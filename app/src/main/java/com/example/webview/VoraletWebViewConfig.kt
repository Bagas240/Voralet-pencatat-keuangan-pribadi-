package com.example.webview

import android.annotation.SuppressLint
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.webkit.WebSettings
import android.webkit.WebView

/**
 * Standardized, security-hardened WebView configurator.
 * Follows modern Android development guidelines and OWASP Mobile recommendations.
 */
object VoraletWebViewConfig {

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

            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true

                // Security Hardening: Never allow local file URLs to access arbitrary files or external origins
                allowFileAccess = true
                allowContentAccess = true
                allowFileAccessFromFileURLs = false
                allowUniversalAccessFromFileURLs = false

                // Security: Block mixed HTTP/HTTPS content
                mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW

                // Security: Enable Google Safe Browsing on supported OS versions
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    safeBrowsingEnabled = true
                }

                // Smooth display and viewport metrics
                useWideViewPort = true
                loadWithOverviewMode = true
                setSupportMultipleWindows(false)
                textZoom = 100 // Maintain precise layout geometry
            }
        }
    }
}
