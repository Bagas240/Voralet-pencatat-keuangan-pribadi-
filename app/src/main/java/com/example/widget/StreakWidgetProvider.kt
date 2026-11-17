package com.example.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import com.example.MainActivity
import com.example.R
import org.json.JSONObject

/**
 * Android Home Screen App Widget for Voralet Financial Streak.
 * Displays live 24-hour flame status, active streak days, and direct launcher.
 */
class StreakWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        for (appWidgetId in appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    internal data class StreakSnapshot(
        val currentStreak: Int,
        val flameLevel: Int,
        val isExpired: Boolean,
        val hasNeverStarted: Boolean
    )

    companion object {
        private const val PREFS_NAME = "voralet_widget_prefs"
        private const val KEY_STREAK_DATA = "streak_data_json"
        private const val TWENTY_FOUR_HOURS_MS = 24L * 60L * 60L * 1000L
        private const val REQUEST_CODE_LAUNCH = 101

        fun updateAllWidgets(context: Context) {
            val appWidgetManager = AppWidgetManager.getInstance(context)
            val thisWidget = ComponentName(context, StreakWidgetProvider::class.java)
            val appWidgetIds = appWidgetManager.getAppWidgetIds(thisWidget)
            for (appWidgetId in appWidgetIds) {
                updateWidget(context, appWidgetManager, appWidgetId)
            }
        }

        fun saveStreakData(context: Context, streakJson: String) {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().putString(KEY_STREAK_DATA, streakJson).apply()
            updateAllWidgets(context)
        }

        internal fun readStreakSnapshot(context: Context): StreakSnapshot {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val rawJson = prefs.getString(KEY_STREAK_DATA, null)

            if (rawJson.isNullOrEmpty()) {
                return StreakSnapshot(
                    currentStreak = 0,
                    flameLevel = 0,
                    isExpired = true,
                    hasNeverStarted = true
                )
            }

            return try {
                val obj = JSONObject(rawJson)
                val streakDays = obj.optInt("currentStreak", 0).coerceAtLeast(0)
                val lastTs = obj.optLong("lastActivityTimestamp", 0L)
                val markedExpired = obj.optBoolean("isExpired", false)
                val diff = if (lastTs > 0L) (System.currentTimeMillis() - lastTs) else Long.MAX_VALUE
                val expired = markedExpired || streakDays <= 0 || lastTs <= 0L || diff > TWENTY_FOUR_HOURS_MS

                val level = if (expired) {
                    0
                } else {
                    when {
                        streakDays >= 30 -> 5
                        streakDays >= 15 -> 4
                        streakDays >= 8 -> 3
                        streakDays >= 4 -> 2
                        else -> 1
                    }
                }

                StreakSnapshot(
                    currentStreak = if (expired) 0 else streakDays,
                    flameLevel = level,
                    isExpired = expired,
                    hasNeverStarted = lastTs <= 0L
                )
            } catch (_: Throwable) {
                StreakSnapshot(
                    currentStreak = 0,
                    flameLevel = 0,
                    isExpired = true,
                    hasNeverStarted = true
                )
            }
        }

        private fun updateWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
            val views = RemoteViews(context.packageName, R.layout.widget_streak)

            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val pendingIntent = PendingIntent.getActivity(
                context,
                REQUEST_CODE_LAUNCH,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_streak_root, pendingIntent)

            val snap = readStreakSnapshot(context)

            if (snap.isExpired) {
                views.setTextViewText(R.id.widget_streak_icon, if (snap.hasNeverStarted) "⚪" else "💨")
                views.setTextViewText(
                    R.id.widget_streak_count,
                    if (snap.hasNeverStarted) "Belum Aktif" else "Api Padam"
                )
                views.setTextViewText(
                    R.id.widget_streak_status,
                    "Catat transaksi di Voralet untuk nyalakan api"
                )
                views.setTextViewText(
                    R.id.widget_streak_badge,
                    if (snap.hasNeverStarted) "MULAI" else "PADAM"
                )
            } else {
                val flameEmoji = when (snap.flameLevel) {
                    1 -> "🔥"
                    2 -> "❤️‍🔥"
                    3 -> "💜"
                    4 -> "🩵"
                    5 -> "👑"
                    else -> "🔥"
                }
                views.setTextViewText(R.id.widget_streak_icon, flameEmoji)
                views.setTextViewText(R.id.widget_streak_count, "${snap.currentStreak} Hari Streak")
                views.setTextViewText(R.id.widget_streak_status, "Menyala • Level ${snap.flameLevel} (+10 🪙/hari)")
                views.setTextViewText(R.id.widget_streak_badge, "24 JAM")
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
