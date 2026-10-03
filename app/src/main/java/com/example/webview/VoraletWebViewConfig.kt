package com.example.webview

import android.annotation.SuppressLint
import android.os.Build
import android.view.View
import android.view.ViewGroup
import android.webkit.WebSettings
import android.webkit.WebView
import java.io.File

/**
 * Standardized, security-hardened and hardware-accelerated WebView configurator.
 * Follows modern Android development guidelines and OWASP Mobile recommendations.
 */
object VoraletWebViewConfig {

    val isEmulator: Boolean by lazy {
        val fingerprint = Build.FINGERPRINT.lowercase()
        val model = Build.MODEL.lowercase()
        val manufacturer = Build.MANUFACTURER.lowercase()
        val hardware = Build.HARDWARE.lowercase()
        val product = Build.PRODUCT.lowercase()
        val board = Build.BOARD.lowercase()
        val device = Build.DEVICE.lowercase()
        val brand = Build.BRAND.lowercase()

        fingerprint.startsWith("generic")
                || fingerprint.startsWith("unknown")
                || fingerprint.contains("test-keys")
                || model.contains("google_sdk")
                || model.contains("emulator")
                || model.contains("android sdk")
                || model.contains("cuttlefish")
                || manufacturer.contains("genymotion")
                || (manufacturer.contains("google") && (product.contains("cf") || product.contains("sdk") || product.contains("gphone")))
                || hardware.contains("goldfish")
                || hardware.contains("ranchu")
                || hardware.contains("cutf")
                || hardware.contains("vsoc")
                || hardware.contains("cheeps")
                || hardware.contains("qemu")
                || product.contains("sdk")
                || product.contains("vbox")
                || product.contains("emulator")
                || product.contains("simulator")
                || product.contains("cf_")
                || product.contains("cuttlefish")
                || product.contains("gphone")
                || board.contains("cutf")
                || board.contains("vsoc")
                || device.contains("cutf")
                || device.contains("vsoc")
                || device.contains("generic")
                || brand.startsWith("generic")
                || !File("/dev/dri/renderD128").exists()
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

            // In emulators or cloud streaming environments lacking hardware rendernodes,
            // using software layer prevents Mesa "Failed to open rendernode" driver crashes and GPU stalls.
            if (isEmulator || !File("/dev/dri/renderD128").exists()) {
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
                cacheMode = WebSettings.LOAD_NO_CACHE
                setSupportMultipleWindows(false)
                textZoom = 100 // Maintain precise layout geometry
                setOffscreenPreRaster(!isEmulator && File("/dev/dri/renderD128").exists())
            }
        }
    }
}
