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
6. Add `RELEASE_NOTES_v<version>.md`, then tag the exact commit with a signed or
   annotated semantic-version tag. The tag must match Android's `versionName`.
7. Push the tag. The signed-release workflow builds the APK and AAB, verifies
   the APK signature, publishes SHA-256 checksums, and creates GitHub build
   provenance attestations before publishing the GitHub release.
8. Confirm the uploaded asset digests, provenance, tag target, CI status, and
   release notes.

The Android signing key and credentials must never be committed. Future updates
must use the same protected key. Key access is limited to release maintainers.
GitHub Actions stores the key and its credentials as encrypted repository
secrets; never print those values or expose them to pull-request workflows.
