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
      android.system.Os.setenv("MESA_LOG_FILE", "/dev/null", true)
      android.system.Os.setenv("vendor.mesa.log", "silent", true)
      android.system.Os.setenv("vendor.mesa.log.file", "/dev/null", true)
    } catch (_: Throwable) {
      // Safe fallback
    }

    try {
      System.setProperty("log.tag.MESA", "SUPPRESS")
      val spClass = Class.forName("android.os.SystemProperties")
      val setMethod = spClass.getMethod("set", String::class.java, String::class.java)
      setMethod.invoke(null, "log.tag.MESA", "SUPPRESS")
      setMethod.invoke(null, "log.tag.MESA", "SILENT")
      setMethod.invoke(null, "vendor.mesa.log", "silent")
      setMethod.invoke(null, "vendor.mesa.log.file", "/dev/null")
    } catch (_: Throwable) {
      // Safe fallback
    }

    try {
      val cmdLineFile = java.io.File("/data/local/tmp/webview-command-line")
      cmdLineFile.writeText("_ --disable-gpu --disable-gpu-rasterization --disable-gpu-compositing")
      cmdLineFile.setReadable(true, false)
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
