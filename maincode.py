# -*- coding: utf-8 -*-
"""
Created on Sun Aug 06 16:19:38 2017

@author: wangzilong
"""
from splitextractor import *

# load a file
fname = "20160802.txt"
f = open(fname)
ft = f.read()
f.close()
print "file loaded"

# because there are only single line numbers seperate patients 
# add a spliter before each patient
s = "##@@##@@##"
def add_spliter_site(text,expression,spliter="##@@##@@##"):
    def repl(m):
        return spliter + m.group()
    return re.sub(expression,repl,text,flags=re.M)

frt = add_spliter_site(ft,r"\n\s*(\d+)\s*\n")

i = r"\n\s*(\d+)\s*\n" # ID regular expression
id_e = SimpleExtractor("id",i)

b = Bundle(frt,s,id_e) # send text with spliter to build a bundle
            
print "bundle created"

# Basic data extractors
name_e = SimpleExtractor("name","姓名\s*(\S+)\s*")
sex_e = SimpleExtractor("sex","性别\s*(\S+)\s*")
age_e = SimpleExtractor("age","年龄\s*(\S+)\s*岁")
sdate_e = SimpleExtractor("date","手术日期：\s*(\S+)\s*")

basic_data_es = [name_e,sex_e,age_e,sdate_e]

# History data extractors
hbp_d = MatchExtractor.make_disease_dict(ur"高血压")
hbp_e = MatchExtractor("hbp",hbp_d,unicode_flag = True)
    
dm_d = MatchExtractor.make_disease_dict(ur"糖尿病")
dm_e = MatchExtractor("dm",dm_d,unicode_flag = True)

hyperlipem_d = MatchExtractor.make_disease_dict(ur"高血脂")
hyperlipem_e = MatchExtractor("hyperlipem",hyperlipem_d,unicode_flag = True)

ami_d = MatchExtractor.make_disease_dict(ur"心梗")
ami_e = MatchExtractor("ami",ami_d,unicode_flag = True)

af_d = MatchExtractor.make_disease_dict(ur"房颤")
af_e = MatchExtractor("af",af_d,unicode_flag = True)

history_es = [hbp_e,dm_e,hyperlipem_e,ami_e,af_e]

# UCG extractors

ucg_re = r"心超报告单.+报告医师"
ao_e = TwoStepExtractor("ao",ucg_re,"主动脉根部内径\s*(\S+)\s*")
la_e = TwoStepExtractor("la",ucg_re,"左房内径\s*(\S+)\s*")
lvedd_e = TwoStepExtractor("lvedd",ucg_re,"左室舒张末内径\s*(\S+)\s*")
lvesd_e = TwoStepExtractor("lvesd",ucg_re,"左室收缩末内径\s*(\S+)\s*")
ivs_e = TwoStepExtractor("ivs",ucg_re,"室间隔厚度\s*(\S+)\s*")
pwt_e = TwoStepExtractor("pwt",ucg_re,"左室后壁厚度\s*(\S+)\s*")
pap_e = TwoStepExtractor("pap",ucg_re,"肺动脉收缩压\s*(\S+)\s*")
#avc TODO
lvef_e = TwoStepExtractor("lvef",ucg_re,"左室射血分数（LVEF）：\s*(\S+)\s*")
eda_e = TwoStepExtractor("E/A",ucg_re,"E/A\s*(\S+)\s*")
dt_e = TwoStepExtractor("dt",ucg_re,"DT：\s*(\S+)\s*")
speak_e = TwoStepExtractor("S-peak",ucg_re,"S波峰值：\s*(\S+)\s*")
epdap_e = TwoStepExtractor("E\'/A\'",ucg_re,"E\'/A\'\s*(\S+)\s*")
diagnosis_e = TwoStepExtractor("diag",ucg_re,"影像学 诊断: s*(.+)\n")

ucg_es = [ao_e,la_e,lvedd_e,lvesd_e,ivs_e,pwt_e,pap_e,lvef_e,eda_e,dt_e,speak_e,epdap_e,diagnosis_e]

# blood examination extractor
# extractor to obtain operation time
import time,datetime
operation_time_re = re.compile(r"手术日期：\s*(\S+)\s*")

# convert multiple syntex string to time
def strToTime(string):
    s1 = "%Y-%m-%d"
    s2 = "%Y.%m.%d"
    try:
        return datetime.datetime.strptime(string,s1)
    except:
        try:
            return datetime.datetime.strptime(string,s2)
        except:
            print string
            return None
        finally:
            pass
    finally:
        pass

# time comparing function            
def timebefore(date1,date2):
    d1 = strToTime(date1)
    d2 = strToTime(date2)
    if d2<=d1:
        return True
    else:
        return False

def timeafter(date1,date2):
    return not timebefore(date1,date2)
    
compare_pattern = r"\s*(\S+)\s*{}(?:（急）)?\s+([0-9.]+)\s+"

ctnt_re = compare_pattern.format("心肌肌钙蛋白T")
pre_ctnt_e = CompareExtractor("pre_ctnt",operation_time_re,ctnt_re,timebefore) 

bnp_re = compare_pattern.format("氨基末端利钠肽前体")
pre_bnp_e = CompareExtractor("pre_bnp",operation_time_re,bnp_re,timebefore) 

ck_re = compare_pattern.format("肌酸激酶")
pre_ck_e = CompareExtractor("pre_ck",operation_time_re,ck_re,timebefore) 

ckmb_re = compare_pattern.format("肌酸激酶MB亚型")
pre_ckmb_e = CompareExtractor("pre_ckmb",operation_time_re,ckmb_re,timebefore) 

cr_re = compare_pattern.format("肌酐")
pre_cr_e = CompareExtractor("pre_cr",operation_time_re,cr_re,timebefore) 

pre_exam_es = [pre_ctnt_e,pre_bnp_e,pre_ck_e,pre_ckmb_e,pre_cr_e]


post_ctnt_e = CompareExtractor("post_ctnt",operation_time_re,ctnt_re,timeafter) 
post_bnp_e = CompareExtractor("post_bnp",operation_time_re,bnp_re,timeafter) 
post_ck_e = CompareExtractor("post_ck",operation_time_re,ck_re,timeafter) 
post_ckmb_e = CompareExtractor("post_ckmb",operation_time_re,ckmb_re,timeafter) 
post_cr_e = CompareExtractor("post_cr",operation_time_re,cr_re,timeafter) 

post_exam_es = [post_ctnt_e,post_bnp_e,post_ck_e,post_ckmb_e,post_cr_e]


simple_pattern = r"\s*\S+\s*{}(?:（急）)?\s+([0-9.]+)\s+"
exam_tc_e = SimpleExtractor("tc",simple_pattern.format("总胆固醇"))
exam_tg_e = SimpleExtractor("tg",simple_pattern.format("甘油三酯"))
exam_HDL_e = SimpleExtractor("HDL",simple_pattern.format("高密度脂蛋白胆固醇"))
exam_LDL_e = SimpleExtractor("LDL",simple_pattern.format("低密度脂蛋白胆固醇"))
exam_lpa_e = SimpleExtractor("lpa",simple_pattern.format("载脂蛋白A-I"))
exam_g_e = SimpleExtractor("G",simple_pattern.format("葡萄糖"))
exam_HbA1c_e = SimpleExtractor("HbA1c",simple_pattern.format("糖化血红蛋白"))
exam_HB_e = SimpleExtractor("HB",simple_pattern.format("血红蛋白"))
exam_PLT_e = SimpleExtractor("PLT",simple_pattern.format("血小板计数"))

exam_es = [exam_tc_e,exam_tg_e,exam_HDL_e,exam_LDL_e,exam_lpa_e,
    exam_g_e,exam_HbA1c_e,exam_HB_e,exam_PLT_e]

# add all extractors
b.add_extractors(basic_data_es)
b.add_extractors(history_es)
b.add_extractors(ucg_es)
b.add_extractors(pre_exam_es)
b.add_extractors(post_exam_es)
b.add_extractors(exam_es)

exd = b.extract()
#print exd
fout_name = fname.split('.')[0]+".csv"
fout = open(fout_name,'w')
#fout.write(exd.decode("UTF-8").encode("GB18030"))
fout.write(exd)
fout.close()

#import cProfile
#cProfile.run("b.extract()")
