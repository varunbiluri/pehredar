# Release process

1. Ensure `main` is clean and CI is green.
2. Update `versionCode` and semantic `versionName` in the Android build file.
3. Add release notes and run:

   ```bash
   python3 scripts/check_localizations.py
   cd android
   ./gradlew clean testDebugUnitTest lintDebug assembleRelease
   ```

4. Verify the APK signature and inspect packaged permissions.
5. Test saved, unsaved, missing-permission, and protection-disabled cases on at
   least one physical Android 10+ device. Public stable releases require the
   device matrix documented in the roadmap.
6. Tag the exact commit with a signed or annotated semantic-version tag.
7. Publish the signed APK as a GitHub prerelease or release with its SHA-256.
8. Confirm the uploaded asset digest, tag target, CI status, and release notes.

The Android signing key and credentials must never be committed. Future updates
must use the same protected key. Key access is limited to release maintainers.
