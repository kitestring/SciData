from GUI import ConcoleGUI 
from csvExtract import Extract
from SQLiteAPI import SciDatabase
from DataProcessor import Calculator
import os
import pandas as pd
import time
from jsonAPI import JSON_Tools
import socket
from excelmacros import Macros

class Controls():
	
	def __init__(self):
		self.calc = Calculator()
		self.gui = ConcoleGUI()
		self.DebuggingMode = False
		self.csvDirectory = os.getcwd()
		
		self.factTableColumns = {}
		self.analyteTableColumns = {} 
		self.analyteNameDict = {} 
		self.chromatographyDict = {}
		
		runDescription = '''Generates a plot that shows the total number of hours for\n\t\ta given category\\sub-category per 7 day period.'''
		self.commandDict = {
			'help': [self.basicInstructions, "Lists each command."],
			'exit': [self.exitProgram, "Exits the program."],
			'mine': [self.ETL, 'Extracts the data from all the csv files found in the\n\t\tcurrent working directory. Then loads into\n\t\tthe SQL database.'],
			'dbug': [self.Debugging, 'Enables debugging mode which logs activity to the concole.'],
			'clr': [self.clearDatabase, 'Clears all the data from your database.'],
			'set': [self.dataSetList, 'Prints a list of each data set that has been uploaded.'],
			'summ': [self.SummaryTable, 'Outputs a summary table containing IDL,\n\t\tsensitivity, & spectral quality data for each analyte within a given data set.'],
			'sim': [self.CreateSpectralQualityVisualizations, "Outputs the spectral quality data.\n\t\tWhich includes a plot of Concentration vs. Similarity scores and tabulated data."],
			'quan': [self.CreateQuantCurve, "Outputs a scatter plot for concentration vs. area with a 1st order best fit."],
			'cs': [self.clearDataSet, "Clears the defined data set(s) from the data base."],
			'vs': [self.ViewSet, "Shows which analytes are containted in each data set\n\t\t& how many replicates at each concentration were found."],
			'sv': [self.SaveDictionaries, "Saves the following dictionaries:\n\t\t\t-factTableColumns\n\t\t\t-analyteTableColumns\n\t\t\t-analyteNameDict\n\t\t\t-chromatographyDict"],
			'add': [self.AddAnalyte, "Add's an analyte to the database"],
			'vd': [self.ViewJSONDataFile, "View Python dictionaries."],
			'gc': [self.AddGCMethod, "Add's a GC method to the database."],
			'aas': [self.AddSynonymToAnalyteDict, "Add a synonym to an existing analyte in the analyte dictionary."],
			'pt': [self.MakePrettyTables, "Converts the average similarity csv files to a single excel file with pretty tables."]
			}
		self.runProgram = True
		# if this is being run on my computer then run locally else use the S: drive
		if socket.gethostname() == 'CND651145F':
			self.workingpath = 'C:\\SciData'
		else:
			self.workingpath = 'S:\\006_Mercury II\\Analyses\\050_6500 Series Data Automation'
			
		self.dbname = 'HRT_6500_Validation.db'
		self.dict_file_path = os.path.join(self.workingpath, 'dicts.txt')
		self.JSON_Tools = JSON_Tools()
		
	def initialize(self):
		# Gets all of the object dictonary data from dicts.txt
		# Next, creates an new SciDatabase object 
		self.loadDicts()
		self.sciDB = SciDatabase(os.path.join(self.workingpath, self.dbname), self.factTableColumns, self.analyteTableColumns)
	
	def SaveDictionaries(self):
		self.JSON_Tools.dump_Data_To_File(self.dict_file_path, factTableColumns = self.factTableColumns, analyteTableColumns = self.analyteTableColumns, analyteNameDict = self.analyteNameDict, chromatographyDict = self.chromatographyDict)
	
	def loadDicts(self):
		self.factTableColumns, self.analyteTableColumns, self.analyteNameDict, self.chromatographyDict = self.JSON_Tools.Parce_Data(self.JSON_Tools.Load_Data(self.dict_file_path))
	
	def MakePrettyTables(self):
		filenames = os.listdir(self.csvDirectory)
		# Remove files that are not csv's and not a SummaryTable csv
		filenames[:] = [os.path.join(self.csvDirectory, f) for f in filenames if '.csv' in f and not 'SummaryTable' in f]
		csvFilesStr = ','.join(filenames)
		ExcelVBAMacros = Macros()
		self.giveUserFeedback('Building Pretty Tables Workbook\nPlease Wait a Moment...')
		ExcelVBAMacros.BuildPrettyTableWorkbook(csvFilesStr)
		self.giveUserFeedback('Done Building Pretty Tables Workbook')
	
	def AddSynonymToAnalyteDict(self):
		self.giveUserFeedback('Careful I was laszy on this one, and there is few checks.\nBe sure you are sure!!!')
		existing_analyte = self.getRawUserInput('Which Analyte do you wish to add synonym to?')
		new_synonym = self.getRawUserInput('Input additional synonym.')
		message = "Existing Analyte to add synonym: {ex}\nNew Analyte Synonym: {ns}".format(ex=existing_analyte,ns=new_synonym)
		self.giveUserFeedback(message)
		response = self.getRawUserInput('Type "y" to accept')
		if response.lower() == 'y':
			self.analyteNameDict[new_synonym] = existing_analyte
			self.giveUserFeedback('Changes Accepted')
		else:
			self.giveUserFeedback('Action Aborted')
	
	def ViewJSONDataFile(self):
		Loaded_JSON_Data = self.JSON_Tools.Load_Data(self.dict_file_path)
		text = self.JSON_Tools.toString(Loaded_JSON_Data)
		self.giveUserFeedback(text)
	
	def run(self):
		# returns the boolean value for runProgram
		return self.runProgram
	
	def exitProgram(self):
		self.runProgram = False
		self.giveUserFeedback('Exiting Program...\nGoodbye')
		self.sciDB.closeDBConnection()
		
	def runUserCommand(self, prompt):
		# Prompts the user for a command using the getRawUserInput method then
		# sends the command to the exectuteCommand method
		self.exectuteCommand(self.gui.userInput(prompt))
		
	def getRawUserInput(self, prompt):
		# Prompts the user for a command using the userInput
		# method which the GUI class has.
		return self.gui.userInput(prompt)
		
	def giveUserFeedback(self, text):
		# Outputs feedback to the user via text to the concoleOutput
		# this is handled by the concoleOutput method with the GUI class has
		self.gui.concoleOutput(text)
	
	def basicInstructions(self):
		# Gets the program instructions string from the getCommandsWithDescriptions method
		# then sends the string to the giveUserFeedback method
		# Add csv directory name as DataSetName to sub-dictionary
		current_working_directory = self.csvDirectory.split('\\')
		
		text = 'Current Working Directory: ' + current_working_directory[-1] + "\n\n" + self.getCommandsWithDescriptions()
		self.giveUserFeedback(text)
	
	def AddAnalyte(self):
		# Adds an analyte to the database
		# Adds x_TAF_foreignkey & x_PF_foreignkey to the self.factTableColumns (list)
		# Adds x to the self.analyteNameDict & checks for alternative names
		# Creates corresponding tables in the data base and updates the sample table
		
		new_analyte = self.getRawUserInput('Input the analyte to add...')
		new_analyte_names = [new_analyte]
		
		# Checks to see if this analyte is already in the database
		if (new_analyte + "_TAF_foreignkey") in self.factTableColumns:
			self.giveUserFeedback("Analyte is already in the database.")
			return None
		elif new_analyte == '':
			self.giveUserFeedback("No Entry, Action Aborted")
			return None
		else:
			# Check to see if 1st character of the new analyte name begins with a number
			# This is done because SQL will not allow a column or table to begin with a number
			try:
				int(new_analyte[0])
				self.giveUserFeedback("Analyte name cannot begin with a number.")
				return None
			except ValueError:
				# Do nothing if the 1st character of the new analylte name is not an integer
				pass
			
			# Prompts user to define an additional synonym
			synonym = self.getRawUserInput("Define any synonym for this analyte, if none leave blank.")
			if synonym != '':
				new_analyte_names.append(synonym)
				text = "New Analyte:\t\t%s\nNew Synonym Name 1: \t%s\nNew Synonym Name 2: \t%s" % (new_analyte, new_analyte_names[0], new_analyte_names[1])
			else:
				text = "New Analyte:\t\t%s\nNew Synonym Name 1: \t%s" % (new_analyte, new_analyte_names[0])
			
			# Allow the user to confirm selection before applying the change
			self.giveUserFeedback(text)
			confirm = self.getRawUserInput("Do you wish to update the database with the analyte above. - (y)")
			if confirm.lower() == 'y':
				# Update the self.analyteNameDict
				for new_analyte_name in new_analyte_names:
					self.analyteNameDict[new_analyte_name] = new_analyte
					self.analyteNameDict[new_analyte_name] = new_analyte
				# Update the self.factTableColumns
				self.factTableColumns.append(new_analyte + "_TAF_foreignkey")
				self.factTableColumns.append(new_analyte + "_PF_foreignkey")
				# Apply updates to the self.sciDB
				self.sciDB.AddAnalyteToDatabase(new_analyte)
				# After the database has been updated, save changes to file
				self.SaveDictionaries()
				# Inform user of updates
				self.giveUserFeedback("The analyte above has been added to the database.")
	
	def AddGCMethod(self):
		# Add the defined GC method to the chromatographyDict
		# Key = GC method & value = 1D or GCxGC
		
		new_GC_Method = self.getRawUserInput('Input a new GC Method')
		
		# Checks to see if this analyte is already in the dictionary
		if self.chromatographyDict.get(new_GC_Method, 'NotFound') != 'NotFound':
			self.giveUserFeedback("GC Method is already in the database.")
		else:
			text = 'You have entered the following GC method: "%s"\nDefine this as a 1D or GCxGC method with the corresponding integer.\n\t1: 1D\n\t2: GCxGC' % new_GC_Method
			new_GC_Method_type = self.getRawUserInput(text)
			if new_GC_Method_type == '1':
				self.chromatographyDict[new_GC_Method] = '1D'
				text = "Added to chromatographyDict.\nGC Method\t%s\nChromatography:\t1D" % new_GC_Method
			elif new_GC_Method_type == '2':
				self.chromatographyDict[new_GC_Method] = 'GCxGC'
				text = "Added to chromatographyDict.\nGC Method\t%s\nChromatography:\tGCxGC" % new_GC_Method
			else:
				self.giveUserFeedback('Invalid entry, action aborted.')
				return None
			
			# Save changes to file
			self.SaveDictionaries()
			self.giveUserFeedback(text)
	
	def getCommandsWithDescriptions(self):
		# Iterates through the commandDict to build a string
		# that lists each command with a description of what it does
		keyList = self.commandDict.keys()
		keyList = sorted(keyList)
		commandString = 'Command\t\tDescription'
		for key in keyList:
			commandString += '\n%s\t\t%s' % (key, self.commandDict[key][1])
		
		return commandString
		
	def ETL(self):
		# Extracts data from the csv files for the parced directory.
		# The data is returned as a pandas DataFrame which sould be loaded into
		# the sample (fact) table.  It will also return a dictionary where each 
		# key is a DB table name and the value is an analyte DataFrame which should
		# be loaded into the corresponding analyte (dimension) table.
		
		csvExtractor = Extract(self.csvDirectory, self.sciDB.schema, self.DebuggingMode, self.analyteNameDict, self.chromatographyDict)
		csv_dict = csvExtractor.getcsvData()
		
		if self.DebuggingMode:
			csvExtractor.peak_in_db_dict()
		
		start_time = time.time()
		
		for key_table, value_column_dict in csv_dict.items():
				
			if len(value_column_dict['id']) != 0:
				self.sciDB.load_Data(pd.DataFrame(value_column_dict), key_table)
		
		self.sciDB.CommitDB()
		
		self.giveUserFeedback("--- %s seconds ---" % (time.time() - start_time))
		self.giveUserFeedback('Data successfully uploaded to  the database')
		
	def clearDatabase(self):
		response = self.getRawUserInput("The action will clear all the data in your database\nare you sure you want to do this?\nType 'y' to confirm")
		if response.lower() == 'y':
			self.sciDB.clearDB()
			self.sciDB.CommitDB()
			self.giveUserFeedback('You have cleared all data from the database.')
		else:
			self.giveUserFeedback('You have aborted this action')
	
	def clearDataSet(self):
		# Prompt user to select data sets to clear from the database
		data_sets, analytes_lst, analyte_table_lst = self.InitializeDataSet()
		if data_sets == False:
			return None
		
		# Clear the data from the defined data set(s)
		self.sciDB.ClearDataSetData(data_sets, analyte_table_lst)
	
	def ViewSet(self):
		# Prints all the number of times each analylte that was found at 
		# each concentration in a given data set 
		
		# Prompt the user to select a given data set
		data_set = self.DataSetSelector()
		
		if data_set == "Invalid Selection":
			self.giveUserFeedback("Invalid Selection - Action Aborted")
		else:
			analytes_lst, analyte_table_lst = self.GetUniqueAnalyteAndAnalyteTableListsForAllDataSets([data_set])
			df = self.sciDB.GetRepsAtEachConcentration(analyte_table_lst, data_set)
			print(df)
			
	
	def CreateSpectralQualityVisualizations(self):
		# Prompt user to select data sets to include in the output & 
		# Query DB for all the unique analytes and data_tables accross all data_sets
		data_sets, analytes_lst, analyte_table_lst = self.InitializeDataSet('PeakFindingOnly')
		if data_sets == False:
			return None
		
		# Iterate through each analyte table and create each Spectral Plot & Table
		for n, analyte_table in enumerate(analyte_table_lst):
			similarity_df = self.sciDB.Similarities(analyte_table, data_sets)
			df = self.calc.BuildSimilarity_PlotsTables(similarity_df, data_sets, analytes_lst[n])
			self.DataFrameToCSV(df, analytes_lst[n], True)
			
	def CreateQuantCurve(self):
		# Prompt user to select data sets to include in the output & 
		# Query DB for all the unique analytes and data_tables accross all data_sets
		data_sets, analytes_lst, analyte_table_lst = self.InitializeDataSet('TargetAnalyteFindingOnly')
		if data_sets == False:
			return None
		
		# Iterate through each analyte table create a single df with
		# the data that will be used to create all the plots 
		quant_df_lst = []
		for analyte_table in analyte_table_lst:
			quant_df_lst.append(self.sciDB.GetQuantCurveData(analyte_table, data_sets))
		quant_df = pd.concat(quant_df_lst)
		
		# Prompts the user to select the desired concentration range to be plotted
		max_conc, min_conc = self.ConcentrationRangeSelector(quant_df['Conc_pg'])
		# Terminate the method 
		if max_conc == None or min_conc == None:
			self.giveUserFeedback('You have entered an invalid value.')
			return None
		elif max_conc == 'Skip' or min_conc == 'Skip':
			return None
		
		# Filter df for concentration range
		quant_df = quant_df[(quant_df['Conc_pg'] >= min_conc) & (quant_df['Conc_pg'] <= max_conc)]
		
		# Create each QuantCurve
		self.calc.BuildQuantCurves(quant_df)
		
	def ConcentrationRangeSelector(self, conc_pd_series):
		# Converts a unique list of concentrations to a dictionary with integers as keys
		conc_lst = sorted(conc_pd_series.value_counts().index)
		conc_dict = {key: value for key, value in enumerate(conc_lst)}
		
		# Iterates through the conc_dict to build a string
		# that lists each conc_dict paired with a selection integer
		keyList = conc_dict.keys()
		keyList = sorted(keyList)
		concentrationString = 'Int\tConc (pg)'
		for key in keyList:
			concentrationString += '\n%s\t%s' % (key, round(conc_dict[key],2))
		
		# Splits the user selection into a list
		concentrationString += '\n\nAbove is the concentration range for the selected data set(s).\nSelect two integers comma delimited that correspond with the\ndesired concentration range to be ploted.'
		selection = self.getRawUserInput(concentrationString)
		selections = selection.replace(" ","").split(',')
		
		# Checks for the correct number of elements in the list
		if len(selections) != 2:
			self.giveUserFeedback('You have entered the incorrect number of values.')
			return 'Skip', 'Skip'
		# Assignes the corresponding selected key values to the variables below
		else:
			try:
				selections = [int(x) for x in selections]
				selections = sorted(selections)
				max_conc = conc_dict.get(selections[1], None)
				min_conc = conc_dict.get(selections[0], None)
			except ValueError:
				return None, None
				
		return max_conc, min_conc
	
	
	def InitializeDataSet(self, DataProcessingType='Both_PeakFinding_TargetAnalyteFinding'):
		# Prompt user to select data sets to include in the output
		data_sets = self.MultiDataSetSelector()
		if data_sets == False:
			return False, None, None
					
		# Query DB for all the unique analytes and data_tables accross all data_sets
		analytes_lst, analyte_table_lst = self.GetUniqueAnalyteAndAnalyteTableListsForAllDataSets(data_sets, DataProcessingType)
		
		return data_sets, analytes_lst, analyte_table_lst
		
	def GetUniqueAnalyteAndAnalyteTableListsForAllDataSets(self, data_sets, DataProcessingType='Both_PeakFinding_TargetAnalyteFinding'):
		# Query DB for all the unique analytes and data_tables accross all data_sets
		analytes_lst = []
		analyte_table_lst = []
		for data_set in data_sets:
			temp_analytes_lst, temp_analyte_table_lst = self.sciDB.DataSetAnalytes(data_set, DataProcessingType)
			analytes_lst.extend(temp_analytes_lst)
			analyte_table_lst.extend(temp_analyte_table_lst)
		
		analytes_lst = sorted(list(set(analytes_lst)))
		analyte_table_lst = sorted(list(set(analyte_table_lst)))
		
		return analytes_lst, analyte_table_lst
		

	
	def MultiDataSetSelector(self):
		# Gets the list of data sets to visualize, checks that the selections are valid, 
		# and checks with the user that the correct selections have been made.
		data_sets, invalid_selection = self.GetMultiDataSetSelections()
		
		# Check if selections are valid
		if invalid_selection == True:
			self.giveUserFeedback("Invalid Selection - Action Aborted")
			return False
		# Let user confirm selections
		else:
			text = "\n".join(data_sets) + '\n\nYou have selected the data sets above. Do you wish to continue with these selections?\nType "y" to confirm'
			response = self.getRawUserInput(text)
			if response.lower() != 'y':
				self.giveUserFeedback('You have aborted this action')
				return False
			else:
				return data_sets
	
	def GetMultiDataSetSelections(self):
		# Allows the user to select a multiple data sets by selecting a corresponding integers.
		# that are comma delimited.  Returns the selected data sets as a list of strings
		DataSetDict = self.createDataSetDict()
		text = '\n%s\t%s' % ('No.', 'Data Set')
		for key, value in DataSetDict.items():
			text = text + '\n%s\t%s' % (key, value)
		self.giveUserFeedback(text)
		
		selection = self.getRawUserInput('Enter comma seperated integer to select a data set(s).')
		selections = selection.replace(" ","").split(',')
		data_sets = []
		for selection in selections:
			data_sets.append(DataSetDict.get(selection, "Invalid Selection"))
		return data_sets, ("Invalid Selection" in data_sets)
	
	def dataSetList(self):
		for set in sorted(self.sciDB.UniqueDataSets()):
			print(set)
			
	def SummaryTable(self):
		data_set = self.DataSetSelector()
		
		if data_set == "Invalid Selection":
			self.giveUserFeedback("Invalid Selection - Action Aborted")
		else:
			df = self.CreateSummaryTable(data_set)
			print(df)
			self.DataFrameToCSV(df, "SummaryTable" + "_" + data_set, False)
			
	def CreateSummaryTable(self, data_set):
		# Initialize DataFrame
		df = pd.DataFrame(columns=['Analyte', 'Chrom', 'IDL', 'PF_Sen', 'TAF_Sen', 'MinConc_800_Sim'])
		# Query DB for analyte & analyte tables lists
		# analytes_lst, analyte_table_lst = self.getDataSetAnalyteTables(data_set)
		analytes_lst, analyte_table_lst = self.sciDB.DataSetAnalytes(data_set)
		if self.DebuggingMode == True:
			print(analytes_lst)
			print('\n')
			print(analyte_table_lst)
			input('pause')
		
		# Initialize analyte_dict
		analyte_dict = self.Initialize_Analyte_dict(analytes_lst)
		
		for analyte_table in analyte_table_lst:
			
			# Get analyte name & Data Processing Type
			AnalyteName, ProcessingType = self.sciDB.GetAnalyteNameAndProcessingType(analyte_table)
			
			if self.DebuggingMode == True:
				print('AnalyteName: ', AnalyteName)
				print('ProcessingType: ', ProcessingType)
			
			# Determines the concentration where at least 50% of the time
			# the defined analytes is found, this concentration is assigned to analyte_sensitivity.
			sensitivity_df = self.sciDB.SensitivityQuery(analyte_table, data_set)
			analyte_sensitivity = self.calc.SensitivityFinder(sensitivity_df)
			
			if ProcessingType == "TargetAnalyteFinding":
				analyte_dict[AnalyteName]['TAF_Sen'] = analyte_sensitivity
				
				# Determine IDL at 100 fg (TAF only)
				df_Area_100fg = self.sciDB.Get_100fgArea(analyte_table, data_set)
				Area_100fg_lst = df_Area_100fg['Area_100fg'].tolist()
				IDL = self.calc.calculate_IDL(Area_100fg_lst, 100, self.DebuggingMode)
				analyte_dict[AnalyteName]['IDL'] = IDL
				
			elif ProcessingType == "PeakFinding":
				analyte_dict[AnalyteName]['PF_Sen'] = analyte_sensitivity
				
				# Determine lowest concentration where the average similarity >= 800 (PF only)
				df_ave_sim = self.sciDB.GetAveSimilarities(analyte_table, data_set)
				lowest_conc_with_800_similarity = self.calc.Lowest800Similarity(df_ave_sim)
				analyte_dict[AnalyteName]['MinConc_800_Sim'] = lowest_conc_with_800_similarity
				
			# Get chromatography
			analyte_dict[AnalyteName]['Chrom'] = self.sciDB.GetChromatography(data_set)
		
		# Appends data in analyte_dict to the DataFrame
		for analyte in analytes_lst:
			analyte_dict[analyte]['Analyte'] = analyte
			df = df.append(analyte_dict[analyte], ignore_index=True)
			
		return df
	
	def Initialize_Analyte_dict(self, analyte_list):
		analyte_dict = {}
		for analyte in analyte_list:
			analyte_dict[analyte] = {}
		return analyte_dict
	
	def DataSetSelector(self):
		# Allows the user to select a data set by selecting a corresponding integer.
		# Returns the selected data set as a string
		DataSetDict = self.createDataSetDict()
		text = '\n%s\t%s' % ('No.', 'Data Set')
		for key, value in DataSetDict.items():
			text = text + '\n%s\t%s' % (key, value)
		self.giveUserFeedback(text)
		
		selection = self.getRawUserInput('Enter an integer to select a data set.')
		return DataSetDict.get(selection, "Invalid Selection")
	
	def DataFrameToExcel(self, df):
		# self.getRawUserInput('Enter Excel File Name')
		pass
		
	def DataFrameToCSV(self, df, FileName, include_index):
		df.to_csv(FileName + '.csv', index=include_index, encoding='utf-8')
	
	def createDataSetDict(self):
		dataSetLst = self.sciDB.UniqueDataSets()
		DataSetDict = {}
		for n, set in enumerate(sorted(dataSetLst)):
			DataSetDict[str(n)] = set
		return DataSetDict
			
	def Debugging(self):
		self.DebuggingMode = not self.DebuggingMode
		print('Debuggin mode = ', self.DebuggingMode)
		
	def exectuteCommand(self, command):
		# using the user input as a key, gets the corresponding value from the 
		# commandDict.  The value is a list that corresponds to a given command
		# The list is formatted as follows: [self.method, "Command description"]
		# If the key is not found "bad input" the user is given an
		# invalid command feedback statement.
		method = self.commandDict.get(command.lower(), 'Invalid Command')
		
		if method != 'Invalid Command':
			method[0]()
		else:
			self.giveUserFeedback('Invalid Command\nFor a list of the commands type "help"')
		
app = Controls()
app.giveUserFeedback('\n\n\n\n\n\nWelcome to SciData\nBelow is the list of commands.')
app.basicInstructions()
app.initialize()

while(app.run()):
	app.runUserCommand("Enter Command")

	
	
	
	
	