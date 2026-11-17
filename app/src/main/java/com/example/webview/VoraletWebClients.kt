package com.example.webview

import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import android.webkit.ConsoleMessage
import android.webkit.JsResult
import android.webkit.PermissionRequest
import android.webkit.RenderProcessGoneDetail
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.result.ActivityResultLauncher
import androidx.core.content.FileProvider
import com.example.security.AppSecurityGuard
import com.example.security.AssetVaultDecryptor
import java.io.ByteArrayInputStream
import java.io.File

class VoraletWebViewClient(
    private val appContext: Context,
    private val tamperLocked: Boolean = false,
    private val onCrashRecover: () -> Unit
) : WebViewClient() {

    private val allowedAssetPattern = Regex("^[a-zA-Z0-9._-]+$")

    override fun shouldInterceptRequest(
        view: WebView?,
        request: WebResourceRequest?
    ): WebResourceResponse? {
        if (tamperLocked) {
            return blockedResponse()
        }
        val uri = request?.url ?: return blockedResponse()
        val scheme = uri.scheme?.lowercase()

        if (scheme == "data" || scheme == "blob") {
            return null
        }

        if (scheme != "https" || uri.host != VoraletWebViewConfig.VIRTUAL_HOST) {
            return blockedResponse()
        }

        val rawPath = (uri.encodedPath ?: "/").trimStart('/')
        val normalizedPath = if (rawPath.startsWith("assets/")) {
            rawPath.removePrefix("assets/")
        } else {
            rawPath
        }

        if (normalizedPath.isEmpty() || normalizedPath == "index.html") {
            return try {
                val htmlBytes = AssetVaultDecryptor.loadDecryptedHtml(appContext)
                WebResourceResponse(
                    "text/html",
                    "UTF-8",
                    200,
                    "OK",
                    mapOf(
                        "Cache-Control" to "no-store, no-cache, must-revalidate",
                        "X-Content-Type-Options" to "nosniff"
                    ),
                    ByteArrayInputStream(htmlBytes)
                )
            } catch (_: Throwable) {
                blockedResponse()
            }
        }

        if (normalizedPath.startsWith("vendor/") && !normalizedPath.contains("..")) {
            val fileName = normalizedPath.removePrefix("vendor/")
            if (allowedAssetPattern.matches(fileName)) {
                return try {
                    val stream = appContext.assets.open("vendor/$fileName")
                    WebResourceResponse(
                        mimeTypeFor(fileName),
                        "UTF-8",
                        200,
                        "OK",
                        mapOf(
                            "Cache-Control" to "no-store, no-cache, must-revalidate",
                            "X-Content-Type-Options" to "nosniff"
                        ),
                        stream
                    )
                } catch (_: Throwable) {
                    blockedResponse()
                }
            }
        }

        return blockedResponse()
    }

    override fun shouldOverrideUrlLoading(
        view: WebView?,
        request: WebResourceRequest?
    ): Boolean {
        if (tamperLocked) return true
        val uri = request?.url ?: return true
        val urlString = uri.toString()
        val isTrusted = AppSecurityGuard.isTrustedLocalOrigin(urlString) &&
            uri.scheme.equals("https", ignoreCase = true) &&
            uri.host == VoraletWebViewConfig.VIRTUAL_HOST
        // Strict offline policy: block navigation to any external or file:// URL
        return !isTrusted
    }

    override fun onRenderProcessGone(
        view: WebView?,
        detail: RenderProcessGoneDetail?
    ): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            detail?.didCrash()
        }
        onCrashRecover()
        return true
    }

    private fun mimeTypeFor(fileName: String): String = when {
        fileName.endsWith(".js", ignoreCase = true) -> "application/javascript"
        fileName.endsWith(".css", ignoreCase = true) -> "text/css"
        fileName.endsWith(".svg", ignoreCase = true) -> "image/svg+xml"
        fileName.endsWith(".png", ignoreCase = true) -> "image/png"
        fileName.endsWith(".webp", ignoreCase = true) -> "image/webp"
        fileName.endsWith(".html", ignoreCase = true) -> "text/html"
        else -> "application/octet-stream"
    }

    private fun blockedResponse(): WebResourceResponse = WebResourceResponse(
        "text/plain",
        "UTF-8",
        403,
        "Forbidden",
        mapOf("Cache-Control" to "no-store"),
        ByteArrayInputStream(ByteArray(0))
    )
}

class VoraletWebChromeClient(
    private val context: Context,
    private val fileChooserLauncher: ActivityResultLauncher<Intent>,
    private val onFileCallbackReady: (ValueCallback<Array<Uri>>?) -> Unit,
    private val onCameraUriReady: (Uri?) -> Unit
) : WebChromeClient() {

    override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
        // Silence console output in production to prevent sensitive ledger leaks to logcat
        return true
    }

    override fun onPermissionRequest(request: PermissionRequest?) {
        // Zero permissions policy: strictly deny all web API hardware permission requests
        try {
            request?.deny()
        } catch (_: Throwable) {}
    }

    override fun onShowFileChooser(
        webView: WebView?,
        filePathCallback: ValueCallback<Array<Uri>>?,
        fileChooserParams: FileChooserParams?
    ): Boolean {
        onFileCallbackReady(filePathCallback)
        onCameraUriReady(null)

        return try {
            val isCapture = fileChooserParams?.isCaptureEnabled == true
            val acceptsImage = fileChooserParams?.acceptTypes?.any {
                it.contains("image", ignoreCase = true)
            } == true

            val launchIntent: Intent = if (isCapture && acceptsImage) {
                val captureDir = File(context.cacheDir, "receipt_captures").apply { mkdirs() }
                // Clean stale temp captures older than 1 hour
                captureDir.listFiles()?.forEach { f ->
                    if (System.currentTimeMillis() - f.lastModified() > 3600_000L) f.delete()
                }
                val photoFile = File(captureDir, "struk_${System.currentTimeMillis()}.jpg")
                val photoUri = FileProvider.getUriForFile(
                    context,
                    "${context.packageName}.fileprovider",
                    photoFile
                )
                val cameraIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
                    putExtra(MediaStore.EXTRA_OUTPUT, photoUri)
                    addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION or Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }
                if (cameraIntent.resolveActivity(context.packageManager) != null) {
                    onCameraUriReady(photoUri)
                    cameraIntent
                } else {
                    onCameraUriReady(null)
                    buildPickerIntent(fileChooserParams)
                }
            } else {
                buildPickerIntent(fileChooserParams)
            }

            fileChooserLauncher.launch(launchIntent)
            true
        } catch (_: Throwable) {
            onCameraUriReady(null)
            onFileCallbackReady(null)
            false
        }
    }

    private fun buildPickerIntent(params: FileChooserParams?): Intent {
        val acceptsImageOnly = params?.acceptTypes?.any { it.startsWith("image/", ignoreCase = true) } == true &&
            params.acceptTypes.none { it.contains("json", ignoreCase = true) || it.contains("csv", ignoreCase = true) }

        if (acceptsImageOnly && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            return Intent(MediaStore.ACTION_PICK_IMAGES).apply {
                type = "image/*"
            }
        }
        return params?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
            type = if (acceptsImageOnly) "image/*" else "*/*"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
    }

    override fun onJsConfirm(
        view: WebView?,
        url: String?,
        message: String?,
        result: JsResult?
    ): Boolean {
        val ctx = view?.context ?: return false
        return try {
            AlertDialog.Builder(ctx)
                .setTitle("Konfirmasi")
                .setMessage(message ?: "Apakah Anda yakin ingin melanjutkan?")
                .setPositiveButton("Ya, Lanjutkan") { _, _ -> result?.confirm() }
                .setNegativeButton("Batal") { _, _ -> result?.cancel() }
                .setOnCancelListener { result?.cancel() }
                .setCancelable(true)
                .create()
                .show()
            true
        } catch (_: Throwable) {
            result?.cancel()
            false
        }
    }

    override fun onJsAlert(
        view: WebView?,
        url: String?,
        message: String?,
        result: JsResult?
    ): Boolean {
        val ctx = view?.context ?: return false
        return try {
            AlertDialog.Builder(ctx)
                .setTitle("Pemberitahuan")
                .setMessage(message ?: "")
                .setPositiveButton("OK") { _, _ -> result?.confirm() }
                .setOnCancelListener { result?.confirm() }
                .setCancelable(true)
                .create()
                .show()
            true
        } catch (_: Throwable) {
            result?.confirm()
            false
        }
    }
}
