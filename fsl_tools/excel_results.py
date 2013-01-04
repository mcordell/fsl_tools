__author__ = 'Michael'
import  os
import xlrd
import re
from xlutils import copy
from PIL import Image

class ExcelResults:
    def __init__(self,col_labels,row_labels, ME_paths,excel_outpath,configuration, scale_factor=.65, 
                 vertical_move=27, horizontal_move=8):
        self.col_labels=col_labels
        self.row_labels=row_labels
        self.ME_paths=ME_paths
        self.configuration=configuration
        self.template_path=configuration.template_path
        self.excel_outpath=excel_outpath
        self.scale_factor=scale_factor
        self.vertical_move=vertical_move
        self.horizontal_move=horizontal_move
        self.cope_match_pattern=configuration.cope_pattern
        self.LABEL_POS_START_COL=3

    def determine_cope(self,in_string):
        #TODO could be moved somewhereelse
        """
        Helper function for determining a cope # from a give string "in_string" 
        
        Attributes:
            in_string - the string hopefully containing a cope number/pattern

        Returns:
            cope_number - the number of the cope determined from the in_string
        """
        cope_number_match=re.search(self.cope_match_pattern,in_string)
        if cope_number_match:
            number_match=re.search("\d+",cope_number_match.group(0))
            if number_match:
                cope_number=number_match.group(0)
        if cope_number:
            return cope_number

    def intialize_workbook(self):
        """
            Loads the template excel workbook and writes the column labels
        """
        rb = xlrd.open_workbook(self.template_path, formatting_info=True)
        wb=copy.copy(rb)
        #TODO this assumes that we are only working on the "first" sheet
        ws = wb.get_sheet(0)
        label_pos=self.LABEL_POS_START_COL
        count=1
        while count <= len(self.col_labels):
            if label_pos < 256:
                ws.write(0,label_pos,self.col_labels[str(count)].strip('\"'))
                label_pos+=self.horizontal_move
            count+=1
        self.wb=wb
        self.ws=ws

    def write_all_rows(self):
        """
            Writes all mixed effects as invidual rows to this ExcelResults worksheet
        """
        organized_MEs=self.organize_ME_paths()
        vert_start=2
        horz_start=0
        for ind in range(1,len(organized_MEs)+1):
            i=str(ind)
            horz_start=0
            try:
                name=self.row_labels[i]
            except KeyError:
                name=''
                print "Higher level Mixed effects not found in lower level copes. Mismatch?"
            me=organized_MEs[i]
            self.write_row(name,vert_start,horz_start,me,self.ws)
            vert_start+=self.vertical_move


    def organize_ME_paths(self):
        """
            method for sorting mixed effects paths within this ExcelResults object by cope number

            Returns:
                organized_MEs= a dict where the key is the cope number, and the path is the value
        """
        organized_MEs=dict()
        for me in self.ME_paths:
            cope=self.determine_cope(me)
            if cope:
                organized_MEs[cope]=me
        return organized_MEs

    def main(self):
        self.intialize_workbook()
        self.write_all_rows()
        self.wb.save(self.excel_outpath)

    def write_row(self,row_name,vertical_start,horizontal_start,me_root_path,worksheet):
        """  
            Searches through a mixed effects directory for result images and writes them to a row
            within a worksheet. The image scaling in specified by the scale_factor variable of 
            ExcelResults object. Similarly, the horizontal move factor is the number of cells 
            to move over for each image.
            
            Attributes:
                row_name - the title written above each image in the row
                horizontal_start - the column number where the first image is inserted within the worksheet
                vertical_start - the row number where the first image is inserted within the worksheet
                me_root_path - the path to the mixed effects directory where the results are located
                worksheet - the worksheet that is written
       """
        files_list=os.listdir(me_root_path)
        for cope_name in files_list:
            copenumber_match=re.search(self.configuration.cope_pattern,cope_name)
            if copenumber_match:
                cope_dir=os.path.join(me_root_path,cope_name)
                if os.path.isdir(cope_dir):
                    worksheet.write(vertical_start-1,horizontal_start,row_name)
                    rendered_thresh=os.path.join(cope_dir,"rendered_thresh_zstat1.png")
                    report_poststats=os.path.join(cope_dir,"report_poststats.html")
                    cluster_max_path=os.path.join(cope_dir,"cluster_zstat1_std.txt")
                    if os.path.isfile(rendered_thresh) and os.path.isfile(cluster_max_path):
                        with file(cluster_max_path,'r') as cluster_file:
                            cluster_lines=cluster_file.readlines()
                        if len(cluster_lines) > 1:
                            img = Image.open(rendered_thresh)
                            (width,height)=img.size
                            new_width=int(width*self.scale_factor)
                            new_height=int(height*self.scale_factor)
                            cope_value_match=re.search("\d+",copenumber_match.group(0))
                            fe_cope_num=int(cope_value_match.group(0))
                            horizontal_count_move=(fe_cope_num-1)*self.horizontal_move
                            resized=img.resize((new_width,new_height))
                            resized.save("resized_temp.bmp")
                            worksheet.insert_bitmap("resized_temp.bmp",vertical_start,horizontal_start+horizontal_count_move)
                            halfway=((fe_cope_num-1)*self.horizontal_move)+(.5*self.horizontal_move)
                            halfway=int(halfway)
                            z_value=self.get_z_value(report_poststats)
                            resized=img.resize((new_width,new_height))
                            worksheet.write(vertical_start-1,horizontal_start+halfway,z_value.rstrip())
                            os.remove("resized_temp.bmp")

    def get_z_value(self,report_path):
        """
            Searches post stats report to find the max z-value

            Attributes:
                report_path - path to the report post states to be parsed

            Returns:
                z_value - z value from the report_path
        """
        with open(report_path, 'r') as f:
            lines=f.readlines()
        for i in range(0,len(lines)):
            line=lines[i]
            line_match=re.search("<IMG BORDER=0 SRC=.ramp.gif>",line)
            if line_match:
                z_value_line=lines[i+1]
                z_value=z_value_line.rstrip()
                return z_value

    if __name__ == "__main__":
        main()
