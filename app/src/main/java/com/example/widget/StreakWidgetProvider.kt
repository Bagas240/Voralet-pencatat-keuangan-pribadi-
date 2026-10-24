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
 * Android Home Screen App Widget for Voralet Financial Streak 🔥.
 * Displays the 24-hour flame status, active streak days, and direct launcher.
 */
class StreakWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        for (appWidgetId in appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    companion object {
        private const val PREFS_NAME = "voralet_widget_prefs"
        private const val KEY_STREAK_DATA = "streak_data_json"

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

        private fun updateWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
            val views = RemoteViews(context.packageName, R.layout.widget_streak)

            // Setup launch intent to open MainActivity
            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val pendingIntent = PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_streak_root, pendingIntent)

            // Parse saved streak data
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val rawJson = prefs.getString(KEY_STREAK_DATA, null)

            var streakDays = 1
            var isExpired = false
            var flameLevel = 1

            if (!rawJson.isNullOrEmpty()) {
                try {
                    val obj = JSONObject(rawJson)
                    streakDays = obj.optInt("currentStreak", 1)
                    val lastTs = obj.optLong("lastActivityTimestamp", 0L)
                    val now = System.currentTimeMillis()
                    val diff = now - lastTs
                    // 24 hours expiry
                    isExpired = lastTs > 0L && diff > (24L * 60L * 60L * 1000L)
                    flameLevel = when {
                        isExpired || streakDays <= 0 -> 0
                        streakDays in 1..3 -> 1
                        streakDays in 4..7 -> 2
                        streakDays in 8..14 -> 3
                        streakDays in 15..29 -> 4
                        else -> 5
                    }
                } catch (_: Throwable) {
                    streakDays = 1
                }
            }

            if (isExpired) {
                views.setTextViewText(R.id.widget_streak_icon, "💨")
                views.setTextViewText(R.id.widget_streak_count, "Api Padam")
                views.setTextViewText(R.id.widget_streak_status, "Buka Voralet untuk mulai kembali!")
                views.setTextViewText(R.id.widget_streak_badge, "PADAM")
            } else {
                val flameEmoji = when (flameLevel) {
                    1 -> "🔥"
                    2 -> "❤️‍🔥"
                    3 -> "💜"
                    4 -> "🩵"
                    5 -> "👑"
                    else -> "🔥"
                }
                views.setTextViewText(R.id.widget_streak_icon, flameEmoji)
                views.setTextViewText(R.id.widget_streak_count, "$streakDays Hari Streak")
                views.setTextViewText(R.id.widget_streak_status, "Menyala • Level $flameLevel (+10 🪙/hari)")
                views.setTextViewText(R.id.widget_streak_badge, "24 JAM")
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
