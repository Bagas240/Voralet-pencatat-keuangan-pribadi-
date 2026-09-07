package com.example

import android.annotation.SuppressLint
import android.os.Build
import android.os.Bundle
import android.view.ViewGroup
import android.util.Log
import android.webkit.ConsoleMessage
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
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.viewinterop.AndroidView
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
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
  backgroundColor: Int,
  modifier: Modifier = Modifier
) {
  var reloadKey by remember { mutableIntStateOf(0) }
  var webViewRef by remember { mutableStateOf<WebView?>(null) }

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

          settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            allowFileAccessFromFileURLs = true
            allowUniversalAccessFromFileURLs = true
            cacheMode = WebSettings.LOAD_DEFAULT
            useWideViewPort = true
            loadWithOverviewMode = true
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
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

