import cups
import time

mainPrinter = "LP-S7160"


def print_pdf(printer_name, pdf_path, duplex=True):
    conn = cups.Connection()
    printers = conn.getPrinters()
    if printer_name not in printers:
        raise ValueError(f"プリンター '{printer_name}' が見つかりません")

    options = {
        'media': 'A4',
        'fit-to-page': 'true'
    }
    if duplex:
        options['sides'] = 'two-sided-long-edge'

    job_id = conn.printFile(printer_name, pdf_path, "Flask Print Job", options)
    jpb_status = conn.getJobAttributes(job_id)
    while jpb_status['job-state'] < 9:
        time.sleep(1)
        jpb_status = conn.getJobAttributes(job_id)

        return job_id


if __name__ == "__main__":
    # 使用するプリンターの名前と印刷するPDFファイルのパスを指定
    printer_name = mainPrinter
    pdf_path = "./aaaaa.pdf"

    print(print_pdf(printer_name, pdf_path))
    # conn = cups.Connection()
    # printers = conn.getPrinters()
    # print(printers[mainPrinter])
