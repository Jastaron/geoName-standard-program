import numpy as np
import pandas as pd
from pypinyin import lazy_pinyin as lpy, Style
from pywubi import wubi as wb
import jieba
import pymysql
import logging
from tkinter import filedialog
from time import time

# 关闭jieba log输出
jieba.setLogLevel(logging.INFO)
jieba.load_userdict(r'../Resource/All_Abbr.txt')

def fin(strokes_path):
    # 如果返回 0, 则也是在unicode中不存在kTotalStrokes字段
    strokes = []
    with open(strokes_path, 'r') as fr:
        for line in fr:
            strokes.append(int(line.strip()))
    return strokes

def get_stroke(c,strokes):
    unicode_ = ord(c)
    if 13312 <= unicode_ <= 64045:
        return strokes[unicode_ - 13312]
    elif 131072 <= unicode_ <= 194998:
        return strokes[unicode_ - 80338]
    else:
        print("c should be a CJK char, or not have stroke in unihan data.")
        # can also return 0

PyIniDict = {
    'b':'1', 'p':'2', 'm':'3', 'f':'4', 'd':'5', 't':'6', 'n':'7', 'l':'7',
    'g':'8', 'k':'9', 'h':'A', 'j':'B', 'q':'C', 'x':'D', 'zh':'E', 'ch':'F',
    'sh':'G', 'r':'H', 'z':'E', 'c':'F', 's':'G', 'y':'I', 'w':'J', '':'I'
}
PyFinalDict = {
    'a':'1', 'o':'2', 'e':'3', 'i':'4', 'u':'5', 'v':'5', 'yu':'5', 'ai':'6',
    'ei':'7', 'ui':'8', 'ao':'9', 'ou':'A', 'iu':'B', 'ie':'C', 'ye':'C',
    've':'D', 'yue':'D', 'ue':'D', 'er':'E', 'an':'F', 'en':'G', 'in':'H',
    'un':'I', 'ven':'J', 'yun':'J', 'ang':'F', 'eng':'I', 'ing':'H',
    'ong':'K', 'yin':'H','you':'A', 'uang':'L', 'iang':'M', 'iong':'N',
    'ua':'O', 'wen':'I', 'yan':'P', 'ian':'P', 'yang':'M', 'yong':'N',
    'uo':'Q', 'wo':'Q', 'ia':'R', 'ya':'R', 'uan':'S', 'wan':'S', 'wa':'O',
    'iao':'T','yao':'T','yuan':'S','wu':'5','yi':'4','ying':'H','on':'K',
    'ig':'H','wai':'6', 'wang': 'L', 'wei': '8', 'og': 'A'
}
strokesDict = {
    0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',
    10:'a',11:'b',12:'c',13:'d',14:'e',15:'f',16:'g',17:'h',18:'i',19:'j',
    20:'k',21:'l',22:'m',23:'n',24:'o',25:'p',26:'q',27:'r',28:'s',29:'t',
    30:'u',31:'v',32:'w',33:'x',34:'y',35:'z',36:'A',37:'B',38:'C',39:'D',
    40:'E',41:'F',42:'G',43:'H',44:'I',45:'J',46:'K',47:'L',48:'M',49:'N',
    50:'O',51:'P',52:'Q',53:'R',54:'S',55:'T',56:'U',57:'V',58:'W',59:'X',
    60:'Y',61:'Z'
}
city_error = {
    '达县':'达州市',
    '渡口':'攀枝花市'
}
config = {
    "host": "localhost",  # 一般为localhost
    "user": "root",  # 一般为root
    "password": "20030415",  # 一般为root
    "database": "sc_cq_specimen_normalization"  # 选择您的数据库
}
provinces = ['四川','重庆']
db = pymysql.connect(**config)

# 所有的资源
total_locations = pd.read_csv(r'../Resource/SC_CQ_total_load.csv')
history_image = pd.read_csv(r'../Resource/history_final.csv')
county_abbr_file = pd.read_csv(r'../Resource/county_abbr.csv')
strokes = fin(r'../Resource/strokes.txt')

totalDict = {}
layerDict = {'四川省': {}}
for i in range(len(total_locations)):
    PAC = total_locations.iloc[i][0]
    province = total_locations.iloc[i][1]
    city = total_locations.iloc[i][2]
    county = total_locations.iloc[i][3]
    if county is np.nan:
        continue
    if city == '重庆市':
        province = '四川省'
    if city not in layerDict[province]:
        layerDict[province][city] = {}
    layerDict[province][city][county] = PAC


# 历史地名/地名考字典
# 需修改
history_name = history_image['NAME']
history_PAC = history_image['PAC']
history_dict = dict(zip(history_name, history_PAC))

# 省级表（不用再找了）
province_list = ['四川', '重庆']

# 缩写字典
countyAbbr = county_abbr_file['NAME'].tolist()
PAC_total = county_abbr_file['PAC'].tolist()
countyAbbrDict = dict(zip(countyAbbr, PAC_total))



