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
 * Android Home Screen App Widget for Voralet Companion Pet 🐾.
 * Displays pet mood, fullness, happiness, and coin balance directly on the Android home screen.
 */
class PetWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        for (appWidgetId in appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    companion object {
        private const val PREFS_NAME = "voralet_widget_prefs"
        private const val KEY_PET_DATA = "pet_data_json"

        fun updateAllWidgets(context: Context) {
            val appWidgetManager = AppWidgetManager.getInstance(context)
            val thisWidget = ComponentName(context, PetWidgetProvider::class.java)
            val appWidgetIds = appWidgetManager.getAppWidgetIds(thisWidget)
            for (appWidgetId in appWidgetIds) {
                updateWidget(context, appWidgetManager, appWidgetId)
            }
        }

        fun savePetData(context: Context, petJson: String) {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            prefs.edit().putString(KEY_PET_DATA, petJson).apply()
            updateAllWidgets(context)
        }

        private fun updateWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
            val views = RemoteViews(context.packageName, R.layout.widget_pet)

            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val pendingIntent = PendingIntent.getActivity(
                context,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_pet_root, pendingIntent)

            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val rawJson = prefs.getString(KEY_PET_DATA, null)

            var petType = "DOG"
            var petName = "Milo"
            var fullness = 80
            var happiness = 85
            var coins = 50

            if (!rawJson.isNullOrEmpty()) {
                try {
                    val obj = JSONObject(rawJson)
                    petType = obj.optString("type", "DOG")
                    petName = obj.optString("name", if (petType == "CAT") "Luna" else "Milo")
                    fullness = obj.optInt("fullness", 80)
                    happiness = obj.optInt("happiness", 85)
                    coins = obj.optInt("coins", obj.optInt("petCoins", 50))
                } catch (_: Throwable) {
                    // fallback to defaults
                }
            }

            val isCat = petType.equals("CAT", ignoreCase = true)
            val petEmoji = if (isCat) "🐱" else "🐶"
            val typeLabel = if (isCat) "Cat" else "Dog"
            val foodLabel = if (isCat) "Kenyang 🐟" else "Kenyang 🍖"

            views.setTextViewText(R.id.widget_pet_avatar, petEmoji)
            views.setTextViewText(R.id.widget_pet_name, "$petName ($typeLabel)")
            views.setTextViewText(R.id.widget_pet_coins, "🪙 $coins")
            views.setTextViewText(R.id.widget_pet_fullness_title, foodLabel)
            views.setTextViewText(R.id.widget_pet_fullness_val, "$fullness%")
            views.setTextViewText(R.id.widget_pet_happiness_title, "Senang ❤️")
            views.setTextViewText(R.id.widget_pet_happiness_val, "$happiness%")

            if (fullness > 80 && happiness > 80) {
                views.setTextViewText(R.id.widget_pet_footer, "Peliharaan Sehat & Bahagia (+5 🪙 Harian Aktif!) ✨")
            } else if (fullness < 30 || happiness < 30) {
                views.setTextViewText(R.id.widget_pet_footer, "Peliharaan butuh perhatian! Ketuk untuk beri makan 🍖")
            } else {
                views.setTextViewText(R.id.widget_pet_footer, "Ketuk untuk elus dan rawat peliharaan ➜")
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
