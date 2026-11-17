package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.notification.VoraletNotificationHelper
import com.example.widget.PetWidgetProvider
import com.example.widget.StreakWidgetProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class WidgetAndNotificationTest {

  private lateinit var context: Context

  @Before
  fun setup() {
    context = ApplicationProvider.getApplicationContext()
    context.getSharedPreferences("voralet_widget_prefs", Context.MODE_PRIVATE).edit().clear().commit()
    context.getSharedPreferences("voralet_notification_prefs", Context.MODE_PRIVATE).edit().clear().commit()
  }

  @Test
  fun `streak snapshot handles empty state, active level 3, and expired timeout`() {
    // 1. Empty / never started
    val empty = StreakWidgetProvider.readStreakSnapshot(context)
    assertTrue(empty.hasNeverStarted)
    assertTrue(empty.isExpired)
    assertEquals(0, empty.currentStreak)
    assertEquals(0, empty.flameLevel)

    // 2. Active level 3 streak (10 days within 24h)
    val now = System.currentTimeMillis()
    StreakWidgetProvider.saveStreakData(
      context,
      """{"currentStreak":10,"lastActivityTimestamp":${now - 60_000L},"isExpired":false}"""
    )
    val active = StreakWidgetProvider.readStreakSnapshot(context)
    assertFalse(active.hasNeverStarted)
    assertFalse(active.isExpired)
    assertEquals(10, active.currentStreak)
    assertEquals(3, active.flameLevel)

    // 3. Expired (> 24 hours ago)
    val expiredTs = now - (25L * 60L * 60L * 1000L)
    StreakWidgetProvider.saveStreakData(
      context,
      """{"currentStreak":12,"lastActivityTimestamp":$expiredTs,"isExpired":false}"""
    )
    val expired = StreakWidgetProvider.readStreakSnapshot(context)
    assertFalse(expired.hasNeverStarted)
    assertTrue(expired.isExpired)
    assertEquals(0, expired.currentStreak)
    assertEquals(0, expired.flameLevel)
  }

  @Test
  fun `pet snapshot handles multi-day decay and legacy petCoins fallback`() {
    val fmt = SimpleDateFormat("yyyy-MM-dd", Locale.US)
    val twoDaysAgo = fmt.format(Date(System.currentTimeMillis() - 2L * 24L * 60L * 60L * 1000L))

    PetWidgetProvider.savePetData(
      context,
      """{"type":"CAT","name":"Luna","fullness":90,"happiness":80,"petCoins":140,"lastFedDate":"$twoDaysAgo"}"""
    )

    val snapshot = PetWidgetProvider.readPetSnapshot(context)
    assertEquals("CAT", snapshot.type)
    assertEquals("Luna", snapshot.name)
    assertEquals(140, snapshot.coins)
    assertEquals(60, snapshot.fullness) // 90 - (2 * 15)
    assertEquals(60, snapshot.happiness) // 80 - (2 * 10)
  }

  @Test
  fun `scheduleDailyReminder toggles enabled and disabled cleanly`() {
    VoraletNotificationHelper.scheduleDailyReminder(context, enabled = true, timeHHmm = "20:30")
    val prefs = context.getSharedPreferences("voralet_notification_prefs", Context.MODE_PRIVATE)
    assertTrue(prefs.getBoolean("reminder_enabled", false))
    assertEquals("20:30", prefs.getString("reminder_time", ""))

    VoraletNotificationHelper.scheduleDailyReminder(context, enabled = false, timeHHmm = "20:30")
    assertFalse(prefs.getBoolean("reminder_enabled", true))
  }
}
