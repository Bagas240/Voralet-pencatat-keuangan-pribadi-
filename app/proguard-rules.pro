# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# Preserve JavaScript interface for WebView
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keepclassmembers class com.example.bridge.AndroidNativeBridge {
    public *;
}

# Preserve AppWidget Providers
-keep class com.example.widget.StreakWidgetProvider { *; }
-keep class com.example.widget.PetWidgetProvider { *; }

# Obfuscate class and method names in release builds
-repackageclasses ''
-allowaccessmodification
-renamesourcefileattribute ""

# Strip verbose debug logs in production
-assumenosideeffects class android.util.Log {
    public static *** v(...);
    public static *** d(...);
    public static *** i(...);
}


