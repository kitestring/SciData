import os.path
import json
import fileinput


class JSON_Tools():
		
	def dump_Data_To_File(self, dict_file_path, **kwargs):
		all_dicts = {}
		
		if kwargs != None:
			for key, value in kwargs.items():
				all_dicts[key] = value
		
			with open(dict_file_path, 'w') as outfile:
				json.dump(all_dicts, outfile)
				outfile.close()
				
	def Load_Data(self, dict_file_path):
		with open(dict_file_path) as json_data:
			return json.load(json_data)
		
	def Parce_Data(self, json_data):
		# Dictionaries for SQLiteAPI
			# 'factTableColumns'
			# 'analyteTableColumns'
		# Dictionaries for csvExtract
			# 'analyteNameDict'
			# 'chromatographyDict'
		
		return json_data['factTableColumns'], json_data['analyteTableColumns'], json_data['analyteNameDict'], json_data['chromatographyDict']