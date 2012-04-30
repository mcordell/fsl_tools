__author__ = 'Michael'
import xlwt, os, xlrd, re
from xlutils import copy
from PIL import Image

class excel_results:
    def __init__(self, higher_level_names, lower_level_names, ME_paths, template_path, excel_outpath):
        self.higher_level_names=higher_level_names
        self.lower_level_names=lower_level_names
        self.ME_paths=ME_paths
        self.template_path=template_path
        self.excel_outpath=excel_outpath
        self.scale_factor=.65
        self.vertical_move=27
        self.horizontal_move=8

    def determine_cope(self,cope_name):
        copenumber_match=re.search("cope\d+",cope_name)
        if copenumber_match:
            number_match=re.search("\d+",copenumber_match.group(0))
            if number_match:
                cope_number=number_match.group(0)
        if cope_number:
            return cope_number


    def write_row(self,row_name,vertical_start,horizontal_start,me_root_path,worksheet):
        files_list=os.listdir(me_root_path)
        worksheet.write(vertical_start-1,horizontal_start,row_name)
        for cope_name in files_list:
            copenumber_match=re.search("cope\d+",cope_name)
            if copenumber_match:
                cope_dir=os.path.join(me_root_path,cope_name)
                if os.path.isdir(cope_dir):
                    rendered_thresh=os.path.join(cope_dir,"rendered_thresh_zstat1.png")
                    if os.path.isfile(rendered_thresh):
                        img = Image.open(rendered_thresh)
                        (width,height)=img.size
                        new_width=int(width*self.scale_factor)
                        new_height=int(height*self.scale_factor)
                        resized=img.resize((new_width,new_height))
                        resized.save("resized_temp.bmp")
                        worksheet.insert_bitmap("resized_temp.bmp",vertical_start,horizontal_start)
                        os.remove("resized_temp.bmp")
                horizontal_start+=self.horizontal_move

        


    def main(self):
        #open template file
        rb = xlrd.open_workbook(self.template_path, formatting_info=True)
        #ws0 = rb.sheet_by_index(0)
        wb= copy.copy(rb)
        ws = wb.get_sheet(0)
        vert_start=2
        horz_start=0
        for me in self.ME_paths:
            cope=self.determine_cope(me)
            if cope:
                horz_start=0
                name=self.lower_level_names[cope]
                self.write_row(name,vert_start,horz_start,me,ws)
                vert_start+=self.vertical_move
        wb.save(self.excel_outpath)


    if __name__ == "__main__":
        main()
