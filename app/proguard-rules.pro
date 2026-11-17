# Add project specific ProGuard rules here.
# Strong Anti-Decompilation, Bytecode Shrinking & Reverse Engineering Hardening

# Preserve JavaScript interface only for explicitly annotated @JavascriptInterface methods
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keepclassmembers class com.example.bridge.AndroidNativeBridge {
    @android.webkit.JavascriptInterface <methods>;
}

# Preserve AppWidget Providers & Notification Receiver (referenced via AndroidManifest.xml)
-keep class com.example.widget.StreakWidgetProvider { *; }
-keep class com.example.widget.PetWidgetProvider { *; }
-keep class com.example.notification.PetReminderReceiver { *; }

# Keep Offline ML Kit Text Recognition reflection/JNI classes cleanly
-dontwarn com.google.mlkit.**
-dontwarn com.google.android.gms.**
-keepclassmembers class com.google.mlkit.vision.text.** { *; }

# Aggressive Obfuscation & Bytecode Flattening (R8 Full Mode)
# Flattens all packages into unreadable single-letter classes & drops debug source maps
-repackageclasses ''
-flattenpackagehierarchy ''
-allowaccessmodification
-overloadaggressively
-renamesourcefileattribute ""
-dontkeepattributes SourceFile,LineNumberTable,LocalVariableTable,LocalVariableTypeTable

# Strip Kotlin reflection/metadata & compiler intrinsics checks in release builds
-assumenosideeffects class kotlin.jvm.internal.Intrinsics {
    public static void checkNotNull(...);
    public static void checkNotNullParameter(...);
    public static void checkExpressionValueIsNotNull(...);
    public static void checkReturnedValueIsNotNull(...);
    public static void checkFieldIsNotNull(...);
    public static void checkParameterIsNotNull(...);
}

# Strip all logging & stack-trace calls in release builds to prevent data/flow leaks
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int v(...);
    public static int d(...);
    public static int i(...);
    public static int w(...);
    public static int e(...);
    public static int wtf(...);
}
-assumenosideeffects class java.lang.Throwable {
    public void printStackTrace();
}
