from owslib.iso import *
from lxml import etree
from jinja2 import Environment, FileSystemLoader

def validate_inspire(md):

	result = {}
	result["status"] = "succeded"
	result["errors"] = []
	result["num_of_errors"] = "0"
	errors = 0

	if md.identification is None:
		result["errors"].append("gmd:CI_ResponsibleParty: Organization missing")
		result["errors"].append("gmd:CI_ResponsibleParty: E-mail missing")
		result["errors"].append("gmd:CI_ResponsibleParty: Role missing")
		result["errors"].append("gmd:MD_DataIdentification: Title is missing")
		result["errors"].append("gmd:MD_DataIdentification: Abstract is missing")
		result["errors"].append("gmd:MD_ScopeCode: Resource Type is missing")
		result["errors"].append("gmd:language: Resource Language is missing")
		result["errors"].append("gmd:RS_Identifier: Unique Resource Identifier is missing")
		result["errors"].append("gmd:topicCategory: TopicCategory is missing")
		result["errors"].append("gmd:MD_Keywords: Keywords are missing")
		result["errors"].append("gmd:thesaurusName: Thesaurus Title is missing")
		result["errors"].append("gmd:thesaurusName: Thesaurus Date is missing")
		result["errors"].append("gmd:thesaurusName: Thesaurus Date Type is missing")
		result["errors"].append("gmd:EX_Extent: extent element is missing")
		result["errors"].append("gmd:EX_GeographicBoundingBox: bbox is missing")
		result["errors"].append("Both gmd:EX_TemporalExtent and gmd:CI_Date are missing")
		result["errors"].append("gmd:useLimitation is missing")
		result["errors"].append("gmd:accessConstraints is missing")
		result["errors"].append("gmd:otherConstraints is missing")
		errors += 20
	else:
		if md.identification.contact is None or len(md.identification.contact) < 1:
			result["errors"].append("gmd:CI_ResponsibleParty: Organization missing")
			result["errors"].append("gmd:CI_ResponsibleParty: E-mail missing")
			result["errors"].append("gmd:CI_ResponsibleParty: Role missing")
			errors += 3
		else:
			if md.identification.contact[0].organization is None:
				result["errors"].append("gmd:CI_ResponsibleParty: Organization missing")
				errors += 1
			if md.identification.contact[0].email is None:
				result["errors"].append("gmd:CI_ResponsibleParty: E-mail missing")
				errors += 1
			if md.identification.contact[0].role is None:
				result["errors"].append("gmd:CI_ResponsibleParty: Role missing")
				errors += 1

		if md.identification.title is None:
			result["errors"].append("gmd:MD_DataIdentification: Title is missing")
			errors += 1
		if md.identification.abstract is None:
			result["errors"].append("gmd:MD_DataIdentification: Abstract is missing")
			errors += 1
		if md.identification.identtype is None:
			result["errors"].append("gmd:MD_ScopeCode: Resource Type is missing")
			errors += 1
		if md.identification.resourcelanguage is None or len(md.identification.resourcelanguage) < 1:
			result["errors"].append("gmd:language: Resource Language is missing")
			errors += 1
		if md.identification.uricode is None or len(md.identification.uricode) < 1:
			result["errors"].append("gmd:RS_Identifier: Unique Resource Identifier is missing")
			errors += 1
		if md.identification.topiccategory is None or len(md.identification.topiccategory) < 1:
			result["errors"].append("gmd:topicCategory: TopicCategory is missing")
			errors += 1
		if md.identification.keywords is None or len(md.identification.keywords) < 1:
			result["errors"].append("gmd:MD_Keywords: Keywords are missing")
			result["errors"].append("gmd:thesaurusName: Thesaurus Title is missing")
			result["errors"].append("gmd:thesaurusName: Thesaurus Date is missing")
			result["errors"].append("gmd:thesaurusName: Thesaurus Date Type is missing")
			errors += 4
		else:
			if md.identification.keywords[0]['keywords'] is None or len(md.identification.keywords[0]['keywords']) < 1:
				result["errors"].append("gmd:MD_Keywords: Keywords are missing")
				errors += 1
			if md.identification.keywords[0]['thesaurus'] is None:
				result["errors"].append("gmd:thesaurusName: Thesaurus Title is missing")
				result["errors"].append("gmd:thesaurusName: Thesaurus Date is missing")
				result["errors"].append("gmd:thesaurusName: Thesaurus Date Type is missing")
				errors += 3
			else:
				if md.identification.keywords[0]['thesaurus']['title'] is None:
					result["errors"].append("gmd:thesaurusName: Thesaurus Title is missing")
					errors += 1
				if md.identification.keywords[0]['thesaurus']['date'] is None:
					result["errors"].append("gmd:thesaurusName: Thesaurus Date is missing")
					errors += 1
				if md.identification.keywords[0]['thesaurus']['datetype'] is None:
					result["errors"].append("gmd:thesaurusName: Thesaurus Date Type is missing")
					errors += 1
		if md.identification.extent is None:
			result["errors"].append("gmd:EX_Extent: extent element is missing")
			errors += 1
		else:
			if md.identification.extent.boundingBox is None:
				result["errors"].append("gmd:EX_GeographicBoundingBox: bbox is missing")
				errors += 1
			else:
				if md.identification.extent.boundingBox.minx is None:
					result["errors"].append("gmd:westBoundLongitude: minx is missing")
					errors += 1
				if md.identification.extent.boundingBox.maxx is None:
					result["errors"].append("gmd:eastBoundLongitude: maxx is missing")
					errors += 1
				if md.identification.extent.boundingBox.miny is None:
					result["errors"].append("gmd:southBoundLatitude: miny is missing")
					errors += 1
				if md.identification.extent.boundingBox.maxy is None:
					result["errors"].append("gmd:northBoundLatitude: maxy is missing")
					errors += 1
		if len(md.identification.date) < 1 and (md.identification.temporalextent_start is None or md.identification.temporalextent_end is None):
			result["errors"].append("Both gmd:EX_TemporalExtent and gmd:CI_Date are missing")
			errors += 1
		if len(md.identification.uselimitation) < 1:
			result["errors"].append("gmd:useLimitation is missing")
			errors += 1
		if len(md.identification.accessconstraints) < 1:
			result["errors"].append("gmd:accessConstraints is missing")
			errors += 1
		if len(md.identification.otherconstraints) < 1:
			result["errors"].append("gmd:otherConstraints is missing")
			errors += 1

	if md.languagecode is None:
		result["errors"].append("gmd:LanguageCode: Language code missing")
		errors += 1
	if md.datestamp is None:
		result["errors"].append("gmd:dateStamp: Date is missing")
		errors += 1
	if md.identifier is None:
		result["errors"].append("gmd:identifier: Identifier is missing")
		errors += 1
	if md.dataquality is None:
		result["errors"].append("gmd:LI_Lineage is missing")
		result["errors"].append("gmd:DQ_ConformanceResult: date is missing")
		result["errors"].append("gmd:DQ_ConformanceResult: date type is missing")
		# result["errors"].append("gmd:DQ_ConformanceResult: degree is missing")
		result["errors"].append("gmd:DQ_ConformanceResult: title is missing")
		errors += 4
	else:
		if md.dataquality.lineage is None:
			result["errors"].append("gmd:LI_Lineage is missing")
			errors += 1
		if len(md.dataquality.conformancedate) < 1:
			result["errors"].append("gmd:DQ_ConformanceResult: date is missing")
			errors += 1
		if len(md.dataquality.conformancedatetype) < 1:
			result["errors"].append("gmd:DQ_ConformanceResult: date type is missing")
			errors += 1
		# if len(md.dataquality.conformancedegree) < 1:
		# 	result["errors"].append("gmd:DQ_ConformanceResult: degree is missing")
		# 	errors += 1
		if len(md.dataquality.conformancetitle) < 1:
			result["errors"].append("gmd:DQ_ConformanceResult: title is missing")
			errors += 1

	if md.contact is None:
		result["errors"].append("gmd:contact: Organization name is missing")
		result["errors"].append("gmd:contact: e-mail is missing")
		errors += 2
	else:
		if md.contact[0].organization is None:
			result["errors"].append("gmd:contact: Organization name is missing")
			errors += 1
		if md.contact[0].email is None:
			result["errors"].append("gmd:contact: e-mail is missing")
			errors += 1

	if errors > 0:
		result["status"] = "failed"
		result["num_of_errors"] = str(errors)

	return result

def export_iso(md,template,outfile):
	pass

filename1 = 'aiolikos_charths.xml'
filename2 = 'aktogrammh.xml'
filename3 = 'full.xml'

# Create instances to test
valid_md = MD_Metadata(etree.parse(filename1))
not_valid_md = MD_Metadata(etree.parse(filename2))
full_md = MD_Metadata(etree.parse(filename3))

###########################
### create a new record ###
###########################
md = MD_Metadata()
md.identification = MD_DataIdentification()
md.dataquality = DQ_DataQuality()
md.distribution = MD_Distribution()
md.identification.extent = EX_Extent()
md.identification.extent.boundingBox = EX_GeographicBoundingBox()

# Metadata/Point Of Contact (GIMED):
val = CI_ResponsibleParty()
val.organization = 'xouxoutos'
val.email = 'foufoutos@gmail.com'
val.role = 'pointOfContact'
md.contact.append(val)
val = CI_ResponsibleParty() # record2
val.organization = 'momos'
val.email = 'kokos@gmail.com'
val.role = 'pointOfContact'
md.contact.append(val)

# Metadata/Metadata Date (GIMED):
md.datestamp = '2014-05-20'

# Metadata/Metadata Language (GIMED):
md.languagecode = 'eng'

# Identification/Resource Title (GIMED):
md.identification.title = 'Title blah blah'

# Identification/Resource Abstract (GIMED):
md.identification.abstract = 'Abstract blah blah'

# Identification/Resource Type (GIMED):
md.identification.identtype = 'dataset'

# Identification/Resource Locator (GIMED):
val = CI_OnlineResource()
val.url = 'http://publicamundi.eu'
md.distribution.online.append(val)

# Identification/Unique Resource Identifier (GIMED):
md.identifier = '286c0725-146e-4533-b1bf-d6e367f6c342'
md.identification.uricode.append('286c0725-146e-4533-b1bf-d6e367f6c342')

# Identification/Resource Language (GIMED):
md.identification.resourcelanguage.append('eng')
md.identification.resourcelanguage.append('gre')

# Classification/Topic Category (GIMED):
md.identification.topiccategory.append('biota')
md.identification.topiccategory.append('environment')

# Keyword/Keyword (GIMED):
kw = {}
kw['keywords'] = []
kw['keywords'].append('Agricultural and aquaculture facilities')
kw['keywords'].append('Bio-geographical regions')
kw['type'] = None
kw['thesaurus'] = {}
kw['thesaurus']['date'] = '2008-06-01'
kw['thesaurus']['datetype'] = 'publication'
kw['thesaurus']['title'] = 'GEMET - INSPIRE themes, version 1.0'
md.identification.keywords.append(kw)
kw = {}
kw['keywords'] = []
kw['keywords'].append('test')
kw['type'] = None
kw['thesaurus'] = {}
kw['thesaurus']['date'] = '2014-05-20'
kw['thesaurus']['datetype'] = 'creation'
kw['thesaurus']['title'] = 'test themes, version 2.0'
md.identification.keywords.append(kw)

# Geographic/Geographic (GIMED):
md.identification.extent.boundingBox.minx = '23.04'
md.identification.extent.boundingBox.maxx = '25.05'
md.identification.extent.boundingBox.miny = '44.03'
md.identification.extent.boundingBox.maxy = '45.01'

# Temporal/Temporal Extent (GIMED):
md.identification.temporalextent_start = '2014-05-20'
md.identification.temporalextent_end = '2014-05-21'

# Temporal/Date of publication (GIMED):
val = CI_Date()
val.date = '2014-05-06'
val.type = 'publication'
md.identification.date.append(val)
val = CI_Date()
val.date = '2014-05-08'
val.type = 'publication'
md.identification.date.append(val)

# Temporal/Date of creation (GIMED):
val = CI_Date()
val.date = '2014-05-01'
val.type = 'creation'
md.identification.date.append(val)

# Temporal/Date of revision (GIMED):
val = CI_Date()
val.date = '2014-05-12'
val.type = 'revision'
md.identification.date.append(val)

# Quality/Spatial Resolution (GIMED):
md.identification.denominators.append('5000')
md.identification.distance.append('2')
md.identification.uom.append('Meters')

# Quality/Lineage (GIMED):
md.dataquality.lineage = 'history blah blah blah'

# Conformity/Title (GIMED):
md.dataquality.conformancetitle.append('Commission Regulation (EU) No 1089/2010 of 23 November 2010 implementing Directive 2007/2/EC of the European Parliament and of the Council as regards interoperability of spatial data sets and services')

# Conformity/Date (GIMED):
md.dataquality.conformancedate.append('2010-12-08')
md.dataquality.conformancedatetype.append('publication')

# Conformity/Degree (GIMED):
md.dataquality.conformancedegree.append('true')

# Constraints/Limitations on public access (GIMED):
md.identification.accessconstraints.append('otherRestrictions')
md.identification.otherconstraints.append('no limitations')

# Constraints/Conditions for access and use-general (GIMED):
md.identification.uselimitation.append('no conditions apply')

# Organisation/Responsible Party (GIMED):
val = CI_ResponsibleParty()
val.email = 'lolos@gmail.com'
val.organization = 'NTUA'
val.role = 'owner'
md.identification.contact.append(val)

#######################
### end of creation ###
#######################

# Validate INSPIRE
print "------------------------------------------------"
print "Validation result for %s:" % filename1
print validate_inspire(valid_md)
print "------------------------------------------------"
print "Validation result for %s:" % filename2
print validate_inspire(not_valid_md)
print "------------------------------------------------"
print "Validation result for %s:" % filename3
print validate_inspire(full_md)
print "------------------------------------------------"
print "Validation result for custom MD_Metadata record:"
print validate_inspire(md)
print "------------------------------------------------"


# Save custom record to a valid ISO XML file
env = Environment(loader=FileSystemLoader('.'))
env.globals.update(zip=zip)
template = env.get_template('../mdmetadata2iso.xml')
iso_xml = template.render(md=md)
xml_file = "md.xml"
xml_file = open("md.xml", "w")
xml_file.write(iso_xml)
xml_file.close()
xml_file = "md.xml"

new_md = MD_Metadata(etree.parse(xml_file))
print "Validation result for custom MD_Metadata XML record:"
print validate_inspire(new_md)
print "------------------------------------------------"

# # Validate against ISO xsd
# try:
#     schema = 'http://schemas.opengis.net/iso/19139/20060504/gmd/gmd.xsd' 
#     #schema = './iso/19139/20060504/gmd/gmd.xsd'
#     schema = etree.XMLSchema(file=schema)
#     parser = etree.XMLParser(schema=schema,no_network=False)
#     with open(filename1, 'r') as f:
#     	doc = etree.fromstring(f.read(), parser)
#     	print "ISO file is valid"
# except Exception, err:
#     errortext = \
#     'Exception: document not valid.\nError: %s.' % str(err)
#     print errortext

# # Validate against ISO schematron
# iso_sch = 'schematron-rules-iso.sch'
# sct_doc = etree.parse(iso_sch)
# schematron = isoschematron.Schematron(sct_doc)
# xml_doc = etree.parse(filename1)
# print schematron.validate(xml_doc)

# # Validate against INSPIRE schematron
# ins_sch = 'schematron-rules-inspire.sch'
# sct_doc = etree.parse(ins_sch)
# schematron = isoschematron.Schematron(sct_doc)
# xml_doc = etree.parse(filename1)
# print schematron.validate(xml_doc)
