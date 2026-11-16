package com.example.bridge

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.os.Build
import android.print.PrintAttributes
import android.print.PrintManager
import android.util.Base64
import android.webkit.JavascriptInterface
import android.webkit.WebView
import androidx.core.content.FileProvider
import androidx.core.view.WindowCompat
import com.example.export.ExcelXlsxExporter
import com.example.ocr.OfflineReceiptOcrEngine
import com.example.webview.VoraletWebViewConfig
import com.example.widget.PetWidgetProvider
import com.example.widget.StreakWidgetProvider
import org.json.JSONObject
import java.io.File
import java.util.concurrent.Executors

/**
 * High-performance, 100% Offline Native Android Bridge for Voralet.
 * Handles:
 * - Encrypted Home Widget sync
 * - Genuine OOXML (.xlsx) Excel generation & SAF save/share
 * - Offline bundled ML Kit Receipt OCR
 * - Print / PDF export & encrypted backup saving
 */
class AndroidNativeBridge(
    private val activity: Activity,
    private val webViewProvider: () -> WebView?,
    private val safSaveRequester: (fileName: String, mimeType: String, bytes: ByteArray) -> Unit
) {
    companion object {
        const val BRIDGE_NAME = "AndroidBridge"
        private const val XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    private val workerExecutor = Executors.newSingleThreadExecutor()

    @JavascriptInterface
    fun syncWidgetData(streakJson: String?, petJson: String?) {
        try {
            if (!streakJson.isNullOrEmpty()) {
                StreakWidgetProvider.saveStreakData(activity, streakJson)
            }
            if (!petJson.isNullOrEmpty()) {
                PetWidgetProvider.savePetData(activity, petJson)
            }
        } catch (_: Throwable) {}
    }

    @JavascriptInterface
    fun setStatusBarTheme(isDark: Boolean) {
        activity.runOnUiThread {
            try {
                val window = activity.window
                val insetsController = WindowCompat.getInsetsController(window, window.decorView)
                insetsController.isAppearanceLightStatusBars = !isDark
                insetsController.isAppearanceLightNavigationBars = !isDark
            } catch (_: Throwable) {}
        }
    }

    @JavascriptInterface
    fun printHtml(htmlContent: String?, jobTitle: String?) {
        if (htmlContent.isNullOrBlank()) return
        val title = jobTitle ?: "Laporan Keuangan Voralet"
        activity.runOnUiThread {
            try {
                val tempWebView = WebView(activity)
                tempWebView.webViewClient = object : android.webkit.WebViewClient() {
                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        try {
                            val printManager = activity.getSystemService(Context.PRINT_SERVICE) as? PrintManager
                            if (printManager != null && view != null) {
                                val printAdapter = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                                    view.createPrintDocumentAdapter(title)
                                } else {
                                    @Suppress("DEPRECATION")
                                    view.createPrintDocumentAdapter()
                                }
                                val printAttributes = PrintAttributes.Builder()
                                    .setMediaSize(PrintAttributes.MediaSize.ISO_A4)
                                    .setMinMargins(PrintAttributes.Margins.NO_MARGINS)
                                    .build()
                                printManager.print(title, printAdapter, printAttributes)
                            }
                        } catch (_: Throwable) {}
                    }
                }
                tempWebView.loadDataWithBaseURL(null, htmlContent, "text/html", "UTF-8", null)
            } catch (_: Throwable) {}
        }
    }

    /**
     * Generates a genuine OOXML (.xlsx) workbook offline on a background thread
     * and triggers either Android SAF "Save As" ("save") or system Share/Open chooser ("share").
     */
    @JavascriptInterface
    fun exportExcelXlsx(payloadJson: String?, fileName: String?, mode: String?): Boolean {
        if (payloadJson.isNullOrBlank()) return false
        val safeName = (fileName ?: "Voralet_Laporan_Keuangan.xlsx")
            .replace(Regex("[^a-zA-Z0-9._-]"), "_")
            .let { if (it.endsWith(".xlsx", ignoreCase = true)) it else "$it.xlsx" }

        workerExecutor.execute {
            try {
                val xlsxBytes = ExcelXlsxExporter.buildWorkbook(payloadJson)
                activity.runOnUiThread {
                    if (mode == "save") {
                        safSaveRequester(safeName, XLSX_MIME, xlsxBytes)
                    } else {
                        shareFileBytes(safeName, xlsxBytes, XLSX_MIME)
                    }
                    notifyExportStatus(true, safeName)
                }
            } catch (_: Throwable) {
                activity.runOnUiThread {
                    notifyExportStatus(false, safeName)
                }
            }
        }
        return true
    }

    /**
     * Saves arbitrary generated files (e.g. encrypted JSON backup, PDF) directly via Android Storage Access Framework
     * so users can store them cleanly into Downloads/Documents without storage permissions.
     */
    @JavascriptInterface
    fun saveFileToDevice(fileName: String?, contentBase64: String?, mimeType: String?): Boolean {
        if (fileName.isNullOrBlank() || contentBase64.isNullOrBlank()) return false
        return try {
            val bytes = Base64.decode(contentBase64, Base64.DEFAULT)
            val safeName = fileName.replace(Regex("[^a-zA-Z0-9._-]"), "_")
            val resolvedMime = mimeType ?: "application/octet-stream"
            activity.runOnUiThread {
                safSaveRequester(safeName, resolvedMime, bytes)
            }
            true
        } catch (_: Throwable) {
            false
        }
    }

    @JavascriptInterface
    fun shareOrSaveFile(fileName: String?, contentBase64: String?, mimeType: String?): Boolean {
        if (fileName.isNullOrBlank() || contentBase64.isNullOrBlank()) return false
        return try {
            val bytes = Base64.decode(contentBase64, Base64.DEFAULT)
            val safeName = fileName.replace(Regex("[^a-zA-Z0-9._-]"), "_")
            val resolvedMime = mimeType ?: XLSX_MIME
            shareFileBytes(safeName, bytes, resolvedMime)
        } catch (_: Throwable) {
            false
        }
    }

    /**
     * Performs 100% offline on-device OCR on a photographed or selected receipt image.
     */
    @JavascriptInterface
    fun recognizeReceiptText(base64Image: String?, callbackId: String?) {
        if (base64Image.isNullOrBlank() || callbackId.isNullOrBlank()) return
        workerExecutor.execute {
            OfflineReceiptOcrEngine.recognizeFromBase64(base64Image) { resultJson ->
                val quotedId = JSONObject.quote(callbackId)
                val quotedJson = JSONObject.quote(resultJson)
                activity.runOnUiThread {
                    try {
                        webViewProvider()?.evaluateJavascript(
                            "window.__onVoraletOcrResult && window.__onVoraletOcrResult($quotedId, $quotedJson);",
                            null
                        )
                    } catch (_: Throwable) {}
                }
            }
        }
    }

    private fun shareFileBytes(safeName: String, bytes: ByteArray, mimeType: String): Boolean {
        return try {
            val exportDir = File(activity.cacheDir, "exports").apply { mkdirs() }
            exportDir.listFiles()?.forEach { f ->
                if (System.currentTimeMillis() - f.lastModified() > 86_400_000L) f.delete()
            }
            val file = File(exportDir, safeName)
            file.writeBytes(bytes)

            val uri = FileProvider.getUriForFile(
                activity,
                "${activity.packageName}.fileprovider",
                file
            )
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = mimeType
                putExtra(Intent.EXTRA_STREAM, uri)
                putExtra(Intent.EXTRA_SUBJECT, safeName)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            activity.startActivity(Intent.createChooser(intent, "Buka atau Simpan $safeName"))
            true
        } catch (_: Throwable) {
            false
        }
    }

    private fun notifyExportStatus(success: Boolean, fileName: String) {
        try {
            val quotedName = JSONObject.quote(fileName)
            webViewProvider()?.evaluateJavascript(
                "window.__onVoraletExportResult && window.__onVoraletExportResult($success, $quotedName);",
                null
            )
        } catch (_: Throwable) {}
    }

    fun release() {
        try {
            workerExecutor.shutdownNow()
        } catch (_: Throwable) {}
    }
}
