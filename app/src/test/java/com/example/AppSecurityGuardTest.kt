package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.security.AppSecurityGuard
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class AppSecurityGuardTest {

  @Test
  fun `trusted local origin allows only sandboxed asset and about blank`() {
    assertTrue(AppSecurityGuard.isTrustedLocalOrigin("https://appassets.androidplatform.net/index.html"))
    assertTrue(AppSecurityGuard.isTrustedLocalOrigin("file:///android_asset/index.html"))
    assertTrue(AppSecurityGuard.isTrustedLocalOrigin("about:blank"))

    assertFalse(AppSecurityGuard.isTrustedLocalOrigin(null))
    assertFalse(AppSecurityGuard.isTrustedLocalOrigin("https://example.com"))
    assertFalse(AppSecurityGuard.isTrustedLocalOrigin("http://localhost:8080"))
    assertFalse(AppSecurityGuard.isTrustedLocalOrigin("javascript:alert(1)"))
  }

  @Test
  fun `environment integrity check executes without throwing`() {
    val context = ApplicationProvider.getApplicationContext<Context>()
    val report = AppSecurityGuard.verifyEnvironmentIntegrity(context)
    assertFalse("Test runner should not trigger Frida hook detection", report.isHookDetected)
  }
}
