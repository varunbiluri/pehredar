package com.pehredar.app

import android.content.Context

object Settings {
    private const val PREFS_NAME = "pehredar_settings"
    private const val KEY_SILENCE_UNKNOWN = "silence_unknown_numbers"

    fun isSilenceUnknownNumbersEnabled(context: Context): Boolean =
        prefs(context).getBoolean(KEY_SILENCE_UNKNOWN, false)

    fun setSilenceUnknownNumbersEnabled(context: Context, enabled: Boolean) {
        prefs(context).edit().putBoolean(KEY_SILENCE_UNKNOWN, enabled).apply()
    }

    private fun prefs(context: Context) =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
}
