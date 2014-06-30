from vocabularies import vocabularies as v

def flatten_dict_vals(list):
    result = []
    for i in list:
        if 'value' in i:
            result.append(i['value'])
    return result

def get_terms(id):
    if v[id]:
        alist = v[id]['terms']
        reslist = []
        for item in alist:
            reslist.append(item['value'])
        return reslist



def get_keyword_values():
    import keywords
    list = []
    for dict in keywords.keywords_vocabulary:
        list.append(dict.get('value'))
    return list
