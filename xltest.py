import xlwt, os, xlrd
from xlutils import copy
from PIL import Image
__author__ = 'Michael'
size_factor=.60

rb = xlrd.open_workbook("C:/Users/Michael/Desktop/template2.xls", formatting_info=True)
ws0 = rb.sheet_by_index(0)
wb = copy
xx=wb.copy(rb)
ws = xx.get_sheet(0)

#ws0.write(0, 2, "chg wid: none")
img = Image.open('rendered_thresh_zstat1.png')
(width,height)=img.size
new_width=int(width*size_factor)
new_height=int(height*size_factor)
x=img.resize((new_width,new_height))
x.save("rendered_thresh_zstat1.bmp")

ws.insert_bitmap("rendered_thresh_zstat1.bmp",1,0)
ws.insert_bitmap("rendered_thresh_zstat1.bmp",1,8)
xx.save("C:/Users/Michael/Desktop/test.xls")

