import json

from vocabularies_raw import vocabularies, keywords

# Returns list of dictionaries in the following format
# {'title':'Vocab Name','name':'vocab_name','terms':[{'name':'friendly_name', 'title':'Friendly Name', 'terms'(optional):[{'name':'term_name','title':'Term Name'}]}]}
def convert_raw_vocabularies():
    out_list = []
    # Gather vocabularies to tmp list
    tmp = []
    for vocab in vocabularies:
        # There are two types of vocabularies (lists and dicts) that require different manipulation
        if isinstance(vocabularies[vocab],list):
            tmp = convert_list(vocabularies[vocab])
        elif isinstance(vocabularies[vocab],dict):
            tmp = convert_dict(vocabularies[vocab])
        # Append to output list in required format 
        out_list.append({u'title': vocab, u'name': toMachineFriendly(vocab), u'terms': tmp})

    # Do the same for keywords
    tmp = []
    for keyword in keywords:
        tmp.append({u'title':keyword, u'name':toMachineFriendly(keyword), u'terms':convert_list(keywords[keyword])})

        # Append to output list in required format 
        # {'title':'Vocab Name','name':'vocab_name','terms':[{'name':'friendly_name', 'title':'Friendly Name'}]}
        out_list.append({u'title':u'Keywords', u'name':u'keywords', u'terms':tmp})

        fp = open("output.py", "w")
        fp.write(u"vocabularies = "+ json.dumps(out_list, indent=4))
        fp.close()

    return out_list

# Convert human-friendly to machine-friendly names
def toMachineFriendly(name):
    return name.lower().replace(" ","_").replace(",","").replace("(","").replace(")","")

# Convert each list item to appropriate format
# {'name':'friendly_name', 'title':'Friendly Name'}
def convert_list(lst):
    lista = []
    inner_dict = {}
    for it in lst:
        if lst == 'Inspire Data Themes el':
            print it
        lista.append({u'name':""+toMachineFriendly(it)+"",u'title':""+it+""})
    return lista

# Convert each dict item to appropriate format
# {'name':'friendly_name', 'title':'Friendly Name'}
def convert_dict(dct):
    result = []
    for k,v in dct.iteritems():
        result.append({u'name': toMachineFriendly(k), u'title':v})
    return result

if __name__ == '__main__':
    #print 
    convert_raw_vocabularies()
    #[1].get('terms')
    #for i in vocabularies['Inspire Data Themes el']:
    #    print i
