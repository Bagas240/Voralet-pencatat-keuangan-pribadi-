package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.security.AssetVaultDecryptor
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class AssetVaultDecryptorTest {

  @Test
  fun `decrypts voralet_core bin into valid offline html bundle`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val decryptedBytes = AssetVaultDecryptor.loadDecryptedHtml(context)
    val html = decryptedBytes.toString(Charsets.UTF_8)

    assertTrue("Expected non-empty decrypted HTML", html.length > 10_000)
    assertTrue("Expected HTML doctype", html.contains("<!DOCTYPE html>", ignoreCase = true))
    assertTrue("Expected React root mount", html.contains("""<div id="root"></div>"""))
    assertTrue("Expected offline CSP", html.contains("Content-Security-Policy"))
  }

  @Test
  fun `rejects tampered vault ciphertext`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val blob = context.assets.open("voralet_core.bin").use { it.readBytes() }
    val tampered = blob.copyOf()
    tampered[tampered.lastIndex] = (tampered[tampered.lastIndex].toInt() xor 0xFF).toByte()

    assertThrows(IllegalArgumentException::class.java) {
      AssetVaultDecryptor.decryptBlob(tampered)
    }
  }
}
