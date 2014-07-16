import json

# Returns list of dictionaries in the following format
# {'title':'Vocab Name','name':'vocab_name','terms':[{'name':'friendly_name', 'title':'Friendly Name', 'terms'(optional):[{'name':'term_name','title':'Term Name'}]}]}
def convert_raw_vocabularies():
    out_list = []
    # Gather vocabularies to tmp list
    tmp = []
    with open("vocabularies_raw.json") as json_file:
        data = json.load(json_file)

    for vocab in data:
        # There are two types of vocabularies (lists and dicts) that require different manipulation
        if isinstance(data.get(vocab), list):
            tmp = convert_list(data.get(vocab))
        elif isinstance(data.get(vocab), dict):
            if vocab == 'keywords':
                tmp = convert_keyword_dict(data.get(vocab))
            else:
                tmp = convert_dict(data.get(vocab))

        # Append to output list in required format 
        out_list.append({u'title': vocab, u'name': toMachineFriendly(vocab), u'terms': tmp})

    with open("vocabularies.py", "w") as fp:
        fp.write(u"vocabularies = "+ unicode(json.dumps(out_list, indent=4), encoding='utf-8'))
        fp.close()

    return out_list

# Convert human-friendly to machine-friendly names
def toMachineFriendly(name):
    return name.lower().replace(" ","_").replace(",","").replace("(","").replace(")","").replace("-","").replace("__","_")

# Convert each list item to appropriate format
# {'name':'friendly_name', 'title':'Friendly Name'}
def convert_list(lst):
    lista = []
    inner_dict = {}
    for it in lst:
        lista.append({u'name':""+toMachineFriendly(it)+"",u'title':""+it+""})
    return lista

# Convert each dict item to appropriate format
# {'name':'friendly_name', 'title':'Friendly Name'}
def convert_dict(dct):
    result = []
    for k,v in dct.iteritems():
        result.append({u'name': toMachineFriendly(k), u'title':v})
    return result

# Convert each dict item to appropriate format
# {'name':'friendly_name', 'title':'Friendly Name', 'terms':{'name':'blabla', 'title':'Bla Bla'}}
def convert_keyword_dict(dct):
    result = []
    for k,v in dct.iteritems():
        tmp = []
        for value in v:
            tmp.append({u'name':toMachineFriendly(value), u'title':value})

        result.append({u'name': toMachineFriendly(k), u'title':k, u'terms':tmp})
    return result

if __name__ == '__main__':
    #print 
    convert_raw_vocabularies()
    #[1].get('terms')
    #for i in vocabularies['Inspire Data Themes el']:
    #    print i
