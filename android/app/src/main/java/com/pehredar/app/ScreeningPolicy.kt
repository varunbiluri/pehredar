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
