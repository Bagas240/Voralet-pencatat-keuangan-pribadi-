package com.example

import android.app.Application

class VoraletApp : Application() {
  override fun onCreate() {
    super.onCreate()
    MainActivity.prepareWebViewStorage(this)
  }
}
