from openpyxl import Workbook
from openpyxl.drawing.line import LineShape
from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor

# 新しいワークブックを作成
wb = Workbook()

# 新しいシートを作成
ws = wb.active

# 線を作成
line = LineShape(start=(0, 0), end=(200, 200), width=2)

# 矢印を追加
line.arrow = "triangle"  # 終点に三角形の矢印を追加

# 矢印を配置するセルの位置を指定
anchor = OneCellAnchor(anchorCell=ws['C3'])

# シェイプをアンカーに追加
anchor._move(line, "C3")

# ワークシートにアンカーを追加
ws._add_drawing(anchor)

# Excelファイルを保存
wb.save('example_with_arrow.xlsx')
