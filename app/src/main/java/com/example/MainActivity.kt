package com.example

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.ViewGroup
import android.view.WindowManager
import android.webkit.ValueCallback
import android.webkit.WebView
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.viewinterop.AndroidView
import com.example.bridge.AndroidNativeBridge
import com.example.ui.theme.MyApplicationTheme
import com.example.webview.VoraletWebChromeClient
import com.example.webview.VoraletWebViewClient
import com.example.webview.VoraletWebViewConfig
import java.io.File

/**
 * Main Activity for Voralet Personal Finance App v2.8.0.
 * Architected with Clean Principles, Edge-to-Edge display, and Hardware Accelerated Web Engine.
 * Optimized for high-refresh-rate displays (90Hz / 120Hz) and zero-jank 120 FPS animations.
 */
class MainActivity : ComponentActivity() {

    private var currentWebView: WebView? = null

    companion object {
        private const val TAG = "MainActivity"

        fun prepareWebViewStorage(context: Context) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    if (android.os.Process.isIsolated()) return
                    val processName = android.app.Application.getProcessName()
                    if (context.packageName != processName) {
                        WebView.setDataDirectorySuffix(processName)
                    }
                }
                // If a previous version prematurely created empty HTTP Cache directories without the index,
                // purge them so Chromium Simple Cache can initialize cleanly without reconstruction errors.
                val defaultDir = File(context.cacheDir, "WebView/Default")
                val httpCache = File(defaultDir, "HTTP Cache")
                if (httpCache.exists()) {
                    val indexFile = File(httpCache, "index-dir/the-real-index")
                    if (!indexFile.exists()) {
                        httpCache.deleteRecursively()
                    }
                }
            } catch (t: Throwable) {
                Log.w(TAG, "Storage directory preparation notice: ${t.message}")
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prepareWebViewStorage(this)
        // Enable WebView remote debugging only for debug builds
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
        enableEdgeToEdge()
        // Ensure status bar icons are dark/high-contrast by default on light background
        try {
            val insetsController = androidx.core.view.WindowCompat.getInsetsController(window, window.decorView)
            insetsController.isAppearanceLightStatusBars = true
            insetsController.isAppearanceLightNavigationBars = true
        } catch (t: Throwable) {
            Log.d(TAG, "Status bar appearance notice: ${t.message}")
        }

        // Lock / prioritize High Refresh Rate (90Hz / 120Hz) on physical devices (e.g. Infinix, Samsung, Xiaomi)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R && !VoraletWebViewConfig.isEmulator) {
            window.decorView.post {
                try {
                    val currentDisplay = display
                    val modes = currentDisplay?.supportedModes
                    val highestMode = modes?.maxByOrNull { it.refreshRate }
                    if (highestMode != null && highestMode.refreshRate > 60f) {
                        val lp = window.attributes
                        lp.preferredDisplayModeId = highestMode.modeId
                        window.attributes = lp
                    }
                } catch (t: Throwable) {
                    Log.d(TAG, "Display refresh rate optimization notice: ${t.message}")
                }
            }
        }

        setContent {
            MyApplicationTheme {
                val bgColor = MaterialTheme.colorScheme.background
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(bgColor)
                        .systemBarsPadding()
                ) {
                    VoraletWebViewContainer(
                        activity = this@MainActivity,
                        backgroundColor = bgColor.toArgb(),
                        onWebViewReady = { webView ->
                            currentWebView = webView
                        }
                    )
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        currentWebView?.onResume()
    }

    override fun onPause() {
        super.onPause()
        currentWebView?.onPause()
    }

    override fun onDestroy() {
        currentWebView?.let { wv ->
            (wv.parent as? ViewGroup)?.removeView(wv)
            wv.destroy()
        }
        currentWebView = null
        super.onDestroy()
    }
}

@Composable
fun VoraletWebViewContainer(
    activity: ComponentActivity,
    backgroundColor: Int,
    onWebViewReady: (WebView?) -> Unit,
    modifier: Modifier = Modifier
) {
    var reloadKey by remember { mutableIntStateOf(0) }
    var webViewInstance by remember { mutableStateOf<WebView?>(null) }
    var fileCallback by remember { mutableStateOf<ValueCallback<Array<Uri>>?>(null) }

    val fileChooserLauncher = androidx.activity.compose.rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uri = result.data?.data
        if (uri != null) {
            fileCallback?.onReceiveValue(arrayOf(uri))
        } else {
            val clipData = result.data?.clipData
            if (clipData != null && clipData.itemCount > 0) {
                val uris = Array(clipData.itemCount) { i -> clipData.getItemAt(i).uri }
                fileCallback?.onReceiveValue(uris)
            } else {
                fileCallback?.onReceiveValue(null)
            }
        }
        fileCallback = null
    }

    BackHandler(enabled = true) {
        if (webViewInstance?.canGoBack() == true) {
            webViewInstance?.goBack()
        } else {
            activity.finish()
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            onWebViewReady(null)
        }
    }

    key(reloadKey) {
        AndroidView(
            modifier = modifier.fillMaxSize(),
            factory = { context ->
                WebView(context).apply {
                    // Apply standardized hardware acceleration and security configurations
                    VoraletWebViewConfig.applySettings(this, backgroundColor)

                    // Inject secure native bridge
                    val bridge = AndroidNativeBridge(activity)
                    addJavascriptInterface(bridge, AndroidNativeBridge.BRIDGE_NAME)

                    webViewClient = VoraletWebViewClient(
                        onCrashRecover = {
                            (this.parent as? ViewGroup)?.removeView(this)
                            this.destroy()
                            webViewInstance = null
                            onWebViewReady(null)
                            reloadKey++
                        }
                    )

                    webChromeClient = VoraletWebChromeClient(
                        fileChooserLauncher = fileChooserLauncher,
                        onFileCallbackReady = { cb -> fileCallback = cb }
                    )

                    loadUrl("file:///android_asset/index.html")
                    webViewInstance = this
                    onWebViewReady(this)
                }
            },
            update = { webView ->
                webViewInstance = webView
                onWebViewReady(webView)
            }
        )
    }
}
