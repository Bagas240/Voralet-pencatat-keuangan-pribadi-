package com.example

import android.Manifest
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
import androidx.activity.SystemBarStyle
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import com.example.bridge.AndroidNativeBridge
import com.example.notification.VoraletNotificationHelper
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
 * 100% Offline Vault, Edge-to-Edge, FLAG_SECURE vault protection, zero-permission camera/SAF integration,
 * optional POST_NOTIFICATIONS for Pet/Streak reminders, and battery-aware animation throttling.
 */
class MainActivity : ComponentActivity() {

    private var currentWebView: WebView? = null
    private var nativeBridge: AndroidNativeBridge? = null
    private var rootContainer: FrameLayout? = null
    private var fileCallback: ValueCallback<Array<Uri>>? = null
    private var pendingCameraUri: Uri? = null
    private var pendingExportBytes: ByteArray? = null
    private var pendingTestNotifOnGrant = false
    private val ioExecutor = Executors.newSingleThreadExecutor()
    private var lastSafeTopDp = 0f
    private var lastSafeBottomDp = 0f
    private var lastSafeLeftDp = 0f
    private var lastSafeRightDp = 0f

    private val notificationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        val shouldTest = pendingTestNotifOnGrant
        pendingTestNotifOnGrant = false
        if (granted && shouldTest) {
            VoraletNotificationHelper.showPetAndStreakNotification(this, isTest = true)
        }
        currentWebView?.evaluateJavascript(
            "window.__onVoraletNotificationPermission && window.__onVoraletNotificationPermission($granted);",
            null
        )
    }

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
        super.onCreate(savedInstanceState)
        prepareWebViewStorage(this)
        VoraletNotificationHelper.ensureChannel(this)

        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.auto(Color.TRANSPARENT, Color.TRANSPARENT),
            navigationBarStyle = SystemBarStyle.auto(Color.TRANSPARENT, Color.TRANSPARENT)
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            window.isStatusBarContrastEnforced = false
            window.isNavigationBarContrastEnforced = false
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            window.attributes = window.attributes.apply {
                layoutInDisplayCutoutMode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                } else {
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                }
            }
        }

        // Anti-Screen Scraping & Malware Screenshot Protection on physical release devices only
        // (FLAG_SECURE blacks out VirtualDisplay / Streaming Emulator frames if enabled on emulators)
        if (!VoraletWebViewConfig.isEmulator && !AppSecurityGuard.isDebuggableBuild(this)) {
            try {
                window.setFlags(
                    WindowManager.LayoutParams.FLAG_SECURE,
                    WindowManager.LayoutParams.FLAG_SECURE
                )
            } catch (_: Throwable) {}
        }

        // Runtime Integrity Guard (Anti-Debugger, Anti-Frida, Signature Check)
        var securityWarning = false
        try {
            val report = AppSecurityGuard.verifyEnvironmentIntegrity(this)
            if (!report.isSafe && !VoraletWebViewConfig.isEmulator && !AppSecurityGuard.isDebuggableBuild(this)) {
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
        window.decorView.setBackgroundColor(initialBg)
        setContentView(container)

        ViewCompat.setOnApplyWindowInsetsListener(container) { view, windowInsets ->
            val safeInsets = windowInsets.getInsets(
                WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout()
            )
            val imeInsets = windowInsets.getInsets(WindowInsetsCompat.Type.ime())

            // Full-bleed edge-to-edge: never pad top/bottom/sides for system bars (no black gaps);
            // only apply bottom padding while the soft keyboard (IME) is visible.
            view.setPadding(0, 0, 0, imeInsets.bottom)

            val density = resources.displayMetrics.density.takeIf { it > 0f } ?: 1f
            lastSafeTopDp = safeInsets.top / density
            lastSafeBottomDp = if (imeInsets.bottom > 0) 0f else (safeInsets.bottom / density)
            lastSafeLeftDp = safeInsets.left / density
            lastSafeRightDp = safeInsets.right / density
            pushSafeAreaToWebView()

            windowInsets
        }

        setupWebView(initialBg, securityWarning)
    }

    private fun pushSafeAreaToWebView() {
        val wv = currentWebView ?: return
        val top = "%.2f".format(java.util.Locale.US, lastSafeTopDp)
        val bottom = "%.2f".format(java.util.Locale.US, lastSafeBottomDp)
        val left = "%.2f".format(java.util.Locale.US, lastSafeLeftDp)
        val right = "%.2f".format(java.util.Locale.US, lastSafeRightDp)
        val js = """
            (function() {
              var root = document.documentElement;
              if (root && root.style) {
                root.style.setProperty('--voralet-safe-top', '${top}px');
                root.style.setProperty('--voralet-safe-bottom', '${bottom}px');
                root.style.setProperty('--voralet-safe-left', '${left}px');
                root.style.setProperty('--voralet-safe-right', '${right}px');
              }
              if (window.__setVoraletSafeArea) {
                window.__setVoraletSafeArea(${top}, ${bottom}, ${left}, ${right});
              }
            })();
        """.trimIndent()
        wv.post {
            try {
                wv.evaluateJavascript(js, null)
            } catch (_: Throwable) {}
        }
    }

    private fun requestNotificationPermission(sendTestAfterGrant: Boolean) {
        if (VoraletNotificationHelper.hasNotificationPermission(this)) {
            if (sendTestAfterGrant) {
                VoraletNotificationHelper.showPetAndStreakNotification(this, isTest = true)
            }
            currentWebView?.evaluateJavascript(
                "window.__onVoraletNotificationPermission && window.__onVoraletNotificationPermission(true);",
                null
            )
            return
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            pendingTestNotifOnGrant = sendTestAfterGrant
            notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
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
            safSaveRequester = ::launchSaveDocument,
            notificationPermissionRequester = ::requestNotificationPermission
        )
        nativeBridge = bridge

        val webView = WebView(this).apply {
            VoraletWebViewConfig.applySettings(this, backgroundColor)
            addJavascriptInterface(bridge, AndroidNativeBridge.BRIDGE_NAME)

            webViewClient = VoraletWebViewClient(
                appContext = applicationContext,
                tamperLocked = securityWarning,
                onPageFinishedCallback = {
                    rootContainer?.let { ViewCompat.requestApplyInsets(it) }
                    pushSafeAreaToWebView()
                },
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
