package com.example

import com.example.export.ExcelXlsxExporter
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.ByteArrayInputStream
import java.util.zip.ZipInputStream

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [36])
class ExcelXlsxExporterTest {

  @Test
  fun `builds valid multi-sheet ooxml xlsx workbook with rupiah styling and xml escaping`() {
    val samplePayload = """
      {
        "userProfile": { "name": "Bagas Pratama", "username": "bagas240" },
        "accounts": [
          { "id": "acc_1", "name": "BCA Utama", "type": "Bank", "accountNumber": "123456", "initialBalance": 5000000 }
        ],
        "transactions": [
          { "id": "tx_1", "type": "INCOME", "amount": 2500000, "category": "gaji", "accountId": "acc_1", "date": "2026-03-01", "notes": "Bonus & Gaji" },
          { "id": "tx_2", "type": "EXPENSE", "amount": 125000, "category": "makan", "accountId": "acc_1", "date": "2026-03-02", "notes": "Belanja <Indomaret>", "isReceiptScan": true }
        ],
        "savingsGoals": [
          { "id": "goal_1", "title": "Dana Darurat", "targetAmount": 10000000, "currentAmount": 3500000 }
        ],
        "debts": [
          { "id": "debt_1", "type": "PIUTANG", "personName": "Rizal", "amount": 500000, "paidAmount": 100000, "dueDate": "2026-04-01", "isPaid": false }
        ],
        "categoryLabels": {
          "gaji": "Gaji & Bonus",
          "makan": "Makan & Minum"
        }
      }
    """.trimIndent()

    val xlsxBytes = ExcelXlsxExporter.buildWorkbook(samplePayload)
    assertTrue("Expected valid PKZIP signature", xlsxBytes.size > 500 && xlsxBytes[0] == 'P'.code.toByte() && xlsxBytes[1] == 'K'.code.toByte())

    val entries = mutableMapOf<String, String>()
    ZipInputStream(ByteArrayInputStream(xlsxBytes)).use { zis ->
      var entry = zis.nextEntry
      while (entry != null) {
        entries[entry.name] = zis.readBytes().toString(Charsets.UTF_8)
        zis.closeEntry()
        entry = zis.nextEntry
      }
    }

    val expectedEntries = listOf(
      "[Content_Types].xml",
      "_rels/.rels",
      "xl/workbook.xml",
      "xl/_rels/workbook.xml.rels",
      "xl/styles.xml",
      "xl/worksheets/sheet1.xml",
      "xl/worksheets/sheet2.xml",
      "xl/worksheets/sheet3.xml",
      "xl/worksheets/sheet4.xml",
      "xl/worksheets/sheet5.xml"
    )
    expectedEntries.forEach { name ->
      assertTrue("Missing OOXML archive entry: $name", entries.containsKey(name))
    }

    val workbookXml = entries.getValue("xl/workbook.xml")
    assertTrue(workbookXml.contains("Ringkasan Keuangan"))
    assertTrue(workbookXml.contains("Mutasi Transaksi"))
    assertTrue(workbookXml.contains("Hutang &amp; Piutang"))
    assertTrue(workbookXml.contains("Tabungan Impian"))
    assertTrue(workbookXml.contains("Daftar Dompet"))

    val stylesXml = entries.getValue("xl/styles.xml")
    assertTrue("Expected Rupiah custom number format", stylesXml.contains("&quot;Rp&quot;"))

    val sheet2Xml = entries.getValue("xl/worksheets/sheet2.xml")
    assertTrue("Expected XML escaped note", sheet2Xml.contains("Belanja &lt;Indomaret&gt;"))
    assertTrue("Expected receipt source tag", sheet2Xml.contains("Scan Struk"))
    assertFalse("Unescaped angle brackets should not appear inside text", sheet2Xml.contains("<Indomaret>"))
  }
}
