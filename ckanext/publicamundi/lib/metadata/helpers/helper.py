import keywords


class Helper():

    def __init__(self):
        pass

    @staticmethod
    def flatten_dict_vals(list):
        result = []
        for i in list:
            if 'value' in i:
                result.append(i['value'])
        return result

    @staticmethod
    def get_keyword_dict(value):
        dict = {}
        for adict in keywords.keywords_vocabulary:
            if adict.get('value') == value:
                dict = adict
                break
        return dict

    @staticmethod
    def get_all_keyword_terms():
        lista = []
        for adict in keywords.keywords_vocabulary:
            lista += adict.get('terms')
        return list(set(Helper.flatten_dict_vals(lista)))

    @staticmethod
    def get_keyword_keys():
        lista = []
        for a in keywords.keywords_vocabulary:
            lista.append(a.get('value'))
        return lista

#if __name__ == '__main__':

    #print Helper.get_keyword_keys()
