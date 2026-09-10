package com.example

import android.app.Application
import android.content.Context
import android.util.Log

class VoraletApp : Application() {
  init {
    configureMesa()
  }

  override fun attachBaseContext(base: Context?) {
    configureMesa()
    super.attachBaseContext(base)
  }

  override fun onCreate() {
    super.onCreate()
    configureMesa()
    MainActivity.prepareWebViewStorage(this)
  }

  private fun configureMesa() {
    try {
      android.system.Os.setenv("MESA_DEBUG", "0", true)
      android.system.Os.setenv("MESA_NO_ERROR", "1", true)
      android.system.Os.setenv("LIBGL_ALWAYS_SOFTWARE", "1", true)
      android.system.Os.setenv("GALLIUM_DRIVER", "llvmpipe", true)
      android.system.Os.setenv("MESA_LOADER_DRIVER_OVERRIDE", "swrast", true)
      android.system.Os.setenv("EGL_LOG_LEVEL", "fatal", true)
    } catch (_: Throwable) {
    }
  }
}
