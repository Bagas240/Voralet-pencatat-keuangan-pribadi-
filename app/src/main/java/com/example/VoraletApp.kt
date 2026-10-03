package com.example

import android.app.Application
import android.os.Build

class VoraletApp : Application() {

  init {
    configureGraphicsEnvironment()
  }

  override fun attachBaseContext(base: android.content.Context?) {
    configureGraphicsEnvironment()
    super.attachBaseContext(base)
  }

  override fun onCreate() {
    super.onCreate()
    configureGraphicsEnvironment()
    if (isMainProcess()) {
      MainActivity.prepareWebViewStorage(this)
    }
  }

  private fun configureGraphicsEnvironment() {
    try {
      android.system.Os.setenv("LIBGL_DRI3_DISABLE", "1", true)
      android.system.Os.setenv("EGL_LOG_LEVEL", "fatal", true)
      android.system.Os.setenv("MESA_DEBUG", "0", true)
      android.system.Os.setenv("MESA_LOG_LEVEL", "fatal", true)
      android.system.Os.setenv("LIBGL_DEBUG", "quiet", true)
    } catch (_: Throwable) {
      // Safe fallback
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
