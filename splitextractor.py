# -*- coding: utf-8 -*-
"""
Created on Sun Aug 06 16:13:36 2017

@author: wangzilong
"""
import re

class Extractor():
    
    def __init__(self):
        self.name = ""
        
    def extract(self,text):
        raise NotImplementedError
        
        

class SimpleExtractor(Extractor):
    
    """A regular expression with a group 1 to output"""
    def __init__(self,name,regular_expression,default_val="DK"):
        self.name = name
        self.expression = regular_expression
        self.dv = default_val
        
    def extract(self,text):
        m = re.search(self.expression,text)
        if m and m.groups():
            return m.group(1)
        else:
            return self.dv



class MatchExtractor(Extractor):
    
    @staticmethod
    def make_disease_dict(disease_name):
        d = {ur"否认[\u4e00-\u9fa5、]+{}":"无",
             u"有{}":"有",
             u"无{}":"无",
             u"否认{}":"无",
             u"{}\S{{,8}}年":"有",
             u"{}病史\S{{,8}}年":"有"}
        dn = {}
        for k,v in d.iteritems():
            dn[k.format(disease_name)] = v
        return dn
    
    def __init__(self,name,match_dict,defaut_val="DK",unicode_flag = False):
        self.name = name
        self.match_dict = match_dict
        self.dv = defaut_val
        self.unicode_flag = unicode_flag
        
    def extract(self,text):
        if self.unicode_flag:
            text = text.decode("utf-8") #TODO
        for k,v in self.match_dict.iteritems():
            if re.search(k,text):
                return v
        return self.dv



class CompareExtractor(Extractor):
    
    """
    compare_standard : RE repression to find standard to compare in group 1
    regular_expression : group(1) for compare, group(2) is content
    compare_fun : retrun True if it meets the requirement
    """
    
    def __init__(self,name,compare_standard,regular_expression,compare_fun,defaut_val = "DK"):
        self.name =name
        self.compare_standard = compare_standard
        self.regular_expression = re.compile(regular_expression)
        self.compare_fun = compare_fun
        self.dv = defaut_val
        
    def extract(self,text):
        std = re.search(self.compare_standard,text)
        if std == None :
            return self.dv
        stdstr = std.group(1)
        matches = re.findall(self.regular_expression,text)
        #matches = re.finditer(self.regular_expression,text)
        for compare,value in matches:
            #compare,value = m.groups()
            if self.compare_fun(stdstr,compare):
                return value
        return self.dv
            
            

class TwoStepExtractor(Extractor):
    def __init__(self,name,first_re,second_re,defaut_val="DK"):
        self.name = name
        self.first_re = first_re
        self.second_re = second_re
        self.dv = defaut_val
    def extract(self,text):
        sub = re.search(self.first_re,text,flags=re.DOTALL)
        if sub:
            sub_string = sub.group(0)
            m = re.search(self.second_re, sub_string)
            if m and m.groups():
                return m.group(1)
            else:
                return self.dv
        else:
            return self.dv
        
    
class Grain:
    
    def __init__(self,id_extractor,text):
        self.identity = id_extractor.extract(text)
        self.text = text



class Bundle: 
    sep = ","
    nl = "\n"
    
    def __init__(self,text,spliter,id_extractor):
        """initialize a text as bundle and split it into grains with spliter"""
        self.grains = {}
        self.extractors = []
        splited_text = re.split(spliter,text)
        for text_block in splited_text:
            if re.match("^\s*$",text_block):
                continue
            else:
                g = Grain(id_extractor,text_block)
                # print g.identity
                self.grains[g.identity] = g
                
    def add_extractor(self,e):
        self.extractors.append(e)
        
    def add_extractors(self,es):
        self.extractors.extend(es)
        
    def extract(self):
        s = ""
        titles = "id"+ self.sep + self.sep.join([e.name for e in self.extractors])
        print "Start sxtracting"
        i = 0
        for identity,g in self.grains.iteritems():
            s = s+ identity + self.sep + \
                self.sep.join([e.extract(g.text) for e in self.extractors]) + \
                self.nl
            i += 1
            if i%5==0:
                print "{} files are extracted sucessfully".format(i)
        return titles + self.nl + s


