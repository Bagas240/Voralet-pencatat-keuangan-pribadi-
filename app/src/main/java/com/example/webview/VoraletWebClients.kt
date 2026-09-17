package com.example.webview

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.util.Log
import android.webkit.ConsoleMessage
import android.webkit.JsResult
import android.webkit.RenderProcessGoneDetail
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.result.ActivityResultLauncher

class VoraletWebViewClient(
    private val onCrashRecover: () -> Unit
) : WebViewClient() {

    companion object {
        private const val TAG = "VoraletWebViewClient"
    }

    override fun shouldOverrideUrlLoading(
        view: WebView?,
        request: WebResourceRequest?
    ): Boolean {
        val uri = request?.url ?: return false
        val url = uri.toString()

        // Only allow trusted local asset files inside the WebView
        if (url.startsWith("file:///android_asset/")) {
            return false
        }

        // Open external web links or external intent protocols safely via the Android system
        try {
            val intent = Intent(Intent.ACTION_VIEW, uri).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            view?.context?.startActivity(intent)
        } catch (e: Exception) {
            Log.w(TAG, "Blocked or unable to open external URL: $url", e)
        }
        return true
    }

    override fun onReceivedError(
        view: WebView?,
        request: WebResourceRequest?,
        error: WebResourceError?
    ) {
        super.onReceivedError(view, request, error)
        if (request?.isForMainFrame == true) {
            Log.w(TAG, "Main frame error: ${error?.description} (code ${error?.errorCode})")
        }
    }

    override fun onRenderProcessGone(
        view: WebView?,
        detail: RenderProcessGoneDetail?
    ): Boolean {
        val didCrash = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            detail?.didCrash() ?: false
        } else {
            false
        }
        Log.e(TAG, "Render process gone! Crash: $didCrash. Initiating clean recovery.")
        onCrashRecover()
        return true
    }
}

class VoraletWebChromeClient(
    private val fileChooserLauncher: ActivityResultLauncher<Intent>,
    private val onFileCallbackReady: (ValueCallback<Array<Uri>>?) -> Unit
) : WebChromeClient() {

    companion object {
        private const val TAG = "VoraletWebChrome"
    }

    override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
        val msg = consoleMessage?.message() ?: ""
        val line = consoleMessage?.lineNumber() ?: 0
        val source = consoleMessage?.sourceId() ?: ""
        if (consoleMessage?.messageLevel() == ConsoleMessage.MessageLevel.ERROR) {
            Log.e(TAG, "[$source:$line] $msg")
        } else {
            Log.d(TAG, "[$source:$line] $msg")
        }
        return true
    }

    override fun onShowFileChooser(
        webView: WebView?,
        filePathCallback: ValueCallback<Array<Uri>>?,
        fileChooserParams: FileChooserParams?
    ): Boolean {
        onFileCallbackReady(filePathCallback)
        val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "*/*"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        return try {
            fileChooserLauncher.launch(intent)
            true
        } catch (e: Exception) {
            Log.w(TAG, "File chooser launch failed", e)
            onFileCallbackReady(null)
            false
        }
    }

    override fun onJsConfirm(
        view: WebView?,
        url: String?,
        message: String?,
        result: JsResult?
    ): Boolean {
        val context = view?.context ?: return false
        try {
            android.app.AlertDialog.Builder(context)
                .setTitle("Konfirmasi")
                .setMessage(message ?: "Apakah Anda yakin ingin melanjutkan?")
                .setPositiveButton("Hapus") { _, _ ->
                    result?.confirm()
                }
                .setNegativeButton("Batal") { _, _ ->
                    result?.cancel()
                }
                .setOnCancelListener {
                    result?.cancel()
                }
                .setCancelable(true)
                .create()
                .show()
            return true
        } catch (e: Exception) {
            Log.w(TAG, "Native onJsConfirm dialog error", e)
            result?.cancel()
            return false
        }
    }

    override fun onJsAlert(
        view: WebView?,
        url: String?,
        message: String?,
        result: JsResult?
    ): Boolean {
        val context = view?.context ?: return false
        try {
            android.app.AlertDialog.Builder(context)
                .setTitle("Pemberitahuan")
                .setMessage(message ?: "")
                .setPositiveButton("OK") { _, _ ->
                    result?.confirm()
                }
                .setOnCancelListener {
                    result?.confirm()
                }
                .setCancelable(true)
                .create()
                .show()
            return true
        } catch (e: Exception) {
            Log.w(TAG, "Native onJsAlert dialog error", e)
            result?.confirm()
            return false
        }
    }
}
