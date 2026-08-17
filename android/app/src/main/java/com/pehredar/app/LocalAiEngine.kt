package com.pehredar.app

import java.util.Locale

enum class CallerIntent { SCAM_RISK, DELIVERY, APPOINTMENT, BUSINESS, PERSONAL, UNKNOWN }
enum class RiskLevel { HIGH, MEDIUM, LOW }

data class LocalAiResult(val intent: CallerIntent, val risk: RiskLevel)

/**
 * Tiny, deterministic on-device language/risk model. It deliberately makes no
 * network calls and stores no input. STT and TTS are provided by Android's
 * explicitly on-device engines; this classifier supplies the screening policy.
 */
object LocalAiEngine {
    private val highRiskSignals = setOf(
        "otp", "pin", "cvv", "password", "kyc", "blocked", "verify immediately",
        "remote access", "screen share", "ओटीपी", "पासवर्ड", "केवाईसी", "खाता बंद",
    )
    private val pressureSignals = setOf(
        "urgent", "immediately", "today only", "act now", "police", "customs",
        "refund", "prize", "lottery", "तुरंत", "अभी", "इनाम", "लॉटरी",
    )
    private val deliverySignals = setOf(
        "delivery", "courier", "parcel", "package", "blue dart", "delhivery",
        "पार्सल", "कूरियर", "डिलीवरी",
    )
    private val appointmentSignals = setOf(
        "appointment", "clinic", "doctor", "hospital", "dentist", "meeting",
        "अपॉइंटमेंट", "क्लिनिक", "डॉक्टर", "अस्पताल",
    )
    private val businessSignals = setOf(
        "bank", "loan", "insurance", "policy", "interview", "company", "offer",
        "बैंक", "लोन", "बीमा", "पॉलिसी", "इंटरव्यू", "कंपनी",
    )
    private val personalSignals = setOf(
        "friend", "family", "school", "teacher", "dinner", "wedding",
        "दोस्त", "परिवार", "स्कूल", "टीचर", "शादी",
    )

    fun analyze(input: String): LocalAiResult {
        val text = input.lowercase(Locale.ROOT).trim()
        if (text.isEmpty()) return LocalAiResult(CallerIntent.UNKNOWN, RiskLevel.LOW)

        val highHits = highRiskSignals.count(text::contains)
        val pressureHits = pressureSignals.count(text::contains)
        if (highHits > 0) return LocalAiResult(CallerIntent.SCAM_RISK, RiskLevel.HIGH)

        val intent = listOf(
            CallerIntent.DELIVERY to deliverySignals.count(text::contains),
            CallerIntent.APPOINTMENT to appointmentSignals.count(text::contains),
            CallerIntent.BUSINESS to businessSignals.count(text::contains),
            CallerIntent.PERSONAL to personalSignals.count(text::contains),
        ).maxByOrNull { it.second }?.takeIf { it.second > 0 }?.first ?: CallerIntent.UNKNOWN

        val risk = if (pressureHits > 0) RiskLevel.MEDIUM else RiskLevel.LOW
        return LocalAiResult(intent, risk)
    }
}
