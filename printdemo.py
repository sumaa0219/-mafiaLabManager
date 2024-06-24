import cups

# CUPS接続の確立
conn = cups.Connection()

# プリンター名とデバイスURIの指定
printer_name = "LP_S7160"
device_uri = "lpd://172.24.6.242/"
ppd_path = "/path/to/driver.ppd"

# プリンターを手動で追加
try:
    conn.addPrinter(name=printer_name,
                    ppdname=ppd_path,
                    info="LP-S7160",
                    location="")

    # プリンターオプションを設定
    conn.addPrinterOption(printer_name, "device-uri", device_uri)
    conn.addPrinterOption(
        printer_name, "printer-make-and-model", "EPSON LP-S7160")

    # プリンターを有効にしてジョブを受け入れる
    conn.enablePrinter(printer_name)
    conn.acceptJobs(printer_name)

    # プリンターリストの取得と表示
    printers = conn.getPrinters()
    print(printers.keys())

except cups.IPPError as e:
    print(f"IPPError: {e}")
except Exception as e:
    print(f"Error: {e}")
