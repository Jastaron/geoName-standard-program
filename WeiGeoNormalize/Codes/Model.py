from lib import *

# 相似度匹配算法
'''
输入：
testList: 汉字列表，要计算和trainList的相似度
trainList：汉字列表，要计算和testList的相似度
输出：
[最高相似度县级单位，相似程度]
'''
def extract_SSC(list, index):
    Str = list[index]
    if Str != '':
        Ini = lpy(Str, style=Style.INITIALS)[0]
        IniCode = PyIniDict[Ini]
        Final = lpy(Str, style=Style.NORMAL)[0].replace(Ini, '')
        FinalCode = PyFinalDict[Final]
        Tone = lpy(Str, style=Style.TONE3)[0][-1]
        Py = '%s%s%s' % (IniCode, FinalCode, Tone)
        # print(Str,f'{wb(Str)[0]:$<4}')
        Wb = str(f'{wb(Str)[0]:$<4}')
        Bihua = strokesDict[get_stroke(Str, strokes)]
        SSC = Py + Wb + Bihua
    else:
        SSC = '00000000'
    return SSC


def SimilarityCal(testList, trainList, SimilarityScore):
    l = len(testList)
    SSCsum = 0
    for i in range(l):
        TestSSC = extract_SSC(testList, i)
        TrainSSC = extract_SSC(trainList, i)

        # print(TestSSC+'\t'+TrainSSC)

        def CComp(char1, char2):
            if char1 == char2:
                return 1
            else:
                return 0

        te = list(TestSSC)
        tr = list(TrainSSC)
        SSCscore = 0
        for j in range(len(te)):
            if j in [3, 4, 5, 6]:
                SSCscore += 0.15 * CComp(te[j], tr[j])
            else:
                SSCscore += 0.1 * CComp(te[j], tr[j])
            # SSCscore += 0.125*CComp(te[j],tr[j])
        SSCsum += SSCscore
    SSCsum /= l
    # SimilarityScore[''.join(trainList)] = SSCsum
    SimilarityScore.append([''.join(trainList), round(SSCsum, 1)])


def countyAddrComp(p3):
    # countyPro = {}
    leastRatio = 0.5
    SimilarityScore = []
    TestLen = len(p3)
    for i in range(TestLen):
        for j in range(len(countyAbbr)):
            if p3[i] in countyAbbr[j]:
                trainAbbr = countyAbbr[j]
                LocaTrain = countyAbbr[j].find(p3[i])
                LocaTest = i
                # print(LocaTrain,LocaTest)
                TrainList = list(trainAbbr)
                TestList = list(p3)
                # print(TrainList,TestList)
                diff = LocaTrain - LocaTest
                while diff > 0:
                    TestList.insert(0, "")
                    diff -= 1
                while diff < 0:
                    TrainList.insert(0, "")
                    diff += 1
                lenDiff = len(TrainList) - len(TestList)
                while lenDiff > 0:
                    TestList.append("")
                    lenDiff -= 1
                while lenDiff < 0:
                    TrainList.append("")
                    lenDiff += 1
                SimilarityCal(TestList, TrainList, SimilarityScore)
    SimilarityScore.sort(key=(lambda x: x[1]), reverse=True)
    # print(SimilarityScore)
    if len(SimilarityScore) > 0:
        if SimilarityScore[0][1] > leastRatio:
            return SimilarityScore[0]
    else:
        return None


# --------------------找到PAC返回全部数据--------------------
def match_find_return(match_record):
    match_group = []
    for i in [1, 2, 3, 0]:
        match_group.append(match_record.iloc[0][i])
    return match_group


# ---------------------按层级查询---------------------
def layer_search(locations, layerDict, city_error):
    point = layerDict
    layer_match_record = []
    get_pac = False
    for l in locations:
        search_list = list(point.keys())

        if l in '重庆市':
            point = layerDict['四川省']['重庆市']
            layer_match_record.extend(['四川省', '重庆市'])
            continue


        if point == layerDict['四川省']:
            city_bool = False
            for e in list(city_error.keys()):
                if l in e:
                    point = point[city_error[e]]
                    layer_match_record.append(city_error[e])
                    city_bool = True
                    break
            if city_bool:
                continue

        for i in search_list:
            if l in i:
                layer_match_record.append(i)
                point = point[i]
                break
            if isinstance(point, dict) and not isinstance(point[i], dict):
                continue
            harder_keys = point[i].keys()
            harder_tag = False
            for hk in harder_keys:
                if l in hk:
                    layer_match_record.append(i)
                    layer_match_record.append(hk)
                    point = point[i][hk]
                    harder_tag = True
                    break
            if harder_tag:
                break

        if not isinstance(point, dict):
            get_pac = True
            break

    if get_pac:
        match_record = total_locations[total_locations['PAC'] == point]
        result = match_find_return(match_record)
        return result

    if len(layer_match_record) == 2:
        match_record = total_locations[total_locations['city'] == layer_match_record[1]]
        result = match_find_return(match_record)
        return result
    return None


# ---------------------匹配的重构函数-----------------------
def search_child_function(locations, search_list, search_dict, total_locations, reverse_search=False,
                          accuracy_mode=False):
    match_find = False  # 置为False，当找到后可以跳出循环，或指示找到与否
    area_confuse = ['地区', '江津', '达县', '宜宾', '绵阳']  # 川渝的地区列表，需要避开它们找县

    indexs = range(len(locations))
    if len(set(area_confuse) & set(locations)) > 0:
        reverse_search = True

    if reverse_search:
        indexs = range(len(locations) - 1, -1, -1)

    for index in indexs:
        l = locations[index]
        if l in province_list:
            continue
        for i in search_list:
            if (accuracy_mode == True and l == i) or (accuracy_mode == False and l in i):
                # print(l,i)
                match_PAC = search_dict[i]
                # print(match_county)
                match_record = total_locations[total_locations['PAC'] == match_PAC]
                # print(match_record)
                match_find = True
                break
        if match_find:
            return match_find_return(match_record)
    return None


# -------------------利用数据库索引搜索--------------------
def db_search(locations, kind, reverse_search=False, accuracy_mode=False):
    match_find = False
    if reverse_search:
        indexs = range(len(locations) - 1, -1, -1)
    else:
        indexs = range(len(locations))

    for i in indexs:
        l = locations[i]
        if any(_ in l for _ in province):
            continue
        if accuracy_mode:
            sql = f'select * from `{kind}_pac` where {kind}_name = "{l}";'
        else:
            sql = f'select * from `{kind}_pac` where {kind}_name like "%{l}%";'
        cur = db.cursor()
        try:
            cur.execute(sql)
            data = cur.fetchall()
            # print('search db')
            if len(data) > 0:
                match_PAC = data[0][-1]
                match_record = total_locations[total_locations['PAC'] == match_PAC]
                match_find = True
            cur.close()
        except:
            continue
        if match_find:
            return match_find_return(match_record)
    return None


# ----------------------相似度算法------------------------
def similarity_search(locations, countyAbbr_dict, total_locations):
    match_find = False
    for l in locations:
        if any(l in p for p in province_list):
            continue
        l_list = list(l)
        result = countyAddrComp(l_list)
        if result is not None:
            match_PAC = countyAbbr_dict[result[0]]
            match_record = total_locations[total_locations['PAC'] == match_PAC]
            match_find = True
            break
    if match_find:
        return match_find_return(match_record)
    return None


# ----------------------get_locations-----------------------
# def get_locations(locations_str):
#     locations_list = [locations_str]
#     nation_keywords = ['省', '市', '区', '县','自治', '土家族', '苗族', '藏族', '彝族', '羌族']
#
#     szq_tag = False
#     if '市中区' in locations_str:
#         locations_list = locations_str.split('市中区')
#         szq_tag = True
#
#     for i in range(len(nation_keywords)):
#         temp_list = []
#         for j in range(len(locations_list)):
#             temp_list.extend(locations_list[j].split(nation_keywords[i]))
#         locations_list = temp_list
#
#     while '' in locations_list:
#         locations_list.remove('')
#
#
#     result_locations_list = []
#     for i in range(len(locations_list)):
#         if len(locations_list[i]) <= 2:
#             result_locations_list.append(locations_list[i])
#             continue
#         result_locations_list.extend(list(jieba.cut(locations_list[i], cut_all=False, HMM=False)))
#
#     if szq_tag:
#         result_locations_list.append('市中区')
#
#     return result_locations_list

def words_abbreviation(locations):
    nation_keywords = ['自治','土家族','苗族','藏族','彝族','羌族']
    locations_keywords = ['省','市','区','县']
    for i in range(len(locations)):
        if locations[i] == '市中区':
            continue
        radix = 0
        for n_kw in nation_keywords:
            if n_kw in locations[i]:
                locations[i] = locations[i].split(n_kw)[0]
        while any(k in locations[i] for k in locations_keywords) and len(locations[i]) > 2:
            locations[i] = locations[i].split(locations_keywords[radix])[0]
            radix += 1
    while '' in locations:
        locations.remove('')

def get_locations(locations_str):
    locations = list(jieba.cut(locations_str,cut_all=False,HMM=False))
    # print(locations)
    result_locations = []
    single_char = []
    for i in range(len(locations)):
        if len(locations[i]) == 1:
            unicode = ord(locations[i])
            if 13312 <= unicode <= 64045 or 131072 <= unicode <= 194998:
                single_char.append(locations[i])
        else:
            if len(single_char) > 0:
                result_locations.append(''.join(single_char))
                single_char = []
            result_locations.append(locations[i])
    if len(single_char) > 0:
        result_locations.append(''.join(single_char))
    words_abbreviation(result_locations)
    return result_locations


'''--------------------------标准化匹配算法----------------------------'''
def MatchCounty_new(locations_str):
    locations = get_locations(locations_str)
    # print(locations)
    temp_result = None

    # print('layer')
    result = layer_search(locations, layerDict, city_error)
    if result is not None:
        if result[2] is np.nan:
            temp_result = result
        else:
            return result

    # 县级匹配
    # print('county')
    result = search_child_function(locations, countyAbbr, countyAbbrDict, total_locations, reverse_search=False, accuracy_mode=False)
    if result is not None:
        return result

    # 县级匹配
    # print('county')
    result = search_child_function(locations, history_name, history_dict, total_locations, reverse_search=False, accuracy_mode=False)
    if result is not None:
        return result

    if temp_result is not None:
        return temp_result

    # 山峰
    # print('nature')
    result = db_search(locations, 'nature', reverse_search=True, accuracy_mode=True)
    if result is not None:
        return result

    # 小地名
    # print('little')
    result = db_search(locations, 'little', reverse_search=True, accuracy_mode=True)
    if result is not None:
        return result

    # 相似度
    # print('similarity')
    result = similarity_search(locations, countyAbbrDict, total_locations)
    if result is not None:
        return result

    # print('none')

    return []

def output_result(input_str):
    result = MatchCounty_new(input_str)
    if len(result) == 0:
        return ['nan']
    for i in range(len(result)):
        if result[i] is np.nan:
            result[i] = 'nan'
        else:
            result[i] = str(result[i])
    return result