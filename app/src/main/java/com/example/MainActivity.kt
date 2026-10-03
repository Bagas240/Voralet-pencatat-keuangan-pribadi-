package com.example

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.webkit.ValueCallback
import android.webkit.WebView
import android.widget.FrameLayout
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.compose.BackHandler
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import com.example.bridge.AndroidNativeBridge
import com.example.webview.VoraletWebChromeClient
import com.example.webview.VoraletWebViewClient
import com.example.webview.VoraletWebViewConfig
import java.io.File

/**
 * Main Activity for Voralet Personal Finance App v3.0.1.
 * Architected with Clean Principles, Edge-to-Edge display, and robust fallback handling.
 * Eliminates GPU rendernode crashes in emulator containers by using native software rendering.
 */
class MainActivity : ComponentActivity() {

    private var currentWebView: WebView? = null
    private var rootContainer: FrameLayout? = null
    private var fileCallback: ValueCallback<Array<Uri>>? = null

    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
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
                // Clean any corrupted partial cache left over from previous runs so Chromium starts with a clean slate
                val webViewCache = File(context.cacheDir, "WebView")
                if (webViewCache.exists()) {
                    webViewCache.deleteRecursively()
                }
            } catch (t: Throwable) {
                Log.w(TAG, "Storage directory preparation notice: ${t.message}")
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prepareWebViewStorage(this)
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)

        // Enable edge-to-edge
        enableEdgeToEdge()

        if (VoraletWebViewConfig.isEmulator || !File("/dev/dri/renderD128").exists()) {
            window.clearFlags(WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED)
        } else {
            window.addFlags(WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED)
        }

        try {
            val insetsController = WindowCompat.getInsetsController(window, window.decorView)
            insetsController.isAppearanceLightStatusBars = true
            insetsController.isAppearanceLightNavigationBars = true
        } catch (t: Throwable) {
            Log.d(TAG, "Status bar appearance notice: ${t.message}")
        }

        // On physical devices with hardware acceleration, request high refresh rate
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R && !VoraletWebViewConfig.isEmulator && File("/dev/dri/renderD128").exists()) {
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

        // Back button navigation dispatcher
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                val wv = currentWebView
                if (wv != null) {
                    wv.evaluateJavascript("(function(){ return window.handleAndroidBack ? window.handleAndroidBack() : false; })()") { result ->
                        if (result != "true") {
                            if (wv.canGoBack()) {
                                wv.goBack()
                            } else {
                                finish()
                            }
                        }
                    }
                } else {
                    finish()
                }
            }
        })

        // Root container with edge-to-edge window insets handling
        val isHardwareGpuAvailable = !VoraletWebViewConfig.isEmulator && File("/dev/dri/renderD128").exists()
        val container = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(Color.parseColor("#F8FAFC"))
            if (!isHardwareGpuAvailable) {
                setLayerType(View.LAYER_TYPE_SOFTWARE, null)
            }
        }
        rootContainer = container
        setContentView(container)

        ViewCompat.setOnApplyWindowInsetsListener(container) { view, windowInsets ->
            val insets = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars())
            view.setPadding(insets.left, insets.top, insets.right, insets.bottom)
            windowInsets
        }

        setupWebView()
    }

    private fun setupWebView() {
        val container = rootContainer ?: return
        currentWebView?.let { wv ->
            container.removeView(wv)
            wv.destroy()
        }

        val isHardwareGpuAvailable = !VoraletWebViewConfig.isEmulator && File("/dev/dri/renderD128").exists()
        val webView = WebView(this).apply {
            if (!isHardwareGpuAvailable) {
                setLayerType(View.LAYER_TYPE_SOFTWARE, null)
            }
            VoraletWebViewConfig.applySettings(this, Color.parseColor("#F8FAFC"))

            val bridge = AndroidNativeBridge(this@MainActivity)
            addJavascriptInterface(bridge, AndroidNativeBridge.BRIDGE_NAME)

            webViewClient = VoraletWebViewClient(
                onCrashRecover = {
                    setupWebView()
                }
            )

            webChromeClient = VoraletWebChromeClient(
                fileChooserLauncher = fileChooserLauncher,
                onFileCallbackReady = { cb -> fileCallback = cb }
            )

            loadUrl("file:///android_asset/index.html")
        }

        currentWebView = webView
        container.addView(webView)
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
        rootContainer = null
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
                    VoraletWebViewConfig.applySettings(this, backgroundColor)

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
