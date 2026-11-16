package com.example.security

import android.content.Context
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import java.util.zip.Inflater
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

/**
 * In-memory authenticated decryptor for the encrypted Voralet offline web vault (voralet_core.bin).
 * Prevents casual APK extraction from exposing plain HTML/JavaScript source files in assets/.
 *
 * Binary format (VRLT1):
 *   Bytes 0..4   : Magic "VRLT1"
 *   Bytes 5..16  : 12-byte ChaCha20 nonce
 *   Bytes 17..48 : 32-byte HMAC-SHA256 tag over (Magic || Nonce || Ciphertext)
 *   Bytes 49..N  : ChaCha20-encrypted zlib-compressed payload
 */
object AssetVaultDecryptor {

    private val MAGIC = byteArrayOf(0x56, 0x52, 0x4C, 0x54, 0x31) // "VRLT1"

    // Split obfuscated key shards (masked with per-index transforms)
    private val SHARD_A = intArrayOf(
        0x79, 0x2F, 0x7A, 0x62, 0x47, 0x6F, 0x52, 0x79,
        0x7D, 0x6D, 0x5C, 0x45, 0x5F, 0x40, 0x7E, 0x2F,
        0x22, 0x51, 0x71, 0x3D, 0x52, 0x26, 0x2E, 0x65,
        0x48, 0x3A, 0x6B, 0x42, 0x76, 0x59, 0x2D, 0x5B
    )

    private val SHARD_B = intArrayOf(
        0x2F, 0x40, 0x28, 0x23, 0x2B, 0x2A, 0x37, 0x0D,
        0x22, 0x2B, 0x2A, 0x2C, 0x33, 0x34, 0x10, 0x4C,
        0x41, 0x39, 0x1E, 0x5E, 0x37, 0x45, 0x4A, 0x0B,
        0x20, 0x5C, 0x0D, 0x37, 0x17, 0x3F, 0x49, 0x33
    )

    internal fun deriveVaultKeys(): Pair<ByteArray, ByteArray> {
        val rawSeed = ByteArray(32) { idx ->
            ((SHARD_A[idx] xor SHARD_B[idx]) and 0xFF).toByte()
        }
        val digest = MessageDigest.getInstance("SHA-256")
        val encKey = digest.digest(rawSeed + "ENC_CHACHA20_V1".toByteArray(Charsets.UTF_8))
        val macKey = MessageDigest.getInstance("SHA-256")
            .digest(rawSeed + "MAC_HMACSHA256_V1".toByteArray(Charsets.UTF_8))
        return encKey to macKey
    }

    fun loadDecryptedHtml(context: Context, assetName: String = "voralet_core.bin"): ByteArray {
        val blob = context.assets.open(assetName).use { it.readBytes() }
        return decryptBlob(blob)
    }

    fun decryptBlob(blob: ByteArray): ByteArray {
        require(blob.size > 49) { "Corrupt vault container" }
        for (i in MAGIC.indices) {
            require(blob[i] == MAGIC[i]) { "Invalid vault header" }
        }

        val nonce = blob.copyOfRange(5, 17)
        val expectedTag = blob.copyOfRange(17, 49)
        val ciphertext = blob.copyOfRange(49, blob.size)

        val (encKey, macKey) = deriveVaultKeys()

        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(macKey, "HmacSHA256"))
        mac.update(MAGIC)
        mac.update(nonce)
        mac.update(ciphertext)
        val actualTag = mac.doFinal()

        require(MessageDigest.isEqual(expectedTag, actualTag)) { "Vault integrity check failed" }

        val compressed = chacha20Xor(encKey, nonce, 1, ciphertext)
        return inflateZlib(compressed)
    }

    private fun inflateZlib(compressed: ByteArray): ByteArray {
        val inflater = Inflater()
        return try {
            inflater.setInput(compressed)
            val buffer = ByteArray(8192)
            val out = ByteArrayOutputStream(compressed.size * 2)
            while (!inflater.finished()) {
                val count = inflater.inflate(buffer)
                if (count == 0 && inflater.needsInput()) break
                if (count > 0) out.write(buffer, 0, count)
            }
            out.toByteArray()
        } finally {
            inflater.end()
        }
    }

    private fun chacha20Xor(key: ByteArray, nonce: ByteArray, initialCounter: Int, input: ByteArray): ByteArray {
        val output = ByteArray(input.size)
        val keyStream = ByteArray(64)
        var counter = initialCounter
        var offset = 0

        while (offset < input.size) {
            chacha20Block(key, counter, nonce, keyStream)
            val blockLen = minOf(64, input.size - offset)
            for (i in 0 until blockLen) {
                output[offset + i] = (input[offset + i].toInt() xor keyStream[i].toInt()).toByte()
            }
            offset += blockLen
            counter++
        }
        return output
    }

    private fun chacha20Block(key: ByteArray, counter: Int, nonce: ByteArray, out: ByteArray) {
        val state = IntArray(16)
        state[0] = 0x61707865
        state[1] = 0x3320646e
        state[2] = 0x79622d32
        state[3] = 0x6b206574

        val keyBuf = ByteBuffer.wrap(key).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until 8) {
            state[4 + i] = keyBuf.getInt(i * 4)
        }
        state[12] = counter
        val nonceBuf = ByteBuffer.wrap(nonce).order(ByteOrder.LITTLE_ENDIAN)
        state[13] = nonceBuf.getInt(0)
        state[14] = nonceBuf.getInt(4)
        state[15] = nonceBuf.getInt(8)

        val working = state.copyOf()
        for (round in 0 until 10) {
            quarterRound(working, 0, 4, 8, 12)
            quarterRound(working, 1, 5, 9, 13)
            quarterRound(working, 2, 6, 10, 14)
            quarterRound(working, 3, 7, 11, 15)
            quarterRound(working, 0, 5, 10, 15)
            quarterRound(working, 1, 6, 11, 12)
            quarterRound(working, 2, 7, 8, 13)
            quarterRound(working, 3, 4, 9, 14)
        }

        val outBuf = ByteBuffer.wrap(out).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until 16) {
            outBuf.putInt(i * 4, working[i] + state[i])
        }
    }

    private fun quarterRound(x: IntArray, a: Int, b: Int, c: Int, d: Int) {
        x[a] += x[b]; x[d] = Integer.rotateLeft(x[d] xor x[a], 16)
        x[c] += x[d]; x[b] = Integer.rotateLeft(x[b] xor x[c], 12)
        x[a] += x[b]; x[d] = Integer.rotateLeft(x[d] xor x[a], 8)
        x[c] += x[d]; x[b] = Integer.rotateLeft(x[b] xor x[c], 7)
    }
}
