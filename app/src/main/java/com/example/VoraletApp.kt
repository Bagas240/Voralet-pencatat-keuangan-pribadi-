package com.example

import android.app.Application
import android.os.Build

class VoraletApp : Application() {

  companion object {
    init {
      try {
        android.system.Os.setenv("EGL_LOG_LEVEL", "fatal", true)
        android.system.Os.setenv("MESA_DEBUG", "silent", true)
        android.system.Os.setenv("MESA_LOG_LEVEL", "silent", true)
        android.system.Os.setenv("LIBGL_DEBUG", "quiet", true)
        android.system.Os.setenv("LIBGL_ALWAYS_SOFTWARE", "1", true)
        android.system.Os.setenv("GALLIUM_DRIVER", "llvmpipe", true)
        android.system.Os.setenv("MESA_LOADER_DRIVER_OVERRIDE", "swrast", true)
      } catch (_: Throwable) {
        // Safe fallback in restricted environments
      }
    }
  }

  override fun onCreate() {
    super.onCreate()
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
