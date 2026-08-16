package com.pehredar.app

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ScreeningPolicyTest {
    @Test
    fun `unknown caller is silenced when protection is enabled`() {
        assertTrue(ScreeningPolicy.shouldSilence(true, ContactStatus.UNKNOWN))
    }

    @Test
    fun `known caller always rings`() {
        assertFalse(ScreeningPolicy.shouldSilence(true, ContactStatus.KNOWN))
    }

    @Test
    fun `unknown caller rings when protection is disabled`() {
        assertFalse(ScreeningPolicy.shouldSilence(false, ContactStatus.UNKNOWN))
    }

    @Test
    fun `missing caller information fails open`() {
        assertFalse(ScreeningPolicy.shouldSilence(true, ContactStatus.UNAVAILABLE))
    }
}
