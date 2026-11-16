package com.example.ocr

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import org.json.JSONArray
import org.json.JSONObject

/**
 * 100% Offline On-Device Receipt OCR Engine powered by bundled Google ML Kit Latin Text Recognition.
 * Requires zero internet connectivity, zero API keys, and zero external cloud calls.
 */
object OfflineReceiptOcrEngine {

    private const val MAX_OCR_DIMENSION = 1600

    fun recognizeFromBase64(
        base64DataUrl: String,
        onComplete: (String) -> Unit
    ) {
        var bitmap: Bitmap? = null
        try {
            val cleanBase64 = base64DataUrl.substringAfter(",", base64DataUrl)
            val bytes = Base64.decode(cleanBase64, Base64.DEFAULT)

            val boundsOpts = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size, boundsOpts)

            var sampleSize = 1
            while ((boundsOpts.outWidth / sampleSize) > MAX_OCR_DIMENSION ||
                (boundsOpts.outHeight / sampleSize) > MAX_OCR_DIMENSION
            ) {
                sampleSize *= 2
            }

            val decodeOpts = BitmapFactory.Options().apply {
                inSampleSize = sampleSize
                inPreferredConfig = Bitmap.Config.ARGB_8888
            }
            bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size, decodeOpts)
            if (bitmap == null) {
                onComplete(errorJson("Gagal membaca citra struk"))
                return
            }

            val image = InputImage.fromBitmap(bitmap, 0)
            val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

            recognizer.process(image)
                .addOnSuccessListener { visionText ->
                    try {
                        val allLines = mutableListOf<Pair<Int, String>>()
                        for (block in visionText.textBlocks) {
                            for (line in block.lines) {
                                val txt = line.text.trim()
                                if (txt.isNotEmpty()) {
                                    allLines.add((line.boundingBox?.top ?: 0) to txt)
                                }
                            }
                        }
                        allLines.sortBy { it.first }

                        val linesJson = JSONArray()
                        allLines.forEach { linesJson.put(it.second) }

                        val joined = allLines.joinToString("\n") { it.second }
                            .ifBlank { visionText.text.trim() }

                        val result = JSONObject().apply {
                            put("ok", true)
                            put("fullText", joined)
                            put("lines", linesJson)
                        }
                        onComplete(result.toString())
                    } finally {
                        bitmap?.recycle()
                        bitmap = null
                    }
                }
                .addOnFailureListener { ex ->
                    bitmap?.recycle()
                    bitmap = null
                    onComplete(errorJson(ex.message ?: "OCR gagal memproses struk"))
                }
        } catch (t: Throwable) {
            bitmap?.recycle()
            onComplete(errorJson(t.message ?: "Kesalahan pembacaan gambar"))
        }
    }

    private fun errorJson(message: String): String {
        return JSONObject().apply {
            put("ok", false)
            put("fullText", "")
            put("lines", JSONArray())
            put("error", message)
        }.toString()
    }
}
