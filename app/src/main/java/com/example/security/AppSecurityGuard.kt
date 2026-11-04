package com.example.security

import android.content.Context
import android.content.pm.ApplicationInfo
import android.os.Build
import android.os.Debug
import android.os.Process
import android.util.Log
import java.io.BufferedReader
import java.io.File
import java.io.FileReader
import java.net.InetAddress
import java.net.Socket

/**
 * Runtime Application Self-Protection (RASP) & Code Integrity Guard for Voralet.
 * Protects against runtime tampering, decompilation inspection, debugger attachments,
 * Frida/Xposed dynamic hooks, and unauthorized memory dumps.
 */
object AppSecurityGuard {

    private const val TAG = "AppSecurityGuard"

    // Common root binary locations
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
        "/data/local/su"
    )

    // Suspicious injection/hooking libraries and strings
    private val HOOKING_LIBRARIES = arrayOf(
        "frida",
        "xposed",
        "substrate",
        "cydia",
        "gadget"
    )

    /**
     * Performs a comprehensive security and integrity scan.
     * Returns true if the environment is safe, or false if an active threat is detected.
     */
    fun verifyEnvironmentIntegrity(context: Context): SecurityReport {
        val isDebugger = isDebuggerAttached()
        val isTraced = isProcessBeingTraced()
        val isFridaDetected = isFridaPresent()
        val isHookFrameworkDetected = isHookFrameworkPresent()
        val isRooted = isDeviceRooted()

        val isCompromised = isDebugger || isTraced || isFridaDetected || isHookFrameworkDetected

        return SecurityReport(
            isSafe = !isCompromised,
            isDebuggerAttached = isDebugger || isTraced,
            isHookDetected = isFridaDetected || isHookFrameworkDetected,
            isDeviceRooted = isRooted
        )
    }

    /**
     * Checks if a Java/JDWP debugger is actively attached.
     */
    fun isDebuggerAttached(): Boolean {
        return try {
            Debug.isDebuggerConnected() || Debug.waitingForDebugger()
        } catch (_: Throwable) {
            false
        }
    }

    /**
     * Inspects /proc/self/status for TracerPid to detect native GDB/LLDB or ptrace attachments.
     */
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

    /**
     * Scans memory maps (/proc/self/maps) for Frida gadget or server artifacts.
     */
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

    /**
     * Checks for known hooking classes in the runtime class loader.
     */
    fun isHookFrameworkPresent(): Boolean {
        val hookClasses = arrayOf(
            "de.robv.android.xposed.XposedBridge",
            "com.saurik.substrate.MS\$MethodHook"
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

    /**
     * Checks for root binaries and suspicious build tags.
     */
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

    /**
     * Validates whether an incoming URL originates strictly from local secure app assets.
     */
    fun isTrustedLocalOrigin(url: String?): Boolean {
        if (url == null) return false
        return url.startsWith("file:///android_asset/") || url == "about:blank"
    }

    data class SecurityReport(
        val isSafe: Boolean,
        val isDebuggerAttached: Boolean,
        val isHookDetected: Boolean,
        val isDeviceRooted: Boolean
    )
}
