package com.pehredar.app

import android.telecom.Call
import android.telecom.CallScreeningService
import android.telecom.CallScreeningService.CallResponse
import android.util.Log

/**
 * Wired to Android's Telecom framework via the CALL_SCREENING role
 * (requested in MainActivity). Every incoming call is routed through
 * [onScreenCall] before it rings.
 *
 * Stub policy for this skeleton: allow every call through, unchanged.
 * The real behavior -- answering with the scripted greeting, transcribing
 * the caller's reply, and generating an acknowledgment -- is the pipeline
 * already validated on desktop in prototype/pipeline.py (faster-whisper ->
 * Llama 3.2 1B via llama.cpp -> Piper). Wiring it in here requires native
 * (NDK) Android builds of llama.cpp, whisper.cpp, and onnxruntime, plus
 * handling live in-call audio access -- none of that is done yet.
 */
class PehredarCallScreeningService : CallScreeningService() {

    override fun onScreenCall(callDetails: Call.Details) {
        val number = callDetails.handle?.schemeSpecificPart ?: "unknown"
        Log.d(TAG, "Incoming call from $number -- allowing (stub policy, no AI screening wired yet)")

        val response = CallResponse.Builder()
            .setDisallowCall(false)
            .setRejectCall(false)
            .setSkipCallLog(false)
            .setSkipNotification(false)
            .build()
        respondToCall(callDetails, response)
    }

    private companion object {
        const val TAG = "PehredarScreening"
    }
}
