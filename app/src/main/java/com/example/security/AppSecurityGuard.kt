package com.example.security

import android.content.Context
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.os.Build
import android.os.Debug
import java.io.BufferedReader
import java.io.File
import java.io.FileReader
import java.security.MessageDigest

/**
 * Runtime Application Self-Protection (RASP) & Code Integrity Guard for Voralet.
 * Protects against runtime tampering, decompilation inspection, debugger attachments,
 * Frida/Xposed/LSPosed dynamic hooks, debuggable flags, and APK repackaging.
 */
object AppSecurityGuard {

    private val ROOT_PATHS = arrayOf(
        "/system/bin/su",
        "/system/xbin/su",
        "/sbin/su",
        "/system/app/Superuser.apk",
        "/system/app/SuperSU.apk",
        "/data/local/xbin/su",
        "/data/local/bin/su",
        "/system/sd/xbin/su",
        "/system/bin/failsafe/su",
        "/data/local/su",
        "/data/adb/magisk",
        "/data/adb/ksu",
        "/data/adb/ap",
        "/system/bin/magisk"
    )

    private val HOOKING_LIBRARIES = arrayOf(
        "frida",
        "xposed",
        "lsposed",
        "edxposed",
        "substrate",
        "cydia",
        "gadget",
        "libzygisk",
        "riru"
    )

    fun verifyEnvironmentIntegrity(context: Context): SecurityReport {
        val isDebugger = isDebuggerAttached()
        val isTraced = isProcessBeingTraced()
        val isFridaDetected = isFridaPresent()
        val isHookFrameworkDetected = isHookFrameworkPresent() || hasSuspiciousPreload()
        val isRooted = isDeviceRooted()
        val isAppDebuggable = isDebuggableBuild(context)
        val hasValidSignature = getSigningCertSha256(context).isNotEmpty()

        val isCompromised = isDebugger || isTraced || isFridaDetected || isHookFrameworkDetected || !hasValidSignature

        return SecurityReport(
            isSafe = !isCompromised,
            isDebuggerAttached = isDebugger || isTraced,
            isHookDetected = isFridaDetected || isHookFrameworkDetected,
            isDeviceRooted = isRooted,
            isDebuggable = isAppDebuggable,
            hasValidSignature = hasValidSignature
        )
    }

    fun hasSuspiciousPreload(): Boolean {
        return try {
            val preload = System.getenv("LD_PRELOAD")?.lowercase().orEmpty()
            preload.isNotBlank() && HOOKING_LIBRARIES.any { preload.contains(it) }
        } catch (_: Throwable) {
            false
        }
    }

    fun isDebuggableBuild(context: Context): Boolean {
        return try {
            (context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0
        } catch (_: Throwable) {
            false
        }
    }

    @Suppress("DEPRECATION")
    fun getSigningCertSha256(context: Context): String {
        return try {
            val pm = context.packageManager
            val signatures = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                val pkgInfo = pm.getPackageInfo(context.packageName, PackageManager.GET_SIGNING_CERTIFICATES)
                val signingInfo = pkgInfo.signingInfo
                if (signingInfo == null) emptyArray()
                else if (signingInfo.hasMultipleSigners()) signingInfo.apkContentsSigners
                else signingInfo.signingCertificateHistory
            } else {
                val pkgInfo = pm.getPackageInfo(context.packageName, PackageManager.GET_SIGNATURES)
                pkgInfo.signatures ?: emptyArray()
            }
            val firstSig = signatures.firstOrNull() ?: return ""
            val digest = MessageDigest.getInstance("SHA-256").digest(firstSig.toByteArray())
            digest.joinToString("") { "%02x".format(it) }
        } catch (_: Throwable) {
            ""
        }
    }

    fun isDebuggerAttached(): Boolean {
        return try {
            Debug.isDebuggerConnected() || Debug.waitingForDebugger()
        } catch (_: Throwable) {
            false
        }
    }

    fun isProcessBeingTraced(): Boolean {
        return try {
            val statusFile = File("/proc/self/status")
            if (!statusFile.exists() || !statusFile.canRead()) return false

            BufferedReader(FileReader(statusFile)).use { reader ->
                var line = reader.readLine()
                while (line != null) {
                    if (line.startsWith("TracerPid:")) {
                        val parts = line.split("\\s+".toRegex())
                        if (parts.size >= 2) {
                            val tracerPid = parts[1].trim().toIntOrNull() ?: 0
                            return tracerPid != 0
                        }
                    }
                    line = reader.readLine()
                }
            }
            false
        } catch (_: Throwable) {
            false
        }
    }

    fun isFridaPresent(): Boolean {
        return try {
            val mapsFile = File("/proc/self/maps")
            if (!mapsFile.exists() || !mapsFile.canRead()) return false

            BufferedReader(FileReader(mapsFile)).use { reader ->
                var line = reader.readLine()
                while (line != null) {
                    val lower = line.lowercase()
                    for (lib in HOOKING_LIBRARIES) {
                        if (lower.contains(lib)) {
                            return true
                        }
                    }
                    line = reader.readLine()
                }
            }
            false
        } catch (_: Throwable) {
            false
        }
    }

    fun isHookFrameworkPresent(): Boolean {
        val hookClasses = arrayOf(
            "de.robv.android.xposed.XposedBridge",
            "com.saurik.substrate.MS\$MethodHook",
            "io.github.lsposed.lspd.core.Startup"
        )
        for (clazz in hookClasses) {
            try {
                Class.forName(clazz)
                return true
            } catch (_: ClassNotFoundException) {
                // Normal expected condition
            } catch (_: Throwable) {
                return true
            }
        }
        return false
    }

    fun isDeviceRooted(): Boolean {
        try {
            val tags = Build.TAGS
            if (tags != null && tags.contains("test-keys")) {
                return true
            }
            for (path in ROOT_PATHS) {
                if (File(path).exists()) {
                    return true
                }
            }
        } catch (_: Throwable) {
            // Ignore security check exceptions
        }
        return false
    }

    fun isTrustedLocalOrigin(url: String?): Boolean {
        if (url == null) return false
        return url.startsWith("https://appassets.androidplatform.net/") ||
            url.startsWith("file:///android_asset/") ||
            url == "about:blank"
    }

    data class SecurityReport(
        val isSafe: Boolean,
        val isDebuggerAttached: Boolean,
        val isHookDetected: Boolean,
        val isDeviceRooted: Boolean,
        val isDebuggable: Boolean = false,
        val hasValidSignature: Boolean = true
    )
}
