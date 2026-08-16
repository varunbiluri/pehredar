package com.pehredar.app

import android.content.pm.PackageManager
import android.net.Uri
import android.provider.ContactsContract
import android.telecom.Call
import android.telecom.CallScreeningService
import android.telecom.CallScreeningService.CallResponse
import android.util.Log
import androidx.core.content.ContextCompat

/**
 * Wired to Android's Telecom framework via the CALL_SCREENING role
 * (requested in MainActivity). Every incoming call is routed through
 * [onScreenCall] before it rings.
 *
 * Policy: calls from saved contacts always ring normally. Calls from
 * numbers not in contacts ring silently (not blocked -- still reaches
 * voicemail/call log) if the user has enabled that in Settings. Fails
 * open: if contacts can't be checked (permission missing, or the setting
 * is off), every call rings normally, unchanged.
 *
 * This is deliberately the full scope of on-device screening here. Live
 * AI conversation during calls -- the original goal -- is not
 * implemented: see README "Why no live AI conversation" for why that
 * turned out not to be legitimately buildable as a third-party app on
 * either Android or iOS without routing calls through a server.
 */
class PehredarCallScreeningService : CallScreeningService() {

    override fun onScreenCall(callDetails: Call.Details) {
        val number = callDetails.handle?.schemeSpecificPart

        val silenceUnknown = Settings.isSilenceUnknownNumbersEnabled(this)
        val shouldSilence = silenceUnknown && number != null && !isKnownContact(number)

        Log.d(TAG, "Incoming call from ${number ?: "unknown"} -- silence=$shouldSilence (setting=$silenceUnknown)")

        val response = CallResponse.Builder()
            .setDisallowCall(false)
            .setRejectCall(false)
            .setSilenceCall(shouldSilence)
            .setSkipCallLog(false)
            .setSkipNotification(false)
            .build()
        respondToCall(callDetails, response)
    }

    private fun isKnownContact(number: String): Boolean {
        val hasPermission = ContextCompat.checkSelfPermission(this, android.Manifest.permission.READ_CONTACTS) ==
            PackageManager.PERMISSION_GRANTED
        if (!hasPermission) {
            // Can't verify -- fail open rather than silence someone who's
            // actually a saved contact.
            return true
        }
        val uri = Uri.withAppendedPath(ContactsContract.PhoneLookup.CONTENT_FILTER_URI, Uri.encode(number))
        return contentResolver.query(uri, arrayOf(ContactsContract.PhoneLookup._ID), null, null, null)?.use { cursor ->
            cursor.moveToFirst()
        } ?: true
    }

    private companion object {
        const val TAG = "PehredarScreening"
    }
}
