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
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit

/**
 * Android Home Screen App Widget for Voralet Companion Pet.
 * Displays live pet mood, fullness (with daily decay), happiness, and coin balance.
 */
class PetWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        for (appWidgetId in appWidgetIds) {
            updateWidget(context, appWidgetManager, appWidgetId)
        }
    }

    internal data class PetSnapshot(
        val type: String,
        val name: String,
        val fullness: Int,
        val happiness: Int,
        val coins: Int
    )

    companion object {
        private const val PREFS_NAME = "voralet_widget_prefs"
        private const val KEY_PET_DATA = "pet_data_json"
        private const val REQUEST_CODE_LAUNCH = 102

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

        internal fun readPetSnapshot(context: Context): PetSnapshot {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val rawJson = prefs.getString(KEY_PET_DATA, null)

            var petType = "DOG"
            var petName = "Milo"
            var fullness = 80
            var happiness = 85
            var coins = 50
            var lastFedDate = ""

            if (!rawJson.isNullOrEmpty()) {
                try {
                    val obj = JSONObject(rawJson)
                    petType = obj.optString("type", "DOG").ifBlank { "DOG" }
                    val defaultName = if (petType.equals("CAT", ignoreCase = true)) "Luna" else "Milo"
                    petName = obj.optString("name", defaultName).ifBlank { defaultName }
                    fullness = obj.optInt("fullness", 80).coerceIn(0, 100)
                    happiness = obj.optInt("happiness", 85).coerceIn(0, 100)
                    coins = if (obj.has("coins")) {
                        obj.optInt("coins", 50)
                    } else {
                        obj.optInt("petCoins", 50)
                    }.coerceAtLeast(0)
                    lastFedDate = obj.optString("lastFedDate", "")
                } catch (_: Throwable) {
                    // fallback to defaults
                }
            }

            if (lastFedDate.isNotBlank()) {
                val daysElapsed = computeElapsedDays(lastFedDate)
                if (daysElapsed > 0) {
                    fullness = (fullness - daysElapsed * 15).coerceAtLeast(15)
                    happiness = (happiness - daysElapsed * 10).coerceAtLeast(20)
                }
            }

            return PetSnapshot(
                type = petType,
                name = petName,
                fullness = fullness,
                happiness = happiness,
                coins = coins
            )
        }

        private fun computeElapsedDays(lastFedDate: String): Int {
            return try {
                val fmt = SimpleDateFormat("yyyy-MM-dd", Locale.US).apply { isLenient = false }
                val last = fmt.parse(lastFedDate) ?: return 0
                val todayStr = fmt.format(Date())
                val today = fmt.parse(todayStr) ?: return 0
                val diffMs = today.time - last.time
                if (diffMs <= 0L) 0 else TimeUnit.MILLISECONDS.toDays(diffMs).toInt()
            } catch (_: Throwable) {
                0
            }
        }

        private fun updateWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
            val views = RemoteViews(context.packageName, R.layout.widget_pet)

            val intent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            }
            val pendingIntent = PendingIntent.getActivity(
                context,
                REQUEST_CODE_LAUNCH,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_pet_root, pendingIntent)

            val pet = readPetSnapshot(context)
            val isCat = pet.type.equals("CAT", ignoreCase = true)
            val petEmoji = if (isCat) "🐱" else "🐶"
            val typeLabel = if (isCat) "Cat" else "Dog"
            val foodLabel = if (isCat) "Kenyang 🐟" else "Kenyang 🍖"

            views.setTextViewText(R.id.widget_pet_avatar, petEmoji)
            views.setTextViewText(R.id.widget_pet_name, "${pet.name} ($typeLabel)")
            views.setTextViewText(R.id.widget_pet_coins, "🪙 ${pet.coins}")
            views.setTextViewText(R.id.widget_pet_fullness_title, foodLabel)
            views.setTextViewText(R.id.widget_pet_fullness_val, "${pet.fullness}%")
            views.setTextViewText(R.id.widget_pet_happiness_title, "Senang ❤️")
            views.setTextViewText(R.id.widget_pet_happiness_val, "${pet.happiness}%")

            if (pet.fullness > 80 && pet.happiness > 80) {
                views.setTextViewText(R.id.widget_pet_footer, "Peliharaan Sehat & Bahagia (+5 🪙 Harian Aktif!) ✨")
            } else if (pet.fullness < 40 || pet.happiness < 40) {
                views.setTextViewText(R.id.widget_pet_footer, "${pet.name} butuh perhatian! Ketuk untuk beri makan 🍖")
            } else {
                views.setTextViewText(R.id.widget_pet_footer, "Ketuk untuk elus dan rawat peliharaan ➜")
            }

            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}
