from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A4
from datetime import datetime, timedelta
from reportlab.lib.colors import toColor


def edit_letter_on_pdf(cc: canvas.Canvas, text, x, y, font_size=12, font="Helvetica", color="black"):
    """PDFに文字を書き込む関数"""
    cc.setFont(font, font_size)
    cc.setFillColor(toColor(color))
    cc.drawRightString(x=mm_to_points(x), y=mm_to_points(y), text=text)
    return cc


def mm_to_points(mm):
    """ミリメートルをポイントに変換する関数"""
    points = mm / 25.4 * 72
    return points


def get_week_dates(year, month, day):
    """指定された日付から1週間後の各曜日の日付を取得する関数"""
    start_date = datetime(year, month, day)
    weekday = start_date.weekday()
    monday_date = start_date - timedelta(days=weekday)
    next_week_monday = monday_date + timedelta(days=7)
    week_dates = [next_week_monday + timedelta(days=i) for i in range(7)]

    return [[date.strftime("%-m"), date.strftime("%-d")] for date in week_dates]


def gen_pdf(today, option):
    """PDFを生成する関数"""
    input_file = f'./roomReserve/施設使用願{option}.pdf'
    pages = PdfReader(input_file, decompress=False).pages
    output_file_name = today.strftime("%Y-%m-%d")
    if option == 0:
        optionName = "Normal"
    elif option == 1:
        optionName = "Vacation"
    cc = canvas.Canvas(f"./out/{output_file_name}-{optionName}.pdf",
                       pagesize=portrait(A4))
    pp = pagexobj(pages[0])
    cc.doForm(makerl(cc, pp))
    # cc.drawString(x=10, y=10, text="Hello, World")

    # 今日の日付を追加
    # x_base = 123
    # y_base = 272.3
    # for text in [today.strftime("%Y"), today.strftime("%m"), today.strftime("%d")]:
    #     cc = edit_letter_on_pdf(cc, text, x_base, y_base, 10)
    #     x_base += 18

    # 1週間後の日付を追加

    after_week_dates = get_week_dates(
        today.year, today.month, today.day)
    x_base = 31.5
    y_base = 197.7
    for date in after_week_dates:
        for text in date:
            cc = edit_letter_on_pdf(cc, text, x_base, y_base, 10)
            x_base += 7.5
        x_base += 24.5
        cc = edit_letter_on_pdf(cc, "560", x_base, y_base, 10)

        y_base -= 9.2
        x_base = 31.5

    y_base = 96.6
    for date in after_week_dates:
        for text in date:
            cc = edit_letter_on_pdf(cc, text, x_base, y_base, 10)
            x_base += 7.7
        x_base += 24.5
        cc = edit_letter_on_pdf(cc, "560", x_base, y_base, 10)
        y_base -= 9.85
        x_base = 31.5

    cc.showPage()
    cc.save()
    return f"{output_file_name}.pdf"


print(gen_pdf(datetime.now(), 1))
