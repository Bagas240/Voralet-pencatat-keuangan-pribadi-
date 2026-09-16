package com.example

import android.app.Application
import android.os.Build
import android.util.Log
import android.webkit.WebView

class VoraletApp : Application() {
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

