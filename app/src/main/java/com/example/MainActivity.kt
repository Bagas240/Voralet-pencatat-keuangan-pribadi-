package com.example

import android.annotation.SuppressLint
import android.os.Build
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.util.Log
import android.webkit.ConsoleMessage
import android.content.Intent
import android.net.Uri
import android.webkit.ValueCallback
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import android.app.Application
import android.content.Context
import java.io.File
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.viewinterop.AndroidView
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {
  companion object {
    fun prepareWebViewStorage(context: Context) {
      try {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
          val processName = Application.getProcessName()
          if (context.packageName != processName) {
            WebView.setDataDirectorySuffix(processName)
          }
        }
        val cache = context.cacheDir
        val dirs = listOf(
          File(cache, "WebView"),
          File(cache, "WebView/Default"),
          File(cache, "WebView/Default/HTTP Cache"),
          File(cache, "WebView/Default/HTTP Cache/index-dir"),
          File(cache, "WebView/Default/Code Cache"),
          File(cache, "WebView/Default/Code Cache/js"),
          File(cache, "WebView/Default/Code Cache/wasm"),
          File(cache, "org.chromium.android_webview"),
          File(cache, "org.chromium.android_webview/HTTP Cache"),
          File(cache, "org.chromium.android_webview/HTTP Cache/index-dir"),
          File(context.filesDir, "WebView")
        )
        for (dir in dirs) {
          if (dir.isFile) {
            dir.delete()
          }
          if (!dir.exists()) {
            dir.mkdirs()
          }
          dir.setReadable(true, false)
          dir.setWritable(true, false)
          dir.setExecutable(true, false)
        }
      } catch (t: Throwable) {
        Log.w("MainActivity", "Error preparing WebView storage directories", t)
      }
    }
  }

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    prepareWebViewStorage(this)

    WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
    enableEdgeToEdge()
    setContent {
      MyApplicationTheme {
        val bgColor = MaterialTheme.colorScheme.background
        Box(
          modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .imePadding()
            .background(bgColor)
        ) {
          SakuCleanWebView(backgroundColor = bgColor.toArgb())
        }
      }
    }
  }
}

@SuppressLint("SetJavaScriptEnabled")
@Composable
fun SakuCleanWebView(
  backgroundColor: Int = android.graphics.Color.WHITE,
  modifier: Modifier = Modifier
) {
  var reloadKey by remember { mutableIntStateOf(0) }
  var webViewRef by remember { mutableStateOf<WebView?>(null) }
  var fileUploadCallback by remember { mutableStateOf<ValueCallback<Array<Uri>>?>(null) }

  val fileChooserLauncher = rememberLauncherForActivityResult(
    contract = ActivityResultContracts.StartActivityForResult()
  ) { result ->
    val uri = result.data?.data
    if (uri != null) {
      fileUploadCallback?.onReceiveValue(arrayOf(uri))
    } else {
      val clipData = result.data?.clipData
      if (clipData != null && clipData.itemCount > 0) {
        val uris = Array(clipData.itemCount) { i -> clipData.getItemAt(i).uri }
        fileUploadCallback?.onReceiveValue(uris)
      } else {
        fileUploadCallback?.onReceiveValue(null)
      }
    }
    fileUploadCallback = null
  }

  BackHandler(enabled = true) {
    if (webViewRef?.canGoBack() == true) {
      webViewRef?.goBack()
    }
  }

  key(reloadKey) {
    AndroidView(
      modifier = modifier.fillMaxSize(),
      factory = { context ->
        WebView(context).apply {
          layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
          )
          setBackgroundColor(backgroundColor)

          @Suppress("DEPRECATION")
          settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = false
            allowFileAccessFromFileURLs = false
            allowUniversalAccessFromFileURLs = false
            cacheMode = WebSettings.LOAD_DEFAULT
            useWideViewPort = true
            loadWithOverviewMode = true
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            setSupportMultipleWindows(false)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
              safeBrowsingEnabled = true
            }
          }

          webViewClient = object : WebViewClient() {
            override fun onReceivedError(
              view: WebView?,
              request: WebResourceRequest?,
              error: WebResourceError?
            ) {
              super.onReceivedError(view, request, error)
              Log.w("WebView", "Resource error on ${request?.url}: ${error?.description}")
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
              Log.e("WebView", "onRenderProcessGone: didCrash=$didCrash")
              view?.let { wv ->
                (wv.parent as? ViewGroup)?.removeView(wv)
                wv.destroy()
              }
              webViewRef = null
              reloadKey++
              return true
            }
          }

          webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
              Log.d("WebViewConsole", "${consoleMessage?.message()} [line ${consoleMessage?.lineNumber()}]")
              return true
            }

            override fun onShowFileChooser(
              webView: WebView?,
              filePathCallback: ValueCallback<Array<Uri>>?,
              fileChooserParams: FileChooserParams?
            ): Boolean {
              fileUploadCallback?.onReceiveValue(null)
              fileUploadCallback = filePathCallback
              val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                type = "*/*"
              }
              return try {
                fileChooserLauncher.launch(intent)
                true
              } catch (e: Exception) {
                fileUploadCallback?.onReceiveValue(null)
                fileUploadCallback = null
                false
              }
            }
          }

          loadUrl("file:///android_asset/index.html")
          webViewRef = this
        }
      },
      update = { webView ->
        webViewRef = webView
      }
    )
  }
}

