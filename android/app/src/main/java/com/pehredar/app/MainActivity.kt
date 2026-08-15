package com.pehredar.app

import android.app.role.RoleManager
import android.content.Context
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView

    private val requestRoleLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            updateStatus()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        findViewById<Button>(R.id.enableButton).setOnClickListener { requestCallScreeningRole() }

        updateStatus()
    }

    override fun onResume() {
        super.onResume()
        updateStatus()
    }

    private fun roleManager(): RoleManager =
        getSystemService(Context.ROLE_SERVICE) as RoleManager

    private fun requestCallScreeningRole() {
        val roleManager = roleManager()
        if (!roleManager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING)) {
            statusText.text = getString(R.string.role_unavailable)
            return
        }
        if (roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)) {
            updateStatus()
            return
        }
        requestRoleLauncher.launch(roleManager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING))
    }

    private fun updateStatus() {
        val roleManager = roleManager()
        val held = roleManager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING) &&
            roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)
        statusText.text = getString(if (held) R.string.role_active else R.string.role_inactive)
    }
}
