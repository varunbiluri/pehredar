package com.pehredar.app

import android.Manifest
import android.app.role.RoleManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.CompoundButton
import android.widget.Switch
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var contactsStatusText: TextView
    private lateinit var silenceSwitch: Switch

    private val requestRoleLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
            updateStatus()
        }

    private val requestContactsPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) {
            updateStatus()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        contactsStatusText = findViewById(R.id.contactsStatusText)
        silenceSwitch = findViewById(R.id.silenceSwitch)

        findViewById<Button>(R.id.enableButton).setOnClickListener { requestCallScreeningRole() }
        findViewById<Button>(R.id.contactsButton).setOnClickListener {
            requestContactsPermissionLauncher.launch(Manifest.permission.READ_CONTACTS)
        }

        silenceSwitch.isChecked = Settings.isSilenceUnknownNumbersEnabled(this)
        silenceSwitch.setOnCheckedChangeListener { _: CompoundButton, checked: Boolean ->
            Settings.setSilenceUnknownNumbersEnabled(this, checked)
        }

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

    private fun hasContactsPermission(): Boolean =
        ContextCompat.checkSelfPermission(this, Manifest.permission.READ_CONTACTS) ==
            PackageManager.PERMISSION_GRANTED

    private fun updateStatus() {
        val roleManager = roleManager()
        val roleHeld = roleManager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING) &&
            roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)
        statusText.text = getString(if (roleHeld) R.string.role_active else R.string.role_inactive)

        contactsStatusText.text = getString(
            if (hasContactsPermission()) R.string.contacts_granted else R.string.contacts_not_granted
        )
        silenceSwitch.isEnabled = hasContactsPermission()
    }
}
