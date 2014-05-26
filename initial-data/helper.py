import keywords

class Helper():
	def __init__(self):
		pass
	@staticmethod
	def flatten_dict_vals(list):
		print 'list', list
		result = []
		for i in list:
			if 'value' in i:
				result.append(i['value'])
		print 'result', result
		return result
	
	@staticmethod
	def get_keyword_values():
		list = []
		for dict in keywords.keywords_vocabulary:
			list.append(dict.get('value'))
		return list
