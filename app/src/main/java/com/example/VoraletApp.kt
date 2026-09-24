package com.example

import android.app.Application
import android.content.Context
import android.os.Build
import android.system.Os
import android.util.Log
import com.example.webview.VoraletWebViewConfig

class VoraletApp : Application() {

  companion object {
    private const val TAG = "VoraletApp"

    init {
      configureEnvironment()
    }

    fun configureEnvironment(context: Context? = null) {
      try {
        // If the environment lacks a DRI rendernode (virtualized container or headless Android emulator),
        // instruct Mesa to immediately utilize the software rasterizer (llvmpipe/swrast).
        // This eliminates benign probing failures ("Failed to open rendernode: No such file or directory")
        // and avoids GPU fallback delays or stutter on Android 16.
        if (!VoraletWebViewConfig.hasDriRenderNode || VoraletWebViewConfig.isEmulator) {
          Os.setenv("LIBGL_ALWAYS_SOFTWARE", "1", true)
          Os.setenv("GALLIUM_DRIVER", "llvmpipe", true)
          Os.setenv("MESA_LOADER_DRIVER_OVERRIDE", "swrast", true)
        }
        Os.setenv("MESA_LOG_FILE", "/dev/null", true)
        Os.setenv("MESA_DEBUG", "0", true)
        Os.setenv("MESA_SILENT", "1", true)
        Os.setenv("MESA_LOG_LEVEL", "none", true)
        Os.setenv("EGL_LOG_LEVEL", "none", true)
        Os.setenv("GALLIUM_LOG_LEVEL", "none", true)
        Os.setenv("MESA_NO_ERROR", "1", true)
      } catch (t: Throwable) {
        Log.d(TAG, "Mesa environment configuration notice: ${t.message}")
      }
    }
  }

  init {
    configureEnvironment()
  }

  override fun attachBaseContext(base: Context?) {
    super.attachBaseContext(base)
    configureEnvironment(base)
  }

  override fun onCreate() {
    super.onCreate()
    configureEnvironment(this)
    if (isMainProcess()) {
      MainActivity.prepareWebViewStorage(this)
    }
  }

  private fun isMainProcess(): Boolean {
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
      if (android.os.Process.isIsolated()) {
        false
      } else {
        packageName == Application.getProcessName()
      }
    } else {
      true
    }
  }
}


