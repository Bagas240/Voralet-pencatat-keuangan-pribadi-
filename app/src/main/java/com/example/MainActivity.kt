package com.example

import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.ViewGroup
import android.view.WindowManager
import android.webkit.ValueCallback
import android.webkit.WebView
import android.widget.FrameLayout
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import com.example.bridge.AndroidNativeBridge
import com.example.security.AppSecurityGuard
import com.example.webview.VoraletWebChromeClient
import com.example.webview.VoraletWebViewClient
import com.example.webview.VoraletWebViewConfig
import com.example.widget.PetWidgetProvider
import com.example.widget.StreakWidgetProvider
import java.io.File
import java.util.concurrent.Executors

/**
 * Main Activity for Voralet Personal Finance App.
 * 100% Offline, Edge-to-Edge, FLAG_SECURE vault protection, zero-permission camera/SAF integration,
 * and battery-aware animation throttling on pause/background.
 */
class MainActivity : ComponentActivity() {

    private var currentWebView: WebView? = null
    private var nativeBridge: AndroidNativeBridge? = null
    private var rootContainer: FrameLayout? = null
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private var pendingCameraUri: Uri? = null
    private var pendingExportBytes: ByteArray? = null
    private val ioExecutor = Executors.newSingleThreadExecutor()

    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val callback = fileCallback
        fileCallback = null
        val capturedUri = pendingCameraUri
        pendingCameraUri = null

        if (callback == null) return@registerForActivityResult

        if (result.resultCode == RESULT_OK) {
            val dataUri = result.data?.data
            if (dataUri != null) {
                callback.onReceiveValue(arrayOf(dataUri))
            } else if (result.data?.clipData != null && result.data!!.clipData!!.itemCount > 0) {
                val clip = result.data!!.clipData!!
                callback.onReceiveValue(Array(clip.itemCount) { i -> clip.getItemAt(i).uri })
            } else if (capturedUri != null) {
                callback.onReceiveValue(arrayOf(capturedUri))
            } else {
                callback.onReceiveValue(null)
            }
        } else {
            callback.onReceiveValue(null)
        }
    }

    private val saveDocumentLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val bytesToWrite = pendingExportBytes
        pendingExportBytes = null
        val destUri = result.data?.data
        if (result.resultCode == RESULT_OK && destUri != null && bytesToWrite != null) {
            ioExecutor.execute {
                try {
                    contentResolver.openOutputStream(destUri)?.use { os ->
                        os.write(bytesToWrite)
                        os.flush()
                    }
                } catch (_: Throwable) {}
            }
        }
    }

    companion object {
        fun prepareWebViewStorage(context: Context) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                    if (android.os.Process.isIsolated()) return
                    val processName = android.app.Application.getProcessName()
                    if (context.packageName != processName) {
                        WebView.setDataDirectorySuffix(processName)
                    }
                }
                val httpCacheDir = File(context.cacheDir, "WebView/Default/HTTP Cache")
                File(httpCacheDir, "index-dir").mkdirs()
                File(httpCacheDir, "Code Cache/wasm").mkdirs()
                File(httpCacheDir, "Code Cache/js").mkdirs()
            } catch (_: Throwable) {}
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        if (VoraletWebViewConfig.isEmulator) {
            try {
                android.system.Os.setenv("LIBGL_DRI3_DISABLE", "1", true)
                android.system.Os.setenv("EGL_LOG_LEVEL", "fatal", true)
                android.system.Os.setenv("MESA_DEBUG", "0", true)
                android.system.Os.setenv("MESA_LOG_LEVEL", "fatal", true)
                android.system.Os.setenv("LIBGL_DEBUG", "quiet", true)
                android.system.Os.setenv("MESA_LOG_FILE", "/dev/null", true)
                System.setProperty("log.tag.MESA", "SUPPRESS")
                File("/data/local/tmp/webview-command-line").writeText(
                    "_ --disable-gpu --disable-gpu-rasterization --disable-gpu-compositing"
                )
            } catch (_: Throwable) {}
        }

        super.onCreate(savedInstanceState)
        prepareWebViewStorage(this)

        enableEdgeToEdge()

        // Anti-Screen Scraping & Malware Screenshot Protection for Financial Vault & PINs
        try {
            window.setFlags(
                WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE
            )
        } catch (_: Throwable) {}

        // Runtime Integrity Guard (Anti-Debugger, Anti-Frida, Signature Check)
        var securityWarning = false
        try {
            val report = AppSecurityGuard.verifyEnvironmentIntegrity(this)
            if (!report.isSafe && !VoraletWebViewConfig.isEmulator) {
                securityWarning = true
            }
        } catch (_: Throwable) {}

        val isSystemDark = (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) ==
            Configuration.UI_MODE_NIGHT_YES
        val initialBg = if (isSystemDark) Color.parseColor("#0F172A") else Color.parseColor("#F8FAFC")

        try {
            val insetsController = WindowCompat.getInsetsController(window, window.decorView)
            insetsController.isAppearanceLightStatusBars = !isSystemDark
            insetsController.isAppearanceLightNavigationBars = !isSystemDark
        } catch (_: Throwable) {}

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

        val container = FrameLayout(this).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            setBackgroundColor(initialBg)
        }
        rootContainer = container
        setContentView(container)

        ViewCompat.setOnApplyWindowInsetsListener(container) { view, windowInsets ->
            val insets = windowInsets.getInsets(WindowInsetsCompat.Type.systemBars())
            view.setPadding(insets.left, insets.top, insets.right, insets.bottom)
            windowInsets
        }

        setupWebView(initialBg, securityWarning)
    }

    private fun launchSaveDocument(fileName: String, mimeType: String, bytes: ByteArray) {
        pendingExportBytes = bytes
        try {
            val intent = Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = mimeType
                putExtra(Intent.EXTRA_TITLE, fileName)
            }
            saveDocumentLauncher.launch(intent)
        } catch (_: Throwable) {
            pendingExportBytes = null
            nativeBridge?.shareOrSaveFile(
                fileName,
                android.util.Base64.encodeToString(bytes, android.util.Base64.NO_WRAP),
                mimeType
            )
        }
    }

    private fun setupWebView(backgroundColor: Int, securityWarning: Boolean = false) {
        val container = rootContainer ?: return
        currentWebView?.let { wv ->
            container.removeView(wv)
            wv.destroy()
        }
        nativeBridge?.release()

        val bridge = AndroidNativeBridge(
            activity = this,
            webViewProvider = { currentWebView },
            safSaveRequester = ::launchSaveDocument
        )
        nativeBridge = bridge

        val webView = WebView(this).apply {
            VoraletWebViewConfig.applySettings(this, backgroundColor)
            addJavascriptInterface(bridge, AndroidNativeBridge.BRIDGE_NAME)

            webViewClient = VoraletWebViewClient(
                appContext = applicationContext,
                onCrashRecover = {
                    setupWebView(backgroundColor, securityWarning)
                }
            )

            webChromeClient = VoraletWebChromeClient(
                context = this@MainActivity,
                fileChooserLauncher = fileChooserLauncher,
                onFileCallbackReady = { cb -> fileCallback = cb },
                onCameraUriReady = { uri -> pendingCameraUri = uri }
            )

            loadUrl(VoraletWebViewConfig.ENTRY_URL)
        }

        if (securityWarning) {
            webView.postDelayed({
                webView.evaluateJavascript("window.__VORALET_TAMPER_DETECTED__ = true;", null)
            }, 800)
        }

        currentWebView = webView
        container.addView(webView)
    }

    override fun onResume() {
        super.onResume()
        currentWebView?.let { wv ->
            wv.onResume()
            wv.resumeTimers()
            wv.evaluateJavascript(
                "document.documentElement.classList.remove('voralet-paused'); window.dispatchEvent(new Event('voralet-resume'));",
                null
            )
        }
        try {
            StreakWidgetProvider.updateAllWidgets(this)
            PetWidgetProvider.updateAllWidgets(this)
        } catch (_: Throwable) {}
    }

    override fun onPause() {
        currentWebView?.let { wv ->
            wv.evaluateJavascript("document.documentElement.classList.add('voralet-paused');", null)
            wv.onPause()
            wv.pauseTimers()
        }
        super.onPause()
    }

    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        if (level >= TRIM_MEMORY_BACKGROUND) {
            currentWebView?.clearCache(false)
        }
    }

    override fun onDestroy() {
        try {
            ioExecutor.shutdownNow()
        } catch (_: Throwable) {}
        nativeBridge?.release()
        nativeBridge = null
        currentWebView?.let { wv ->
            (wv.parent as? ViewGroup)?.removeView(wv)
            wv.destroy()
        }
        currentWebView = null
        rootContainer = null
        super.onDestroy()
    }
}
