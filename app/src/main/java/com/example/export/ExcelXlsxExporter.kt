package com.example.export

import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/**
 * Pure Kotlin OOXML (.xlsx) Multi-Sheet Workbook Exporter.
 * Generates genuine Microsoft Excel 2007+ (.xlsx) files offline using standard ZipOutputStream
 * with zero external dependencies and full Rupiah currency formatting.
 */
object ExcelXlsxExporter {

    private data class CellData(
        val value: String = "",
        val isNumber: Boolean = false,
        val numericValue: Double = 0.0,
        val styleIndex: Int = STYLE_BODY_LEFT
    )

    private const val STYLE_BODY_LEFT = 1
    private const val STYLE_BODY_CENTER = 2
    private const val STYLE_BODY_BOLD = 3
    private const val STYLE_TITLE = 4
    private const val STYLE_SUBTITLE = 5
    private const val STYLE_HEADER = 6
    private const val STYLE_CURRENCY = 7
    private const val STYLE_CURRENCY_INCOME = 8
    private const val STYLE_CURRENCY_EXPENSE = 9
    private const val STYLE_CURRENCY_BOLD = 10
    private const val STYLE_TOTAL_LABEL = 11
    private const val STYLE_TOTAL_CURRENCY = 12

    fun buildWorkbook(payloadJson: String): ByteArray {
        val root = JSONObject(payloadJson)
        val userProfile = root.optJSONObject("userProfile") ?: JSONObject()
        val accounts = root.optJSONArray("accounts") ?: JSONArray()
        val transactions = root.optJSONArray("transactions") ?: JSONArray()
        val savingsGoals = root.optJSONArray("savingsGoals") ?: JSONArray()
        val debts = root.optJSONArray("debts") ?: JSONArray()
        val categoryLabels = root.optJSONObject("categoryLabels") ?: JSONObject()

        val ownerName = userProfile.optString("name", "Pengguna Voralet").ifBlank { "Pengguna Voralet" }
        val username = userProfile.optString("username", "").let { if (it.isNotBlank()) " (@$it)" else "" }
        val exportDate = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.forLanguageTag("id-ID")).format(Date())

        val accountNameMap = HashMap<String, String>()
        for (i in 0 until accounts.length()) {
            val acc = accounts.optJSONObject(i) ?: continue
            accountNameMap[acc.optString("id")] = acc.optString("name", "Dompet")
        }

        // Compute financial aggregates
        var totalIncome = 0.0
        var totalExpense = 0.0
        var txCountIncome = 0
        var txCountExpense = 0
        val accountIncomeMap = HashMap<String, Double>()
        val accountExpenseMap = HashMap<String, Double>()

        for (i in 0 until transactions.length()) {
            val tx = transactions.optJSONObject(i) ?: continue
            val type = tx.optString("type")
            val amt = tx.optDouble("amount", 0.0)
            val accId = tx.optString("accountId")
            if (type == "INCOME") {
                totalIncome += amt
                txCountIncome++
                accountIncomeMap[accId] = (accountIncomeMap[accId] ?: 0.0) + amt
            } else if (type == "EXPENSE") {
                totalExpense += amt
                txCountExpense++
                accountExpenseMap[accId] = (accountExpenseMap[accId] ?: 0.0) + amt
            }
        }

        var totalWalletBalance = 0.0
        for (i in 0 until accounts.length()) {
            val acc = accounts.optJSONObject(i) ?: continue
            val accId = acc.optString("id")
            val initBal = acc.optDouble("initialBalance", acc.optDouble("balance", 0.0))
            val curBal = initBal + (accountIncomeMap[accId] ?: 0.0) - (accountExpenseMap[accId] ?: 0.0)
            totalWalletBalance += curBal
        }

        var totalSavingsTarget = 0.0
        var totalSavingsCollected = 0.0
        for (i in 0 until savingsGoals.length()) {
            val g = savingsGoals.optJSONObject(i) ?: continue
            totalSavingsTarget += g.optDouble("targetAmount", 0.0)
            totalSavingsCollected += g.optDouble("currentAmount", 0.0)
        }

        var unpaidHutang = 0.0
        var unpaidPiutang = 0.0
        for (i in 0 until debts.length()) {
            val d = debts.optJSONObject(i) ?: continue
            val isPaid = d.optBoolean("isPaid", false) || d.optString("status") == "LUNAS"
            if (!isPaid) {
                val rem = maxOf(0.0, d.optDouble("amount", 0.0) - d.optDouble("paidAmount", 0.0))
                if (d.optString("type") == "PIUTANG") unpaidPiutang += rem else unpaidHutang += rem
            }
        }

        val netCashflow = totalIncome - totalExpense
        val netWorth = totalWalletBalance + totalSavingsCollected + unpaidPiutang - unpaidHutang

        val sheets = listOf(
            "Ringkasan Keuangan" to buildSummarySheet(
                ownerName, username, exportDate,
                totalWalletBalance, totalIncome, totalExpense, netCashflow,
                totalSavingsCollected, totalSavingsTarget,
                unpaidPiutang, unpaidHutang, netWorth,
                transactions.length(), txCountIncome, txCountExpense,
                accounts.length(), savingsGoals.length(), debts.length()
            ),
            "Mutasi Transaksi" to buildTransactionsSheet(transactions, accountNameMap, categoryLabels, totalIncome, totalExpense, netCashflow),
            "Hutang & Piutang" to buildDebtsSheet(debts, unpaidHutang, unpaidPiutang),
            "Tabungan Impian" to buildSavingsSheet(savingsGoals, totalSavingsTarget, totalSavingsCollected),
            "Daftar Dompet" to buildWalletsSheet(accounts, accountIncomeMap, accountExpenseMap, totalWalletBalance)
        )

        val baos = ByteArrayOutputStream(16384)
        ZipOutputStream(baos).use { zos ->
            writeZipEntry(zos, "[Content_Types].xml", buildContentTypesXml(sheets.size))
            writeZipEntry(zos, "_rels/.rels", buildRootRelsXml())
            writeZipEntry(zos, "xl/workbook.xml", buildWorkbookXml(sheets.map { it.first }))
            writeZipEntry(zos, "xl/_rels/workbook.xml.rels", buildWorkbookRelsXml(sheets.size))
            writeZipEntry(zos, "xl/styles.xml", buildStylesXml())
            sheets.forEachIndexed { idx, (_, xmlContent) ->
                writeZipEntry(zos, "xl/worksheets/sheet${idx + 1}.xml", xmlContent)
            }
        }
        return baos.toByteArray()
    }

    private fun writeZipEntry(zos: ZipOutputStream, name: String, content: String) {
        val entry = ZipEntry(name)
        zos.putNextEntry(entry)
        zos.write(content.toByteArray(Charsets.UTF_8))
        zos.closeEntry()
    }

    private fun buildSummarySheet(
        ownerName: String,
        username: String,
        exportDate: String,
        totalWalletBalance: Double,
        totalIncome: Double,
        totalExpense: Double,
        netCashflow: Double,
        totalSavingsCollected: Double,
        totalSavingsTarget: Double,
        unpaidPiutang: Double,
        unpaidHutang: Double,
        netWorth: Double,
        txTotal: Int,
        txIn: Int,
        txOut: Int,
        accCount: Int,
        goalCount: Int,
        debtCount: Int
    ): String {
        val rows = ArrayList<List<CellData>>()
        rows.add(listOf(CellData("VORALET — LAPORAN PEMBUKUAN KEUANGAN (.XLSX)", styleIndex = STYLE_TITLE)))
        rows.add(listOf(CellData("Pemilik: $ownerName$username  |  Diekspor: $exportDate WIB  |  100% Offline Vault", styleIndex = STYLE_SUBTITLE)))
        rows.add(emptyList())
        rows.add(listOf(
            CellData("INDIKATOR KEUANGAN UTAMA", styleIndex = STYLE_HEADER),
            CellData("NILAI / NOMINAL (IDR)", styleIndex = STYLE_HEADER),
            CellData("KETERANGAN", styleIndex = STYLE_HEADER)
        ))
        rows.add(listOf(
            CellData("Total Saldo Dompet Aktif", styleIndex = STYLE_BODY_BOLD),
            CellData(isNumber = true, numericValue = totalWalletBalance, styleIndex = STYLE_CURRENCY_BOLD),
            CellData("$accCount Kantong Keuangan", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("Total Pemasukan Tercatat", styleIndex = STYLE_BODY_LEFT),
            CellData(isNumber = true, numericValue = totalIncome, styleIndex = STYLE_CURRENCY_INCOME),
            CellData("$txIn Transaksi Masuk", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("Total Pengeluaran Tercatat", styleIndex = STYLE_BODY_LEFT),
            CellData(isNumber = true, numericValue = totalExpense, styleIndex = STYLE_CURRENCY_EXPENSE),
            CellData("$txOut Transaksi Keluar", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("Arus Kas Bersih (Surplus / Defisit)", styleIndex = STYLE_BODY_BOLD),
            CellData(isNumber = true, numericValue = netCashflow, styleIndex = if (netCashflow >= 0) STYLE_CURRENCY_INCOME else STYLE_CURRENCY_EXPENSE),
            CellData("$txTotal Total Mutasi", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("Total Tabungan Impian Terkumpul", styleIndex = STYLE_BODY_LEFT),
            CellData(isNumber = true, numericValue = totalSavingsCollected, styleIndex = STYLE_CURRENCY),
            CellData("Dari target ${formatIdrText(totalSavingsTarget)} ($goalCount Target)", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("Total Piutang Aktif (Hak Tagih)", styleIndex = STYLE_BODY_LEFT),
            CellData(isNumber = true, numericValue = unpaidPiutang, styleIndex = STYLE_CURRENCY_INCOME),
            CellData("Aset pinjaman yang belum kembali ($debtCount Catatan)", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("Total Hutang Aktif (Kewajiban)", styleIndex = STYLE_BODY_LEFT),
            CellData(isNumber = true, numericValue = unpaidHutang, styleIndex = STYLE_CURRENCY_EXPENSE),
            CellData("Kewajiban yang harus dilunasi", styleIndex = STYLE_BODY_LEFT)
        ))
        rows.add(listOf(
            CellData("ESTIMASI KEKAYAAN BERSIH (NET WORTH)", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = netWorth, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData("Saldo + Tabungan + Piutang - Hutang", styleIndex = STYLE_TOTAL_LABEL)
        ))

        return renderWorksheetXml(
            rows = rows,
            colWidths = listOf(38.0, 26.0, 40.0),
            mergedRanges = listOf("A1:C1", "A2:C2"),
            freezeRow = 4
        )
    }

    private fun buildTransactionsSheet(
        transactions: JSONArray,
        accountNameMap: Map<String, String>,
        categoryLabels: JSONObject,
        totalIncome: Double,
        totalExpense: Double,
        netCashflow: Double
    ): String {
        val sortedList = ArrayList<JSONObject>(transactions.length())
        for (i in 0 until transactions.length()) {
            transactions.optJSONObject(i)?.let { sortedList.add(it) }
        }
        sortedList.sortByDescending { it.optString("date", "") }

        val rows = ArrayList<List<CellData>>()
        rows.add(listOf(CellData("BUKU MUTASI & ARUS KAS TRANSAKSI", styleIndex = STYLE_TITLE)))
        rows.add(listOf(
            CellData("NO", styleIndex = STYLE_HEADER),
            CellData("TANGGAL", styleIndex = STYLE_HEADER),
            CellData("TIPE", styleIndex = STYLE_HEADER),
            CellData("KATEGORI", styleIndex = STYLE_HEADER),
            CellData("KANTONG / DOMPET", styleIndex = STYLE_HEADER),
            CellData("CATATAN / TOKO", styleIndex = STYLE_HEADER),
            CellData("NOMINAL (IDR)", styleIndex = STYLE_HEADER),
            CellData("SUMBER", styleIndex = STYLE_HEADER)
        ))

        if (sortedList.isEmpty()) {
            rows.add(listOf(CellData("Belum ada mutasi transaksi yang tercatat.", styleIndex = STYLE_BODY_CENTER)))
        } else {
            sortedList.forEachIndexed { idx, tx ->
                val isInc = tx.optString("type") == "INCOME"
                val catKey = tx.optString("category", "lainnya")
                val catName = categoryLabels.optString(catKey, catKey).ifBlank { "Lainnya" }
                val accName = accountNameMap[tx.optString("accountId")] ?: "Dompet Utama"
                val noteText = tx.optString("notes", tx.optString("note", "")).ifBlank { catName }
                val amt = tx.optDouble("amount", 0.0)
                val sourceLabel = if (tx.optBoolean("isReceiptScan", false) || tx.optString("receiptImage", "").isNotBlank()) "Scan Struk" else "Input Manual"

                rows.add(listOf(
                    CellData(isNumber = true, numericValue = (idx + 1).toDouble(), styleIndex = STYLE_BODY_CENTER),
                    CellData(tx.optString("date", "-"), styleIndex = STYLE_BODY_CENTER),
                    CellData(if (isInc) "MASUK" else "KELUAR", styleIndex = STYLE_BODY_CENTER),
                    CellData(catName, styleIndex = STYLE_BODY_LEFT),
                    CellData(accName, styleIndex = STYLE_BODY_LEFT),
                    CellData(noteText, styleIndex = STYLE_BODY_LEFT),
                    CellData(isNumber = true, numericValue = amt, styleIndex = if (isInc) STYLE_CURRENCY_INCOME else STYLE_CURRENCY_EXPENSE),
                    CellData(sourceLabel, styleIndex = STYLE_BODY_CENTER)
                ))
            }
        }

        rows.add(listOf(
            CellData("TOTAL PEMASUKAN", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = totalIncome, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData("", styleIndex = STYLE_TOTAL_LABEL)
        ))
        rows.add(listOf(
            CellData("TOTAL PENGELUARAN", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = totalExpense, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData("", styleIndex = STYLE_TOTAL_LABEL)
        ))
        rows.add(listOf(
            CellData("SELISIH ARUS KAS BERSIH", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = netCashflow, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData("", styleIndex = STYLE_TOTAL_LABEL)
        ))

        return renderWorksheetXml(
            rows = rows,
            colWidths = listOf(7.0, 14.0, 12.0, 22.0, 22.0, 34.0, 22.0, 15.0),
            mergedRanges = listOf("A1:H1"),
            freezeRow = 2
        )
    }

    private fun buildDebtsSheet(debts: JSONArray, unpaidHutang: Double, unpaidPiutang: Double): String {
        val rows = ArrayList<List<CellData>>()
        rows.add(listOf(CellData("BUKU CATATAN HUTANG & PIUTANG", styleIndex = STYLE_TITLE)))
        rows.add(listOf(
            CellData("NO", styleIndex = STYLE_HEADER),
            CellData("JENIS", styleIndex = STYLE_HEADER),
            CellData("NAMA PIHAK", styleIndex = STYLE_HEADER),
            CellData("TOTAL NOMINAL", styleIndex = STYLE_HEADER),
            CellData("SUDAH DIBAYAR", styleIndex = STYLE_HEADER),
            CellData("SISA TAGIHAN", styleIndex = STYLE_HEADER),
            CellData("JATUH TEMPO", styleIndex = STYLE_HEADER),
            CellData("STATUS", styleIndex = STYLE_HEADER)
        ))

        if (debts.length() == 0) {
            rows.add(listOf(CellData("Belum ada catatan hutang atau piutang.", styleIndex = STYLE_BODY_CENTER)))
        } else {
            for (i in 0 until debts.length()) {
                val d = debts.optJSONObject(i) ?: continue
                val total = d.optDouble("amount", 0.0)
                val paid = d.optDouble("paidAmount", 0.0)
                val rem = maxOf(0.0, total - paid)
                val isPaid = d.optBoolean("isPaid", false) || d.optString("status") == "LUNAS" || rem <= 0.0
                val isPiutang = d.optString("type") == "PIUTANG"
                rows.add(listOf(
                    CellData(isNumber = true, numericValue = (i + 1).toDouble(), styleIndex = STYLE_BODY_CENTER),
                    CellData(if (isPiutang) "PIUTANG" else "HUTANG", styleIndex = STYLE_BODY_CENTER),
                    CellData(d.optString("personName", "-"), styleIndex = STYLE_BODY_BOLD),
                    CellData(isNumber = true, numericValue = total, styleIndex = STYLE_CURRENCY),
                    CellData(isNumber = true, numericValue = paid, styleIndex = STYLE_CURRENCY_INCOME),
                    CellData(isNumber = true, numericValue = rem, styleIndex = STYLE_CURRENCY_EXPENSE),
                    CellData(d.optString("dueDate", "-").ifBlank { "-" }, styleIndex = STYLE_BODY_CENTER),
                    CellData(if (isPaid) "LUNAS" else "BELUM LUNAS", styleIndex = STYLE_BODY_CENTER)
                ))
            }
        }

        rows.add(listOf(
            CellData("TOTAL SISA HUTANG BELUM LUNAS", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = unpaidHutang, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData("Sisa Piutang:", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = unpaidPiutang, styleIndex = STYLE_TOTAL_CURRENCY)
        ))

        return renderWorksheetXml(
            rows = rows,
            colWidths = listOf(7.0, 14.0, 26.0, 20.0, 20.0, 20.0, 16.0, 16.0),
            mergedRanges = listOf("A1:H1"),
            freezeRow = 2
        )
    }

    private fun buildSavingsSheet(savingsGoals: JSONArray, totalTarget: Double, totalCollected: Double): String {
        val rows = ArrayList<List<CellData>>()
        rows.add(listOf(CellData("KANTONG TABUNGAN IMPIAN & TARGET DANA", styleIndex = STYLE_TITLE)))
        rows.add(listOf(
            CellData("NO", styleIndex = STYLE_HEADER),
            CellData("NAMA TARGET", styleIndex = STYLE_HEADER),
            CellData("TARGET DANA", styleIndex = STYLE_HEADER),
            CellData("TERKUMPUL", styleIndex = STYLE_HEADER),
            CellData("KEKURANGAN", styleIndex = STYLE_HEADER),
            CellData("PROGRES (%)", styleIndex = STYLE_HEADER),
            CellData("STATUS", styleIndex = STYLE_HEADER)
        ))

        if (savingsGoals.length() == 0) {
            rows.add(listOf(CellData("Belum ada target Tabungan Impian.", styleIndex = STYLE_BODY_CENTER)))
        } else {
            for (i in 0 until savingsGoals.length()) {
                val g = savingsGoals.optJSONObject(i) ?: continue
                val target = g.optDouble("targetAmount", 0.0)
                val current = g.optDouble("currentAmount", 0.0)
                val short = maxOf(0.0, target - current)
                val pct = if (target > 0) minOf(100.0, (current / target) * 100.0) else 0.0
                rows.add(listOf(
                    CellData(isNumber = true, numericValue = (i + 1).toDouble(), styleIndex = STYLE_BODY_CENTER),
                    CellData(g.optString("title", "Target"), styleIndex = STYLE_BODY_BOLD),
                    CellData(isNumber = true, numericValue = target, styleIndex = STYLE_CURRENCY),
                    CellData(isNumber = true, numericValue = current, styleIndex = STYLE_CURRENCY_INCOME),
                    CellData(isNumber = true, numericValue = short, styleIndex = STYLE_CURRENCY_EXPENSE),
                    CellData(String.format(Locale.US, "%.1f%%", pct), styleIndex = STYLE_BODY_CENTER),
                    CellData(if (current >= target && target > 0) "TERCAPAI" else "PROSES", styleIndex = STYLE_BODY_CENTER)
                ))
            }
        }

        rows.add(listOf(
            CellData("TOTAL TABUNGAN IMPIAN", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = totalTarget, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData(isNumber = true, numericValue = totalCollected, styleIndex = STYLE_TOTAL_CURRENCY),
            CellData(isNumber = true, numericValue = maxOf(0.0, totalTarget - totalCollected), styleIndex = STYLE_TOTAL_CURRENCY),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL)
        ))

        return renderWorksheetXml(
            rows = rows,
            colWidths = listOf(7.0, 28.0, 20.0, 20.0, 20.0, 15.0, 16.0),
            mergedRanges = listOf("A1:G1"),
            freezeRow = 2
        )
    }

    private fun buildWalletsSheet(
        accounts: JSONArray,
        accountIncomeMap: Map<String, Double>,
        accountExpenseMap: Map<String, Double>,
        totalWalletBalance: Double
    ): String {
        val rows = ArrayList<List<CellData>>()
        rows.add(listOf(CellData("DAFTAR DOMPET, BANK & E-WALLET", styleIndex = STYLE_TITLE)))
        rows.add(listOf(
            CellData("NO", styleIndex = STYLE_HEADER),
            CellData("NAMA KANTONG", styleIndex = STYLE_HEADER),
            CellData("TIPE AKUN", styleIndex = STYLE_HEADER),
            CellData("NO. REKENING", styleIndex = STYLE_HEADER),
            CellData("SALDO AWAL", styleIndex = STYLE_HEADER),
            CellData("TOTAL MASUK", styleIndex = STYLE_HEADER),
            CellData("TOTAL KELUAR", styleIndex = STYLE_HEADER),
            CellData("SALDO AKHIR", styleIndex = STYLE_HEADER)
        ))

        for (i in 0 until accounts.length()) {
            val acc = accounts.optJSONObject(i) ?: continue
            val accId = acc.optString("id")
            val init = acc.optDouble("initialBalance", acc.optDouble("balance", 0.0))
            val inAmt = accountIncomeMap[accId] ?: 0.0
            val outAmt = accountExpenseMap[accId] ?: 0.0
            val cur = init + inAmt - outAmt
            rows.add(listOf(
                CellData(isNumber = true, numericValue = (i + 1).toDouble(), styleIndex = STYLE_BODY_CENTER),
                CellData(acc.optString("name", "Dompet"), styleIndex = STYLE_BODY_BOLD),
                CellData(acc.optString("type", "Cash"), styleIndex = STYLE_BODY_LEFT),
                CellData(acc.optString("accountNumber", "-").ifBlank { "-" }, styleIndex = STYLE_BODY_CENTER),
                CellData(isNumber = true, numericValue = init, styleIndex = STYLE_CURRENCY),
                CellData(isNumber = true, numericValue = inAmt, styleIndex = STYLE_CURRENCY_INCOME),
                CellData(isNumber = true, numericValue = outAmt, styleIndex = STYLE_CURRENCY_EXPENSE),
                CellData(isNumber = true, numericValue = cur, styleIndex = STYLE_CURRENCY_BOLD)
            ))
        }

        rows.add(listOf(
            CellData("TOTAL SALDO SELURUH DOMPET", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData("", styleIndex = STYLE_TOTAL_LABEL),
            CellData(isNumber = true, numericValue = totalWalletBalance, styleIndex = STYLE_TOTAL_CURRENCY)
        ))

        return renderWorksheetXml(
            rows = rows,
            colWidths = listOf(7.0, 26.0, 14.0, 18.0, 20.0, 20.0, 20.0, 22.0),
            mergedRanges = listOf("A1:H1"),
            freezeRow = 2
        )
    }

    private fun renderWorksheetXml(
        rows: List<List<CellData>>,
        colWidths: List<Double>,
        mergedRanges: List<String> = emptyList(),
        freezeRow: Int = 0
    ): String {
        val sb = StringBuilder(4096)
        sb.append("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>""")
        sb.append("""<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">""")
        if (freezeRow > 0) {
            sb.append("""<sheetViews><sheetView workbookViewId="0"><pane ySplit="$freezeRow" topLeftCell="A${freezeRow + 1}" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>""")
        }
        sb.append("""<sheetFormatPr defaultRowHeight="20"/>""")
        sb.append("<cols>")
        colWidths.forEachIndexed { i, w ->
            sb.append("""<col min="${i + 1}" max="${i + 1}" width="$w" customWidth="1"/>""")
        }
        sb.append("</cols><sheetData>")
        rows.forEachIndexed { rowIdx, cells ->
            val rNum = rowIdx + 1
            val ht = if (rNum == 1) """ ht="28" customHeight="1"""" else """ ht="20" customHeight="1""""
            sb.append("""<row r="$rNum"$ht>""")
            cells.forEachIndexed { colIdx, cell ->
                val ref = "${colLetter(colIdx)}$rNum"
                if (cell.isNumber) {
                    val vStr = if (cell.numericValue % 1.0 == 0.0) {
                        cell.numericValue.toLong().toString()
                    } else {
                        String.format(Locale.US, "%.2f", cell.numericValue)
                    }
                    sb.append("""<c r="$ref" s="${cell.styleIndex}"><v>$vStr</v></c>""")
                } else {
                    sb.append("""<c r="$ref" t="inlineStr" s="${cell.styleIndex}"><is><t>${escapeXml(cell.value)}</t></is></c>""")
                }
            }
            sb.append("</row>")
        }
        sb.append("</sheetData>")
        if (mergedRanges.isNotEmpty()) {
            sb.append("""<mergeCells count="${mergedRanges.size}">""")
            mergedRanges.forEach { range ->
                sb.append("""<mergeCell ref="$range"/>""")
            }
            sb.append("</mergeCells>")
        }
        sb.append("</worksheet>")
        return sb.toString()
    }

    private fun colLetter(index: Int): String {
        var i = index
        val sb = StringBuilder()
        while (i >= 0) {
            sb.append(('A'.code + (i % 26)).toChar())
            i = (i / 26) - 1
        }
        return sb.reverse().toString()
    }

    private fun escapeXml(input: String): String {
        val sb = StringBuilder(input.length)
        for (ch in input) {
            when (ch) {
                '&' -> sb.append("&amp;")
                '<' -> sb.append("&lt;")
                '>' -> sb.append("&gt;")
                '"' -> sb.append("&quot;")
                '\'' -> sb.append("&apos;")
                else -> {
                    val code = ch.code
                    if (code == 0x9 || code == 0xA || code == 0xD || code >= 0x20) {
                        sb.append(ch)
                    }
                }
            }
        }
        return sb.toString()
    }

    private fun formatIdrText(amount: Double): String {
        return "Rp ${String.format(Locale.forLanguageTag("id-ID"), "%,d", amount.toLong())}"
    }

    private fun buildContentTypesXml(sheetCount: Int): String {
        val overrides = (1..sheetCount).joinToString("") { idx ->
            """<Override PartName="/xl/worksheets/sheet$idx.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>"""
        }
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  $overrides
</Types>"""
    }

    private fun buildRootRelsXml(): String = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

    private fun buildWorkbookXml(sheetNames: List<String>): String {
        val sheetsXml = sheetNames.mapIndexed { idx, name ->
            """<sheet name="${escapeXml(name)}" sheetId="${idx + 1}" r:id="rId${idx + 1}"/>"""
        }.joinToString("")
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>$sheetsXml</sheets>
</workbook>"""
    }

    private fun buildWorkbookRelsXml(sheetCount: Int): String {
        val rels = (1..sheetCount).joinToString("") { idx ->
            """<Relationship Id="rId$idx" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet$idx.xml"/>"""
        }
        return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  $rels
  <Relationship Id="rId${sheetCount + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""
    }

    private fun buildStylesXml(): String = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="1">
    <numFmt numFmtId="164" formatCode="&quot;Rp&quot;\ #,##0;[Red]\-&quot;Rp&quot;\ #,##0"/>
  </numFmts>
  <fonts count="7">
    <font><sz val="10"/><color rgb="FF0F172A"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FF0F172A"/><name val="Calibri"/></font>
    <font><b/><sz val="14"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><i/><sz val="9"/><color rgb="FF64748B"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FF059669"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFDC2626"/><name val="Calibri"/></font>
  </fonts>
  <fills count="5">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0284C7"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0F172A"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE0F2FE"/></patternFill></fill>
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFCBD5E1"/></left>
      <right style="thin"><color rgb="FFCBD5E1"/></right>
      <top style="thin"><color rgb="FFCBD5E1"/></top>
      <bottom style="thin"><color rgb="FFCBD5E1"/></bottom>
    </border>
  </borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="13">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="0" fontId="1" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="0" fontId="2" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="0" fontId="4" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="5" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="6" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="164" fontId="1" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
    <xf numFmtId="0" fontId="1" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment vertical="center"/></xf>
    <xf numFmtId="164" fontId="1" fillId="4" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="right" vertical="center"/></xf>
  </cellXfs>
</styleSheet>"""
}
