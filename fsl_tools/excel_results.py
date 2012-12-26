__author__ = 'Michael'
import  os, xlrd, re
from xlutils import copy
from PIL import Image

def get_z_value(report_path):
    with open(report_path, 'r') as f:
        lines=f.readlines()
    for i in range(0,len(lines)):
        line=lines[i]
        line_match=re.search("<IMG BORDER=0 SRC=.ramp.gif>",line)
        if line_match:
            return lines[i+1]

def write_row(row_name,vertical_start,horizontal_start,me_root_path,worksheet,horizontal_move,scale_factor):
    """ Writes a row in a given worksheet, searching though a me_root_path, using
        the results images within that root directory.row_name is written above each image in the row
        Row writing starts at horiztonal/vertical cell position within the worksheet. Horizontal position
        moves with the horiztonal move
    """
    files_list=os.listdir(me_root_path)
    for cope_name in files_list:
        copenumber_match=re.search("cope\d+",cope_name)
        if copenumber_match:
            cope_dir=os.path.join(me_root_path,cope_name)
            if os.path.isdir(cope_dir):
                worksheet.write(vertical_start-1,horizontal_start,row_name)
                rendered_thresh=os.path.join(cope_dir,"rendered_thresh_zstat1.png")
                report_poststats=os.path.join(cope_dir,"report_poststats.html")
                cluster_max_path=os.path.join(cope_dir,"cluster_zstat1_std.txt")
                #if os.path.isfile(rendered_thresh):
                if os.path.isfile(rendered_thresh) and os.path.isfile(cluster_max_path):
                    with file(cluster_max_path,'r') as cluster_file:
                        cluster_lines= cluster_file.readlines()
                    if len(cluster_lines) > 1:
                        img = Image.open(rendered_thresh)
                        (width,height)=img.size
                        new_width=int(width*scale_factor)
                        new_height=int(height*scale_factor)
                        cope_value_match=re.search("\d+",copenumber_match.group(0))
                        fe_cope_num=int(cope_value_match.group(0))
                        horizontal_count_move=(fe_cope_num-1)*horizontal_move
                        resized=img.resize((new_width,new_height))
                        resized.save("resized_temp.bmp")
                        worksheet.insert_bitmap("resized_temp.bmp",vertical_start,horizontal_start+horizontal_count_move)
                        halfway=((fe_cope_num-1)*horizontal_move)+(.5*horizontal_move)
                        halfway=int(halfway)
                        z=get_z_value(report_poststats)
                        resized=img.resize((new_width,new_height))
                        worksheet.write(vertical_start-1,horizontal_start+halfway,z.rstrip())
                        os.remove("resized_temp.bmp")



class ExcelResults:
    def __init__(self,col_labels,row_labels, ME_paths,excel_outpath,configuration, scale_factor=.65, 
                 vertical_move=27, horizontal_move=8):
        self.col_labels=col_labels
        self.row_labels=row_labels
        self.ME_paths=ME_paths
        self.template_path=configuration.template_path
        self.excel_outpath=excel_outpath
        self.scale_factor=scale_factor
        self.vertical_move=vertical_move
        self.horizontal_move=horizontal_move
        self.cope_match_pattern=configuration.cope_pattern

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

    def main(self):
        #open template file
        """

        """
        rb = xlrd.open_workbook(self.template_path, formatting_info=True)
        #ws0 = rb.sheet_by_index(0)
        wb= copy.copy(rb)
        ws = wb.get_sheet(0)
        label_pos=3
        label_move=8
        count=1
        while count <= len(self.col_labels):
            if label_pos < 256:
                ws.write(0,label_pos,self.col_labels[str(count)].strip('\"'))
                label_pos+=label_move
            count+=1
        wb.save('test.xls')


        vert_start=2
        #noinspection PyUnusedLocal
        horz_start=0
        organize_MEs=dict()
        for me in self.ME_paths:
            cope=self.determine_cope(me)
            if cope:
                organize_MEs[cope]=me
        for ind in range(1,len(organize_MEs)+1):
                i=str(ind)
                horz_start=0
                try:
                    name=self.row_labels[i]
                except KeyError:
                    name=''
                    print "Higher level Mixed effects not found in lower level copes. Mismatch?"
                me=organize_MEs[i]
                write_row(name,vert_start,horz_start,me,ws,self.horizontal_move,self.scale_factor)
                vert_start+=self.vertical_move
        wb.save(self.excel_outpath)


    if __name__ == "__main__":
        main()
