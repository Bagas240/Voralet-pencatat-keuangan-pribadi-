package com.example.webview

import android.annotation.SuppressLint
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.webkit.WebSettings
import android.webkit.WebView

/**
 * Standardized, security-hardened and hardware-accelerated WebView configurator.
 * Follows modern Android development guidelines and OWASP Mobile recommendations.
 */
object VoraletWebViewConfig {

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
            overScrollMode = View.OVER_SCROLL_NEVER
            isVerticalScrollBarEnabled = false
            isHorizontalScrollBarEnabled = false

            // Allow default hardware layer rendering for smooth graphics pipeline
            setLayerType(View.LAYER_TYPE_NONE, null)

            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true

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
                cacheMode = WebSettings.LOAD_DEFAULT
                setSupportMultipleWindows(false)
                textZoom = 100 // Maintain precise layout geometry
            }
        }
    }
}
