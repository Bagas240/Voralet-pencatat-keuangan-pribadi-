package com.example

import com.example.update.GitHubAutoUpdater
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class GitHubAutoUpdaterTest {

  @Test
  fun `normalizeVersion strips v prefix and pre-release suffixes`() {
    assertEquals("3.5.0", GitHubAutoUpdater.normalizeVersion("v3.5.0"))
    assertEquals("3.5.1", GitHubAutoUpdater.normalizeVersion(" V3.5.1-beta.1 "))
    assertEquals("4.0.0", GitHubAutoUpdater.normalizeVersion("v4.0.0+build16"))
    assertEquals("", GitHubAutoUpdater.normalizeVersion(null))
  }

  @Test
  fun `isNewerVersion compares semantic versions accurately`() {
    assertTrue(GitHubAutoUpdater.isNewerVersion("v3.5.1", "3.5.0"))
    assertTrue(GitHubAutoUpdater.isNewerVersion("3.6.0", "3.5.9"))
    assertTrue(GitHubAutoUpdater.isNewerVersion("4.0.0", "3.5.0"))

    assertFalse(GitHubAutoUpdater.isNewerVersion("v3.5.0", "3.5.0"))
    assertFalse(GitHubAutoUpdater.isNewerVersion("3.4.9", "3.5.0"))
    assertFalse(GitHubAutoUpdater.isNewerVersion("", "3.5.0"))
  }

  @Test
  fun `isTrustedGitHubUrl allows only HTTPS GitHub release hosts`() {
    assertTrue(GitHubAutoUpdater.isTrustedGitHubUrl("https://api.github.com/repos/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/latest"))
    assertTrue(GitHubAutoUpdater.isTrustedGitHubUrl("https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/download/v3.5.1/voralet.apk"))
    assertTrue(GitHubAutoUpdater.isTrustedGitHubUrl("https://objects.githubusercontent.com/some/asset.apk"))
    assertTrue(GitHubAutoUpdater.isTrustedGitHubUrl("https://release-assets.githubusercontent.com/some/asset.apk"))

    assertFalse(GitHubAutoUpdater.isTrustedGitHubUrl("http://github.com/Bagas240/Voralet/releases"))
    assertFalse(GitHubAutoUpdater.isTrustedGitHubUrl("https://evil.example.com/voralet.apk"))
    assertFalse(GitHubAutoUpdater.isTrustedGitHubUrl("javascript:alert(1)"))
    assertFalse(GitHubAutoUpdater.isTrustedGitHubUrl(null))
  }

  @Test
  fun `parseReleaseJson selects apk asset download url when available`() {
    val payload = """
      {
        "tag_name": "v3.6.0",
        "html_url": "https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/tag/v3.6.0",
        "body": "Perbaikan keamanan dan performa v3.6.0",
        "assets": [
          {
            "name": "checksums.txt",
            "browser_download_url": "https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/download/v3.6.0/checksums.txt"
          },
          {
            "name": "Voralet-v3.6.0.apk",
            "browser_download_url": "https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/download/v3.6.0/Voralet-v3.6.0.apk"
          }
        ]
      }
    """.trimIndent()

    val result = GitHubAutoUpdater.parseReleaseJson(payload, currentVersion = "3.5.0")
    assertTrue(result.ok)
    assertTrue(result.hasUpdate)
    assertEquals("3.6.0", result.latestVersion)
    assertEquals(
      "https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/download/v3.6.0/Voralet-v3.6.0.apk",
      result.downloadUrl
    )
    assertEquals("Perbaikan keamanan dan performa v3.6.0", result.releaseNotes)
  }

  @Test
  fun `parseReleaseJson rejects untrusted asset host and falls back to safe release page`() {
    val payload = """
      {
        "tag_name": "v3.5.1",
        "html_url": "https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/tag/v3.5.1",
        "assets": [
          {
            "name": "Voralet.apk",
            "browser_download_url": "https://untrusted-mirror.example.org/Voralet.apk"
          }
        ]
      }
    """.trimIndent()

    val result = GitHubAutoUpdater.parseReleaseJson(payload, currentVersion = "3.5.0")
    assertTrue(result.ok)
    assertTrue(result.hasUpdate)
    assertEquals(
      "https://github.com/Bagas240/Voralet-pencatat-keuangan-pribadi-/releases/tag/v3.5.1",
      result.downloadUrl
    )
  }
}
