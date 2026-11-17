package com.example.notification

import android.Manifest
import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.example.MainActivity
import com.example.R
import com.example.widget.PetWidgetProvider
import com.example.widget.StreakWidgetProvider
import java.util.Calendar

/**
 * Native local notification scheduler for Voralet Pet Care & Daily Streak reminders.
 * Uses only optional POST_NOTIFICATIONS (API 33+) and inexact AlarmManager (no exact-alarm permission).
 */
object VoraletNotificationHelper {

    const val CHANNEL_ID = "voralet_pet_streak_channel"
    private const val NOTIFICATION_ID = 3501
    private const val REMINDER_REQUEST_CODE = 3502
    private const val PREFS_NAME = "voralet_notification_prefs"
    private const val KEY_ENABLED = "reminder_enabled"
    private const val KEY_TIME = "reminder_time"

    fun hasNotificationPermission(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }

    fun ensureChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
                ?: return
            val existing = manager.getNotificationChannel(CHANNEL_ID)
            if (existing == null) {
                val channel = NotificationChannel(
                    CHANNEL_ID,
                    "Pengingat Peliharaan & Streak Voralet",
                    NotificationManager.IMPORTANCE_DEFAULT
                ).apply {
                    description = "Notifikasi kondisi kenyang/senang peliharaan dan pengingat catat keuangan harian."
                }
                manager.createNotificationChannel(channel)
            }
        }
    }

    fun scheduleDailyReminder(context: Context, enabled: Boolean, timeHHmm: String?) {
        val cleanTime = (timeHHmm ?: "20:00").trim()
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putBoolean(KEY_ENABLED, enabled)
            .putString(KEY_TIME, cleanTime)
            .apply()

        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
        val intent = Intent(context, PetReminderReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            REMINDER_REQUEST_CODE,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        alarmManager.cancel(pendingIntent)
        if (!enabled) return

        val parts = cleanTime.split(":")
        val hour = parts.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: 20
        val minute = parts.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: 0

        val triggerCal = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
            if (timeInMillis <= System.currentTimeMillis()) {
                add(Calendar.DAY_OF_YEAR, 1)
            }
        }

        alarmManager.setInexactRepeating(
            AlarmManager.RTC_WAKEUP,
            triggerCal.timeInMillis,
            AlarmManager.INTERVAL_DAY,
            pendingIntent
        )
    }

    fun showPetAndStreakNotification(context: Context, isTest: Boolean = false) {
        if (!hasNotificationPermission(context)) return
        ensureChannel(context)

        val pet = PetWidgetProvider.readPetSnapshot(context)
        val streak = StreakWidgetProvider.readStreakSnapshot(context)

        val title: String
        val body: String

        when {
            pet.fullness < 45 || pet.happiness < 45 -> {
                title = "${pet.name} butuh perhatianmu"
                body = "Kenyang ${pet.fullness}% • Senang ${pet.happiness}%. Catat transaksi atau beri makan ${pet.name} sekarang."
            }
            streak.isExpired -> {
                title = "Nyalakan Api Streak & Rawat ${pet.name}"
                body = "Catat satu transaksi hari ini untuk menyalakan streak (+10 koin) dan merawat ${pet.name} (${pet.fullness}% kenyang)."
            }
            else -> {
                title = "${pet.name} sehat & Streak ${streak.currentStreak} hari aktif"
                body = "Kenyang ${pet.fullness}% • Senang ${pet.happiness}% • ${pet.coins} koin. Jaga terus kebiasaan baikmu."
            }
        }

        val finalTitle = if (isTest) "Tes Pengingat Voralet: $title" else title

        val launchIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentPendingIntent = PendingIntent.getActivity(
            context,
            REMINDER_REQUEST_CODE + 1,
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(finalTitle)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(contentPendingIntent)
            .setAutoCancel(true)
            .build()

        try {
            NotificationManagerCompat.from(context).notify(NOTIFICATION_ID, notification)
        } catch (_: SecurityException) {
            // Permission revoked externally
        }
    }
}

class PetReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        VoraletNotificationHelper.showPetAndStreakNotification(context, isTest = false)
    }
}
