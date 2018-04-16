# -*- coding: Latin-1 -*-
import numpy as np
import os
import pandas as pd
import datetime

class Extract():
	
	def __init__(self, csvDirectory, db_schema, DebuggingMode, analyteNameDict, chromatographyDict):
		self.DebuggingMode = DebuggingMode
		self.csvDirectory = csvDirectory
		
		self.chromatographyDict = chromatographyDict			
		self.analyteNameDict = analyteNameDict
		self.db_schema = db_schema
		self.db_dict = {}
		
	def getcsvData(self):
		# initialize DataSetName, database dictionary, and concentration list
		self.initialize_db_dict()
		concLst = []
		self.DataSetName = ""
		
		# get a list of csv files in the define directory
		csvFiles = self.find_csv_filenames_remove_nonASCII()
		
		# iterates through the list of csv files
		for csvFile in csvFiles:
			# Determines concentration from csv files name a append it to the concLst
			concLst.append(self.string_to_concentration(csvFile))
			
			# Get data set name from csv directory name
			DataSetlst = self.csvDirectory.split('\\')
			self.DataSetName = DataSetlst[-1]
			
			# if debuggin mode is on then print the csv file to concole
			if self.DebuggingMode:
				print(csvFile)
			# reads the csv file and creates a DataFrame
			raw_csv_df = self.getRawCSVDataFrame(csvFile)
			
			# Checks if DataFrame is empty
			if raw_csv_df.empty == False: 
				
				# Checks if targeted analytes are within the DataFrame
				if self.are_analytes_found(raw_csv_df['Group']):
				
					# After passing the checks the required columns are cleaned
					# Then the analyte data and sample is added to self.db_dict
					cleaned_df = self.cleanData(raw_csv_df)
					foreignkey_dict = self.addAnalyteDataTo_db_dict(cleaned_df)
					self.addSampleDataTo_db_dict(cleaned_df, foreignkey_dict)
				
				else:
					# No targeted analyes found in sample
					pass
					
			else:
				# DataFrame is empty
				pass

		# Use the concLst to create the DataSetConcentrations sub-dictionary that will eventually
		# be added to the DataSetConcentrations database table
		
		self.AddDataSetConcentrationsTo_db_dict(concLst)
		
		# if debuggin mode is on then print the db_dict to concole
		# if self.DebuggingMode:
			#self.peak_in_db_dict()
			
		
		return self.db_dict
		
		
	def find_csv_filenames_remove_nonASCII(self, suffix=".csv"):
		# This methods finds all csv files in the defined directory
		# If any of the filenames contain a µ character replace with an _
		# Return a list of all csv file names
		
		filenames = os.listdir(self.csvDirectory)
		filenames_fixed = []
		for filename in filenames:
			if filename.endswith(suffix) and 'µ' in filename:
				new_filename = filename.replace('µ', '_')
				os.rename(os.path.join(self.csvDirectory, filename), 
					os.path.join(self.csvDirectory, new_filename))
				filenames_fixed.append(new_filename)
				
			elif filename.endswith(suffix):
				filenames_fixed.append(filename)
				
		return filenames_fixed

	def getRawCSVDataFrame(self, csvFile):
		# Reads the the csv file returns the resulting DataFrame
		# If the csv file is empty then it returns False
		try:
			df =  pd.read_csv(csvFile, encoding="Latin-1")
			return df
		except pd.errors.EmptyDataError:
			return pd.DataFrame()
		except pd.errors.ParserError:
			raise Exception('This csv file is fucked up. You migh want to re-export it dude.', csvFile)
			
	def are_analytes_found(self, group_series):
		# Returns a boolean checking if any targeted analytes are in the DataFrame 
		# It does this by making sure there is atleast 1 value that is not a nan
		# in the grouping column.
		
		return group_series.count() != 0
	
	def filter_df(self, df):
		# Drop all rows in the DataFrame where the "Group" column has missing values and
		# reindex the new dataframe so the row indexes start from 0, and the old index is dropped.
		return df.dropna(axis=0, subset=['Group'], how='any').reset_index(drop=True)
	
	def cleanData(self, df):
		# Remove all rows where group is nan
		df = self.filter_df(df)
		
		# split group column and add the Instrument & TuneAreaCounts columns to df
		split_group_df = self.split_column_to_df(df['Group'], ';')
		df = self.combine_data_frames_axis1(df, split_group_df[['Instrument', 'TuneAreaCounts']])
		
		# Remove the " volts" string from the [ Detector Voltage ] column
		detector_voltage_series = df.apply(self.convert_volts_to_int, axis=1)
		df['DetectorVoltage'] = detector_voltage_series
		
		# Convert the Type column to a DataProcessing type
		ProcessingType_series = df.apply(self.convert_type_column_to_ProcessingType, axis=1)
		df['ProcessingType'] = ProcessingType_series
		
		# Convert the [ GC Method ] column to the Chromatography type
		Chromatography_series = df.apply(self.convert_GCMethod_To_Chromatography, axis=1)
		df['Chromatography'] = Chromatography_series
		
		# Convert the Sample column to a Concentration in pg
		Concentration_series = df.apply(self.convert_sample_name_to_concentration, axis=1)
		df['Concentration_pg'] = Concentration_series
		
		# Convert the [ Sample Date ] & [ Sample Time ] columns to a single DateTime string
		# With the following formatting "YYYY-MM-DD HH:MM:SS"
		datetime_series = df.apply(self.convert_datetime, axis=1)
		df['SampleDateTime'] = datetime_series
		
		# Create sample table id column
		sampleid_series = df.apply(self.create_sample_id, axis=1)
		df['id'] = sampleid_series
		
		# Create analye table id column
		analyteid_series = df.apply(self.create_analyte_id, axis=1)
		df['analyte_id'] = analyteid_series	

		# Create AnalyteName column
		analyteName_series = df.apply(self.convert_Name_to_AnalyteName, axis=1)
		df['AnalyteName'] = analyteName_series
		
		# Create Table Name column
		tableName_series = df.apply(self.get_table_name, axis=1)
		df['TableName'] = tableName_series
		
		# Replace all nans in the dataframe
		df = df.fillna(0)
		
		return self.correctColumnNames(df)
			
		
	def split_column_to_df(self, group_series, delimiter):
		# Split the group_series into Instrument_SN & TuneAreaCounts columns
		# Then return a DataFrame Instrument_SN & TuneAreaCounts columns
		temp_df = group_series.str.split(pat=delimiter, expand=True)
		temp_df.columns = ['Not_Used', 'Instrument', 'TuneAreaCounts']
		return temp_df
		
	def combine_data_frames_axis1(self, df1, df2):
		# Glues together 2 DataFrames using the sorted union of the method
		return pd.concat([df1, df2], axis=1)
	
	def convert_Name_to_AnalyteName(self, row):
		return self.analyteNameDict.get(row['Name'], "Not Found")
		
	def get_table_name(self, row):
		if row['ProcessingType'] == 'PeakFinding':
			pt = 'PF'
		elif row['ProcessingType'] == 'TargetAnalyteFinding':
			pt = 'TAF'
			
		return row['AnalyteName'] + '_' + pt
	
	def convert_volts_to_int(self, row):
		# Splits the 1st four characters from the voltage column and returns it as an integer
		detector_voltage = row['[ Detector Voltage ]']
		return int(detector_voltage[:4])
		
	def convert_type_column_to_ProcessingType(self, row):
		# Converts the column value to a data processing type
		processingType = {'Unknown': 'PeakFinding',
							'Target': 'TargetAnalyteFinding'
						}
		Type = row['Type']
		pt = processingType.get(Type, "Other")
		if pt == "Other":
			raise Exception('Unrecognized Processing Type. Sample Name', row['Sample'])
		return pt
		
	def convert_GCMethod_To_Chromatography(self, row):
		# Converts the GC Method to the specific chromatography type
		chromatography = row['[ GC Method ]']
		return self.chromatographyDict.get(chromatography, "Unknown")
		
	def convert_sample_name_to_concentration(self, row):
		# Example sample name 'PAH Level 01 - 0.4 pg_µL Split 20-1 (20 fg on column)_2.csv'
		# This method gets the concentration value to the right of the "("
		# Then converts that value to pg.
		sample_name = row['Sample']
		return self.string_to_concentration(sample_name)
		
	def string_to_concentration(self, str):
		metricdict = {'fg': 0.001, 'pg': 1, 'ng': 1000}
		str_index = str.index('(') + 1
		concentration_lst = str[str_index:].split(' ')
		return float(concentration_lst[0]) * metricdict.get(concentration_lst[1], 0)
		
	def convert_datetime(self, row):
		#reformat input datetime (mm/dd/yyyy hh:mm:ss 12 hour clock) into yyyy-mm-dd hh:mm:ss 24 hour clock
		
		sample_date = row['[ Sample Date ]']
		sample_time = row['[ Sample Time ]']
		
		dt = '%s %s' % (sample_date, sample_time)
		datetime_parced  =  dt.split(" ")
		
		reformatted_date = str(datetime.datetime.strptime(datetime_parced[0], '%m/%d/%Y').strftime('%Y-%m-%d'))
		time_parced = datetime_parced[1].split(":")
		
		#Convert from AM/PM notation to 24 hr clock
		if datetime_parced[2] == "PM" and int(time_parced[0]) < 12:
			time_parced[0] = str(int(time_parced[0]) + 12)
		elif datetime_parced[2] == "AM" and int(time_parced[0]) == 12:
			time_parced[0] = str(int(time_parced[0]) - 12)
		
		#Zero pad the the hour
		if len(time_parced[0]) == 1:
			time_parced[0] = "0" + time_parced[0]
		
		reformatted_time = '%s:%s:%s' % (time_parced[0], time_parced[1], time_parced[2])
		return "%s %s" % (reformatted_date, reformatted_time)
		
	def create_sample_id(self, row):
		# creates sample table primary key: Instrument_SampleDateTime
		return row['Instrument'] + "_" + row['SampleDateTime']
		
	def create_analyte_id(self, row):
		# creates analyte table primary key: AnalyteName_Instrument_SampleDateTime_ProcessingType
		# real possiblity for errors here if the analyte name is not in
		# the analyte_dict.  
		
		AnalyteTableName = self.analyteNameDict.get(row['Name'], 'Not Found')
		
		if AnalyteTableName == 'Not Found':
			raise Exception('Analyte "%s" has not been added to the analyteNameDict. Sample Name: %s' % (row['Name'], row['Sample']))
			
		return AnalyteTableName + "_" + row['Instrument'] + "_" + row['SampleDateTime'] + "_" + row['ProcessingType']
	
	def correctColumnNames(self, df):
		return df.rename(columns ={'Peak S/N': 'Peak_SN', 'Quant S/N': 'Quant_SN', 'Quant Masses': 'Quant_Masses',
			'1st Dimension Time (s)': 'RT_1D', '2nd Dimension Time (s)': 'RT_2D', 
			'Tailing Factor': 'Tailing_Factor', 'FWHH (s)': 'FWHH'})
	
	def addAnalyteDataTo_db_dict(self, df):
		foreignkey_dict = {}
		for index, row in df.iterrows():
			desired_cols = self.db_schema[row['TableName']][1:]
			for col in desired_cols:
				self.db_dict[row['TableName']][col].append(row[col])
				if col == "Concentration_pg":
					conc = str(row[col])
				
			self.db_dict[row['TableName']]['id'].append(row['analyte_id'])
			foreignkey_dict[row['TableName'] + '_foreignkey'] = row['analyte_id']
			
		foreignkey_dict['DataSetConcentrations_foreignkey'] = self.DataSetName + '_' + conc
			
		return foreignkey_dict
		
	def addSampleDataTo_db_dict(self, df, foreignkey_dict):
		# Add first 7 columns to sub-dictionary
		row = df.iloc[0,:]
		desired_cols = self.db_schema['Sample'][:7]
		for col in desired_cols:
			self.db_dict['Sample'][col].append(row[col])
		
		# Add csv directory name as DataSetName to sub-dictionary
		self.db_dict['Sample']['DataSetName'].append(self.DataSetName)
		
		# Add foreignkeys to sub-dictionary
		for col in self.db_schema['Sample'][8:]:
			foreignkey = foreignkey_dict.get(col, "NotFound")
			self.db_dict['Sample'][col].append(foreignkey)
			
	def AddDataSetConcentrationsTo_db_dict(self, concLst):
		# Primary Key = DataSetName_Concentration
		
		# Convert concLst to a an np array then to a series so that
		# the value_counts method can be used
		concentration_data = np.array(concLst)
		concentration_counts = pd.Series(concentration_data).value_counts()
		
		#concentration_counts_lst = concentration_counts.tolist()
		concentration_lst = concentration_counts.index
		
		# Generate each id for concentration & concentration rep pair
		ids = [self.DataSetName + "_" + str(conc) for conc in concentration_lst]
		
		# Add lists to the DataSetConcentrations sub-dictionary
		self.db_dict['DataSetConcentrations']['id'].extend(ids)
		self.db_dict['DataSetConcentrations']['Concentration_pg'].extend(concentration_lst)
		self.db_dict['DataSetConcentrations']['Repetitions'].extend(concentration_counts.tolist())
			
		
	def initialize_db_dict(self):
		# self.db_dict is a dictionary of dictionaries
		# Primary dictionary - key: table name value: column name
		# Sub dictionaries - key: column name (values from primary dict) values: []
			# The list will be populated with the values extraced from the csv files	 
		
		
		for key_table, value_column_list in self.db_schema.items():
			self.db_dict[key_table] = {}
			for column in value_column_list:
				self.db_dict[key_table][column] = []
	
	def peak_in_db_dict(self):
		# Logic to look in self.db_dict
		for table_dict, value_column_dict in self.db_dict.items(): 
			print('table: ', table_dict)
			
			for key_column, value_list in value_column_dict.items():
				print('\tcolumn: ', key_column)
				
				for value in value_list:
					print('\t\t\t', value)
			
			print('\n')
			input('')