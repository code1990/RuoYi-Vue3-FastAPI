# APK Template Guide

## What changed

1. `manifest.json` is now trimmed for `APP-PLUS` Android packaging.
2. Payment/ad sdk config and absolute local splash paths were removed.
3. `common/config.js` now separates `apiBaseUrl.h5` and `apiBaseUrl.app`.
4. `App.vue` no longer sets a hard-coded tab bar badge on launch.
5. `pages/sys/user/clear-cache.vue` now performs real cache cleanup.

## Before packaging

1. Replace the app name, `appid`, version, and icon resources in `manifest.json`.
2. Replace `buildProfile.androidPackageName` in `common/config.js` with your real package name.
3. Replace `apiBaseUrl.app` with your production or staging app API address.
4. If your project needs payment, location, recording, or contacts, add only the required modules and permissions back.

## Recommended verification

1. Login flow
2. API requests on a real Android device
3. `web-view` page loading
4. File upload and image selection
5. Cache cleanup page behavior
