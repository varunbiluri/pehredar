package com.pehredar.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.widget.EditText
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.button.MaterialButton
import java.util.Locale

class AiLabActivity : AppCompatActivity(), RecognitionListener, TextToSpeech.OnInitListener {
    private lateinit var input: EditText
    private lateinit var result: TextView
    private lateinit var listenButton: MaterialButton
    private lateinit var speakButton: MaterialButton
    private var recognizer: SpeechRecognizer? = null
    private var tts: TextToSpeech? = null
    private var lastReply = ""
    private var offlineTtsAvailable = false

    private val microphonePermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) startListening() else result.setText(R.string.ai_permission_denied)
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_ai_lab)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        input = findViewById(R.id.aiInput)
        result = findViewById(R.id.aiResult)
        listenButton = findViewById(R.id.aiListenButton)
        speakButton = findViewById(R.id.aiSpeakButton)
        findViewById<MaterialButton>(R.id.aiAnalyzeButton).setOnClickListener { analyze() }
        listenButton.setOnClickListener { requestListening() }
        speakButton.setOnClickListener { speakReply() }

        val onDeviceSttAvailable = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
            SpeechRecognizer.isOnDeviceRecognitionAvailable(this)
        listenButton.isEnabled = onDeviceSttAvailable
        if (onDeviceSttAvailable) {
            recognizer = SpeechRecognizer.createOnDeviceSpeechRecognizer(this).also {
                it.setRecognitionListener(this)
            }
        }
        tts = TextToSpeech(this, this)
    }

    private fun requestListening() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) ==
            PackageManager.PERMISSION_GRANTED
        ) startListening() else microphonePermission.launch(Manifest.permission.RECORD_AUDIO)
    }

    private fun startListening() {
        val speechRecognizer = recognizer ?: run {
            result.setText(R.string.ai_stt_unavailable)
            return
        }
        result.setText(R.string.ai_listening)
        speechRecognizer.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        })
    }

    private fun analyze() {
        val analysis = LocalAiEngine.analyze(input.text?.toString().orEmpty())
        val risk = when (analysis.risk) {
            RiskLevel.HIGH -> R.string.ai_risk_high
            RiskLevel.MEDIUM -> R.string.ai_risk_medium
            RiskLevel.LOW -> R.string.ai_risk_low
        }
        val category = when (analysis.intent) {
            CallerIntent.SCAM_RISK -> R.string.ai_category_scam
            CallerIntent.DELIVERY -> R.string.ai_category_delivery
            CallerIntent.APPOINTMENT -> R.string.ai_category_appointment
            CallerIntent.BUSINESS -> R.string.ai_category_business
            CallerIntent.PERSONAL -> R.string.ai_category_personal
            CallerIntent.UNKNOWN -> R.string.ai_category_unknown
        }
        val reply = when (analysis.intent) {
            CallerIntent.SCAM_RISK -> R.string.ai_reply_scam
            CallerIntent.DELIVERY -> R.string.ai_reply_delivery
            CallerIntent.APPOINTMENT -> R.string.ai_reply_appointment
            CallerIntent.BUSINESS -> R.string.ai_reply_business
            CallerIntent.PERSONAL -> R.string.ai_reply_personal
            CallerIntent.UNKNOWN -> R.string.ai_reply_unknown
        }
        lastReply = getString(reply)
        result.text = getString(R.string.ai_result_format, getString(risk), getString(category), lastReply)
        speakButton.isEnabled = offlineTtsAvailable
    }

    private fun speakReply() {
        if (lastReply.isNotBlank()) tts?.speak(lastReply, TextToSpeech.QUEUE_FLUSH, null, "pehredar_reply")
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val language = Locale.getDefault()
            tts?.language = language
            val offlineVoice = tts?.voices
                ?.filterNot { it.isNetworkConnectionRequired }
                ?.filter { it.locale.language == language.language }
                ?.maxByOrNull { it.quality }
            offlineTtsAvailable = offlineVoice != null
            if (offlineVoice != null) tts?.voice = offlineVoice
            speakButton.isEnabled = offlineTtsAvailable && lastReply.isNotBlank()
        } else speakButton.isEnabled = false
    }

    override fun onResults(results: Bundle?) {
        input.setText(results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull().orEmpty())
        analyze()
    }

    override fun onError(error: Int) { result.setText(R.string.ai_stt_unavailable) }
    override fun onReadyForSpeech(params: Bundle?) = Unit
    override fun onBeginningOfSpeech() = Unit
    override fun onRmsChanged(rmsdB: Float) = Unit
    override fun onBufferReceived(buffer: ByteArray?) = Unit
    override fun onEndOfSpeech() = Unit
    override fun onPartialResults(partialResults: Bundle?) = Unit
    override fun onEvent(eventType: Int, params: Bundle?) = Unit

    override fun onDestroy() {
        recognizer?.destroy()
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}
