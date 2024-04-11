import openpyxl
from datetime import datetime, timedelta
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker


def convertWeekday(dateNum: int):
    if dateNum == 0:
        return "月"
    elif dateNum == 1:
        return "火"
    elif dateNum == 2:
        return "水"
    elif dateNum == 3:
        return "木"
    elif dateNum == 4:
        return "金"
    elif dateNum == 5:
        return "土"
    elif dateNum == 6:
        return "日"
    else:
        return "error"


# Excelファイルを開く
wb = openpyxl.load_workbook('autogen.xlsx')

# アクティブなシートを選択する
sheet = wb.active

# 今日の日付を取得する
today = datetime.now()

baseCellNumList = [18, 51]

for x in baseCellNumList:
    # 指定のセルに今日の日付から1週間分の日付を書き込む
    for i in range(5):
        date = today + timedelta(days=i+7)
        day = convertWeekday(int(i))
        sheet['A' + str(i*3+x)] = date.strftime("%m月　%d日") + "（" + day + "）"


# 変更を保存する
wb.save('your_file.xlsx')
