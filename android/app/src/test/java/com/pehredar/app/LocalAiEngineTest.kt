package com.pehredar.app

import org.junit.Assert.assertEquals
import org.junit.Test

class LocalAiEngineTest {
    @Test
    fun `credential request is high risk`() {
        val result = LocalAiEngine.analyze("SBI security needs your OTP immediately")
        assertEquals(CallerIntent.SCAM_RISK, result.intent)
        assertEquals(RiskLevel.HIGH, result.risk)
    }

    @Test
    fun `Hindi credential request is high risk`() {
        val result = LocalAiEngine.analyze("अभी ओटीपी बताइए नहीं तो खाता बंद होगा")
        assertEquals(CallerIntent.SCAM_RISK, result.intent)
        assertEquals(RiskLevel.HIGH, result.risk)
    }

    @Test
    fun `delivery is classified locally`() {
        assertEquals(CallerIntent.DELIVERY, LocalAiEngine.analyze("Blue Dart parcel delivery").intent)
    }

    @Test
    fun `appointment is classified locally`() {
        assertEquals(CallerIntent.APPOINTMENT, LocalAiEngine.analyze("Apollo clinic appointment").intent)
    }

    @Test
    fun `business call is classified locally`() {
        assertEquals(CallerIntent.BUSINESS, LocalAiEngine.analyze("Calling about an interview").intent)
    }

    @Test
    fun `personal call is classified locally`() {
        assertEquals(CallerIntent.PERSONAL, LocalAiEngine.analyze("School teacher calling").intent)
    }

    @Test
    fun `pressure without credentials raises caution`() {
        val result = LocalAiEngine.analyze("This prize is available today only")
        assertEquals(RiskLevel.MEDIUM, result.risk)
    }

    @Test
    fun `empty input remains low risk and unknown`() {
        val result = LocalAiEngine.analyze("  ")
        assertEquals(CallerIntent.UNKNOWN, result.intent)
        assertEquals(RiskLevel.LOW, result.risk)
    }
}
