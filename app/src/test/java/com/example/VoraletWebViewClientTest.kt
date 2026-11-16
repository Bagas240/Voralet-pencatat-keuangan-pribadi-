package com.example

import android.content.Context
import android.net.Uri
import android.webkit.WebResourceRequest
import androidx.test.core.app.ApplicationProvider
import com.example.webview.VoraletWebViewClient
import com.example.webview.VoraletWebViewConfig
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class VoraletWebViewClientTest {

  private fun fakeRequest(urlString: String): WebResourceRequest = object : WebResourceRequest {
    override fun getUrl(): Uri = Uri.parse(urlString)
    override fun isForMainFrame(): Boolean = true
    override fun isRedirect(): Boolean = false
    override fun hasGesture(): Boolean = false
    override fun getMethod(): String = "GET"
    override fun getRequestHeaders(): MutableMap<String, String> = mutableMapOf()
  }

  @Test
  fun `serves decrypted index html over virtual https origin`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val client = VoraletWebViewClient(context) {}

    val response = client.shouldInterceptRequest(null, fakeRequest(VoraletWebViewConfig.ENTRY_URL))
    assertNotNull(response)
    assertEquals(200, response!!.statusCode)
    assertEquals("text/html", response.mimeType)
    val html = response.data.readBytes().toString(Charsets.UTF_8)
    assertTrue(html.contains("""<div id="root"></div>"""))
  }

  @Test
  fun `serves bundled vendor scripts and blocks traversal or external hosts`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val client = VoraletWebViewClient(context) {}

    val vendorResp = client.shouldInterceptRequest(
      null,
      fakeRequest("https://${VoraletWebViewConfig.VIRTUAL_HOST}/vendor/react.production.min.js")
    )
    assertNotNull(vendorResp)
    assertEquals(200, vendorResp!!.statusCode)
    assertEquals("application/javascript", vendorResp.mimeType)
    assertTrue(vendorResp.data.readBytes().isNotEmpty())

    val traversalResp = client.shouldInterceptRequest(
      null,
      fakeRequest("https://${VoraletWebViewConfig.VIRTUAL_HOST}/vendor/../voralet_core.bin")
    )
    assertNotNull(traversalResp)
    assertEquals(403, traversalResp!!.statusCode)

    val externalResp = client.shouldInterceptRequest(null, fakeRequest("https://example.com/payload.js"))
    assertNotNull(externalResp)
    assertEquals(403, externalResp!!.statusCode)

    val fileAssetResp = client.shouldInterceptRequest(null, fakeRequest("file:///android_asset/index.html"))
    assertNotNull(fileAssetResp)
    assertEquals(403, fileAssetResp!!.statusCode)

    assertFalse(client.shouldOverrideUrlLoading(null, fakeRequest(VoraletWebViewConfig.ENTRY_URL)))
    assertTrue(client.shouldOverrideUrlLoading(null, fakeRequest("https://example.com")))
    assertTrue(client.shouldOverrideUrlLoading(null, fakeRequest("file:///android_asset/index.html")))
  }
}
