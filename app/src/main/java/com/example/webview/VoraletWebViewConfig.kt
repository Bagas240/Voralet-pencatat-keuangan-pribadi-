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

    val isEmulator: Boolean by lazy {
        (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || Build.HARDWARE.contains("goldfish")
                || Build.HARDWARE.contains("ranchu")
                || Build.PRODUCT.contains("sdk_gphone")
                || Build.PRODUCT.contains("sdk_google")
                || Build.PRODUCT.contains("google_sdk")
                || Build.PRODUCT.contains("sdk")
                || Build.PRODUCT.contains("sdk_x86")
                || Build.PRODUCT.contains("vbox86p")
                || Build.PRODUCT.contains("emulator")
                || Build.PRODUCT.contains("simulator"))
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
            overScrollMode = View.OVER_SCROLL_NEVER
            isVerticalScrollBarEnabled = false
            isHorizontalScrollBarEnabled = false
            isNestedScrollingEnabled = false

            // On virtual emulator environments (headless Mesa Gallium/Virgl without DRM rendernodes),
            // use LAYER_TYPE_SOFTWARE to prevent Mesa from failing to open /dev/dri/renderD*
            // On real physical hardware devices, use LAYER_TYPE_NONE for full native GPU acceleration
            if (isEmulator) {
                setLayerType(View.LAYER_TYPE_SOFTWARE, null)
            } else {
                setLayerType(View.LAYER_TYPE_NONE, null)
            }

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
                cacheMode = WebSettings.LOAD_DEFAULT
                setSupportMultipleWindows(false)
                textZoom = 100 // Maintain precise layout geometry

                // Pre-rasterize offscreen layers only on real devices to avoid extra EGL contexts on emulator
                if (!isEmulator) {
                    setOffscreenPreRaster(true)
                }
            }
        }
    }
}
