package com.pehredar.app

enum class ContactStatus {
    KNOWN,
    UNKNOWN,
    UNAVAILABLE,
}

/** Pure, fail-open policy kept separate from Android services for testing. */
object ScreeningPolicy {
    fun shouldSilence(silenceUnknownEnabled: Boolean, contactStatus: ContactStatus): Boolean =
        silenceUnknownEnabled && contactStatus == ContactStatus.UNKNOWN
}

/**
 * Converts fallible platform input into a safe policy value. Any missing input
 * or lookup failure is UNAVAILABLE, which makes [ScreeningPolicy] fail open.
 */
object ContactClassifier {
    fun classify(
        number: String?,
        hasContactsPermission: Boolean,
        lookup: (String) -> Boolean,
    ): ContactStatus {
        if (number.isNullOrBlank() || !hasContactsPermission) return ContactStatus.UNAVAILABLE

        return try {
            if (lookup(number)) ContactStatus.KNOWN else ContactStatus.UNKNOWN
        } catch (_: RuntimeException) {
            ContactStatus.UNAVAILABLE
        }
    }
}
