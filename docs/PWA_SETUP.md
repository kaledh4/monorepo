# PWA & APK Setup Guide

To remove the "Chrome Bar" (browser UI) from your Android APK, you must verify ownership of your domain. This is done using the `.well-known/assetlinks.json` file.

## Steps to Fix the "Chrome Bar" Issue

1.  **Get your Signing Key Fingerprint (SHA-256):**
    *   If you are using **PWABuilder**:
        *   Go to the "Android" generation page.
        *   Look for "Signing Key" or "Asset Links" section.
        *   Copy the **SHA-256 Fingerprint**.
    *   If you are using **Android Studio**:
        *   Run the `signingReport` Gradle task.
        *   Copy the **SHA-256** fingerprint for your release key.

2.  **Get your Package Name:**
    *   This is the `applicationId` you chose (e.g., `com.dailyalphaloop.commander`).

3.  **Update `docs/.well-known/assetlinks.json`:**
    *   Open `docs/.well-known/assetlinks.json`.
    *   Replace `REPLACE_WITH_YOUR_PACKAGE_NAME` with your actual package name.
    *   Replace `REPLACE_WITH_YOUR_SHA256_FINGERPRINT` with your actual SHA-256 fingerprint.

4.  **Deploy:**
    *   Push these changes to GitHub.
    *   Wait for GitHub Pages to update.
    *   Verify the file is accessible at `https://kaledh4.github.io/daily-alpha-loop/.well-known/assetlinks.json`.

5.  **Re-build or Re-install:**
    *   Once the file is live and correct, the Android app (TWA) will verify it on launch and hide the browser bar.

## Other Improvements Applied

*   **Manifest Update:** Added `display_override` to `manifest.json` to prioritize standalone mode.
*   **Theme Color:** Added `<meta name="theme-color">` to `index.html` to match the app theme (`#0f172a`), which blends the status bar with the app.
