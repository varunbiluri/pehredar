package com.pehredar.app

import org.junit.Assert.assertFalse
import org.junit.Assert.assertEquals
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

    @Test
    fun `all policy combinations have an explicit safe result`() {
        ContactStatus.entries.forEach { status ->
            assertFalse(ScreeningPolicy.shouldSilence(false, status))
        }
        assertFalse(ScreeningPolicy.shouldSilence(true, ContactStatus.KNOWN))
        assertFalse(ScreeningPolicy.shouldSilence(true, ContactStatus.UNAVAILABLE))
        assertTrue(ScreeningPolicy.shouldSilence(true, ContactStatus.UNKNOWN))
    }

    @Test
    fun `classifier recognizes a saved contact`() {
        assertEquals(ContactStatus.KNOWN, ContactClassifier.classify("+910000000000", true) { true })
    }

    @Test
    fun `classifier recognizes an unsaved number`() {
        assertEquals(ContactStatus.UNKNOWN, ContactClassifier.classify("+910000000000", true) { false })
    }

    @Test
    fun `classifier does not query without permission`() {
        var queried = false
        val result = ContactClassifier.classify("+910000000000", false) {
            queried = true
            false
        }
        assertEquals(ContactStatus.UNAVAILABLE, result)
        assertFalse(queried)
    }

    @Test
    fun `classifier fails open for blank and withheld numbers`() {
        assertEquals(ContactStatus.UNAVAILABLE, ContactClassifier.classify(null, true) { false })
        assertEquals(ContactStatus.UNAVAILABLE, ContactClassifier.classify("   ", true) { false })
    }

    @Test
    fun `classifier fails open when contacts provider throws`() {
        val result = ContactClassifier.classify("+910000000000", true) {
            throw SecurityException("permission changed during lookup")
        }
        assertEquals(ContactStatus.UNAVAILABLE, result)
        assertFalse(ScreeningPolicy.shouldSilence(true, result))
    }
}
