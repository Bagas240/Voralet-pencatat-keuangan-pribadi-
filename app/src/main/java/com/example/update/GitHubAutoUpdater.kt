package com.example.update

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import com.example.BuildConfig
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * Native GitHub Releases Auto-Update Checker for Voralet.
 * Connects strictly over HTTPS to GitHub API/Release hosts without modifying WebView offline isolation
 * and without requiring REQUEST_INSTALL_PACKAGES or any runtime permission.
 */
object GitHubAutoUpdater {

    private const val REPO_OWNER = "Bagas240"
    private const val REPO_NAME = "Voralet-pencatat-keuangan-pribadi-"
    private const val LATEST_RELEASE_API =
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"
    private const val RELEASES_PAGE_FALLBACK =
        "https://github.com/$REPO_OWNER/$REPO_NAME/releases/latest"

    private const val PREFS_NAME = "voralet_update_prefs"
    private const val KEY_LAST_CHECK_TS = "last_check_ts"
    private const val AUTO_CHECK_INTERVAL_MS = 6L * 60L * 60L * 1000L

    private val ALLOWED_GITHUB_HOSTS = setOf(
        "api.github.com",
        "github.com",
        "objects.githubusercontent.com",
        "release-assets.githubusercontent.com"
    )

    data class UpdateCheckResult(
        val ok: Boolean,
        val hasUpdate: Boolean,
        val currentVersion: String,
        val latestVersion: String,
        val downloadUrl: String,
        val releasePageUrl: String,
        val releaseNotes: String,
        val errorMessage: String = ""
    ) {
        fun toJsonString(): String = JSONObject().apply {
            put("ok", ok)
            put("hasUpdate", hasUpdate)
            put("currentVersion", currentVersion)
            put("latestVersion", latestVersion)
            put("downloadUrl", downloadUrl)
            put("releasePageUrl", releasePageUrl)
            put("releaseNotes", releaseNotes)
            put("errorMessage", errorMessage)
        }.toString()
    }

    internal fun normalizeVersion(rawVersion: String?): String {
        return (rawVersion ?: "")
            .trim()
            .removePrefix("v")
            .removePrefix("V")
            .substringBefore("-")
            .substringBefore("+")
            .trim()
    }

    internal fun isNewerVersion(remoteVersion: String?, currentVersion: String?): Boolean {
        val remoteClean = normalizeVersion(remoteVersion)
        val currentClean = normalizeVersion(currentVersion)
        if (remoteClean.isEmpty() || currentClean.isEmpty()) return false

        val remoteParts = remoteClean.split(".").map { it.toIntOrNull() ?: 0 }
        val currentParts = currentClean.split(".").map { it.toIntOrNull() ?: 0 }
        val maxLen = maxOf(remoteParts.size, currentParts.size)

        for (i in 0 until maxLen) {
            val r = remoteParts.getOrElse(i) { 0 }
            val c = currentParts.getOrElse(i) { 0 }
            if (r > c) return true
            if (r < c) return false
        }
        return false
    }

    internal fun isTrustedGitHubUrl(rawUrl: String?): Boolean {
        if (rawUrl.isNullOrBlank()) return false
        return try {
            val uri = Uri.parse(rawUrl.trim())
            val scheme = uri.scheme?.lowercase()
            val host = uri.host?.lowercase()
            scheme == "https" && host != null && ALLOWED_GITHUB_HOSTS.contains(host)
        } catch (_: Throwable) {
            false
        }
    }

    fun shouldRunAutoCheck(context: Context): Boolean {
        val lastCheck = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getLong(KEY_LAST_CHECK_TS, 0L)
        return (System.currentTimeMillis() - lastCheck) >= AUTO_CHECK_INTERVAL_MS
    }

    fun markCheckedNow(context: Context) {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putLong(KEY_LAST_CHECK_TS, System.currentTimeMillis())
            .apply()
    }

    fun checkLatestRelease(
        currentVersion: String = BuildConfig.VERSION_NAME
    ): UpdateCheckResult {
        var conn: HttpURLConnection? = null
        return try {
            val url = URL(LATEST_RELEASE_API)
            conn = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 7000
                readTimeout = 7000
                instanceFollowRedirects = false
                setRequestProperty("Accept", "application/vnd.github+json")
                setRequestProperty("User-Agent", "Voralet-Android/$currentVersion")
            }

            val code = conn.responseCode
            if (code !in 200..299) {
                return UpdateCheckResult(
                    ok = false,
                    hasUpdate = false,
                    currentVersion = currentVersion,
                    latestVersion = currentVersion,
                    downloadUrl = "",
                    releasePageUrl = RELEASES_PAGE_FALLBACK,
                    releaseNotes = "",
                    errorMessage = "HTTP $code"
                )
            }

            val body = BufferedReader(InputStreamReader(conn.inputStream, Charsets.UTF_8)).use {
                it.readText()
            }
            parseReleaseJson(body, currentVersion)
        } catch (t: Throwable) {
            UpdateCheckResult(
                ok = false,
                hasUpdate = false,
                currentVersion = currentVersion,
                latestVersion = currentVersion,
                downloadUrl = "",
                releasePageUrl = RELEASES_PAGE_FALLBACK,
                releaseNotes = "",
                errorMessage = t.message ?: "Offline"
            )
        } finally {
            try {
                conn?.disconnect()
            } catch (_: Throwable) {}
        }
    }

    internal fun parseReleaseJson(
        rawJson: String,
        currentVersion: String = BuildConfig.VERSION_NAME
    ): UpdateCheckResult {
        val json = JSONObject(rawJson)
        val tagName = json.optString("tag_name", "")
        val latestVersion = normalizeVersion(tagName).ifBlank { currentVersion }
        val htmlUrl = json.optString("html_url", RELEASES_PAGE_FALLBACK)
        val safeReleaseUrl = if (isTrustedGitHubUrl(htmlUrl)) htmlUrl else RELEASES_PAGE_FALLBACK
        val notes = json.optString("body", "").take(800)

        var apkDownloadUrl = ""
        val assets = json.optJSONArray("assets")
        if (assets != null) {
            for (i in 0 until assets.length()) {
                val asset = assets.optJSONObject(i) ?: continue
                val assetName = asset.optString("name", "")
                val download = asset.optString("browser_download_url", "")
                if (assetName.endsWith(".apk", ignoreCase = true) && isTrustedGitHubUrl(download)) {
                    apkDownloadUrl = download
                    break
                }
            }
        }

        val resolvedDownload = apkDownloadUrl.ifBlank { safeReleaseUrl }
        val hasUpdate = isNewerVersion(latestVersion, currentVersion)

        return UpdateCheckResult(
            ok = true,
            hasUpdate = hasUpdate,
            currentVersion = currentVersion,
            latestVersion = latestVersion,
            downloadUrl = resolvedDownload,
            releasePageUrl = safeReleaseUrl,
            releaseNotes = notes
        )
    }

    fun openTrustedUpdateUrl(activity: Activity, rawUrl: String?): Boolean {
        val target = if (isTrustedGitHubUrl(rawUrl)) rawUrl!! else RELEASES_PAGE_FALLBACK
        return try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(target)).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            activity.startActivity(intent)
            true
        } catch (_: Throwable) {
            false
        }
    }
}
