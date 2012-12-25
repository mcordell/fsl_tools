__author__ = 'michael'
from excel_results import excel_results



ME_folders=['C:/Users/Michael/Dropbox/Leptin/test/ppi_hyp_a_cope1.gfeat']
fe_cope_names=["wt-loss food",
               "wt-loss nonfood",
               "wt-loss both",
               "leptin food",
               "leptin nonfood",
               "leptin both",
               "leptin wt-loss food",
               "leptin wt-loss nonfood",
               "leptin wt-loss both",
               "wt-loss food neg",
               "wt-loss nonfood neg",
               "wt-loss both neg",
               "leptin food neg",
               "leptin nonfood neg",
               "leptin both neg",
               "leptin wt-loss food neg",
               "letpin wt-loss nonfood neg",
               "leptin wt-loss both neg",
               "group mean"]
fe_cope_names=[
                "WL F",
                "WL NF",
                "Lep F",
                "Lep NF",
                "L WT F",
                "L WT NF",
                "All F > NF",
                "All NF > F",
                "Wt loss F > NF",
                "Wt Loss NF > F",
                "Lep F > NF",
                "Lep NF > F",
                "Lep-WL F > NF ",
                "Lep-WL NF > F",
                "Lep F > WL F",
                "WL F > Lep F",
                "LWL F > WL F",
                "WL F > LWL F",
                "Lep F > LWL F",
                "LWL F > Lep F",
                "Lep NF > WL NF",
                "WL NF > Lep NF",
                "LWL NF > WL NF",
                "WL NF > LWL NF",
                "Lep NF > LWL NF",
                "LWL NF > Lep NF"]

fe_2=dict()
count=1
for item in fe_cope_names:
    fe_2[str(count)]=item
    count +=1
first_cope_names=dict()
first_cope_names['1']='PSY'
first_cope_names['2']='PHYS'
first_cope_names['3']='PPI'
excel_output_path='a2_mr.xls'
template_path='template3.xls'
excel=excel_results(fe_cope_names,first_cope_names, ME_folders, template_path,excel_output_path)
excel.main()