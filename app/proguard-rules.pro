# Add project specific ProGuard rules here.
# Strong Anti-Decompilation & Reverse Engineering Hardening

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

# Aggressive Obfuscation & Bytecode Flattening
# Flattens all packages into root, renaming to unreadable single-letter symbols
-repackageclasses ''
-flattenpackagehierarchy ''
-allowaccessmodification
-overloadaggressively
-renamesourcefileattribute ""
-dontkeepattributes SourceFile,LineNumberTable

# Strip all debugging symbols and logging calls in production
-assumenosideeffects class android.util.Log {
    public static *** v(...);
    public static *** d(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
    public static *** wtf(...);
}

# Protect Security Verification classes from inlining while allowing obfuscation
-keepclassmembers class com.example.security.AppSecurityGuard {
    public static *** *(...);
}
