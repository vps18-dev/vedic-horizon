# ProGuard rules for Vedic Horizon Android App
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keepattributes JavascriptInterface
-keepclassmembers class com.vedichorizon.app.VedicAppBridge {
    public *;
}
