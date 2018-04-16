import sqlite3
import pandas as pd
import time

class SciDatabase():
	def __init__(self, filepath, factTableColumns, analyteTableColumns):
		self.filepath = filepath
		self.conn = sqlite3.connect(self.filepath)
		self.cur = self.conn.cursor()
		sampleTable = 'Sample'	
		
		self.Analyte_Foreignkey_Cols = [col for col in factTableColumns if col.endswith('_foreignkey')]
		self.Analyte_Foreignkey_Cols.remove('DataSetConcentrations_foreignkey')
		
		DataSetAttributesTable = 'DataSetConcentrations'
		DataSetAttributesColumns = ['id', 'Concentration_pg', 'Repetitions']
		
		analyteTables = [col.replace('_foreignkey','') for col in self.Analyte_Foreignkey_Cols if col.endswith('_foreignkey')]
									
		self.schema = {sampleTable: factTableColumns, DataSetAttributesTable: DataSetAttributesColumns}
		for table in analyteTables:
			self.schema[table] = analyteTableColumns
		
	def getTables(self):
		#returns a tuple list with all the table names from a given db connection
		self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		return self.cur.fetchall()
		
	def getColumns(self, table):
		#returns a tuple list with all the column names from a given db connection
		column_query = self.conn.execute('SELECT * from %s' % table)
		x = [description[0] for description in column_query.description]
		return [description[0] for description in column_query.description]
		
	def closeDBConnection(self):
		self.conn.close()
		
	def CommitDB(self):
		self.conn.commit()
		
	def load_DataFrame(self, df, table_name):
		df.to_sql(table_name, self.conn, if_exists="append")
		
	def load_Data(self, df, table_name):
		#executemany - I couldn't for the life of me get executemany to work...?
		# http://jpython.blogspot.com/2013/11/python-sqlite-example-executemany.html
		data, columns = self.createListOfTuples(df, table_name)
		
		for row in data:
			try:
				self.conn.execute("INSERT INTO %s %s VALUES %s" % (table_name, columns, row))
			except sqlite3.IntegrityError:
				print("Record Overwritten\n\tTable: %s\n\tID: %s\n" % (table_name, row[0]))
				self.conn.execute("DELETE FROM %s WHERE id = '%s'" % (table_name, row[0]))
				self.conn.execute("INSERT INTO %s %s VALUES %s" % (table_name, columns, row))
			
	def createListOfTuples(self, df, table_name):
		# creates a list of tuples, each tuple is a row of data from the DataFrame
		# create a tuple of each column correspond to the columns names in the DataFrame
		
		data = []
		for index, row in df.iterrows():
			data.append(tuple(row[self.schema[table_name]].tolist()))
			
		return data, tuple(self.schema[table_name])
		
	def clearDB(self):
		
		for key_table, value in self.schema.items():
			self.conn.execute("DELETE FROM %s" % key_table)	
	
	def UniqueDataSets(self):
		# Returns a list of strings containing all the unique DataSetNames
		# From the Sample table so the the use can query which data sets
		# have been uploaded.
		sql_statement = "SELECT DISTINCT(DataSetName) FROM Sample"
		cursor = self.conn.execute(sql_statement)
		query_lst = cursor.fetchall()
		if query_lst == []:
			return ['Database is currently empty']
		else:
			return [str("%s" % x) for x in query_lst]
	
				
	def SensitivityQuery(self, table, data_set):
		# Returns the number of times an analyte is found at each concentration and the
		# number of repetitions in a particular data set.
		sql_statement = "SELECT COUNT(%s.id) AS Count, %s.Concentration_pg AS Conc_pg, \
							DataSetConcentrations.Repetitions AS Repetitions \
						FROM \
							Sample \
						INNER JOIN %s ON \
							%s.id = Sample.%s_foreignkey \
						INNER JOIN DataSetConcentrations ON \
							DataSetConcentrations.id = Sample.DataSetConcentrations_foreignkey \
						WHERE \
							Sample.DataSetName = '%s' \
						GROUP BY \
							Conc_pg \
						ORDER BY \
							Conc_pg;" % (table, table, table, table, table, data_set)
		return pd.read_sql_query(sql_statement, self.conn)
		
	def DataSetAnalytes(self, data_set, TableProcessingToReturn='Both_PeakFinding_TargetAnalyteFinding'):
		# Query all foreign key columns in Sample table and return a list of all analyts that are
		# found in a given data set.
		column_string = self.createQueryColumnsStr(TableProcessingToReturn)
				
		# Build SQL statement & Query sample table for all foreign key columns of a given data set
		sql_statement = "SELECT %s FROM Sample WHERE Sample.DataSetName = '%s';" % (column_string, data_set)		
		df = pd.read_sql_query(sql_statement, self.conn)
		
		return self.GetFoundAnalytesLst(df)
		
	def createQueryColumnsStr(self, TableProcessingToReturn):

		if TableProcessingToReturn == 'PeakFindingOnly':
			col_ends_with = '_PF_foreignkey'
		elif TableProcessingToReturn == 'TargetAnalyteFindingOnly':
			col_ends_with = '_TAF_foreignkey'
		elif TableProcessingToReturn == 'Both_PeakFinding_TargetAnalyteFinding':
			col_ends_with = '_foreignkey'
			
		QueryColumnsLst = [col for col in self.Analyte_Foreignkey_Cols if col.endswith(col_ends_with)]
		
		return " ,".join(QueryColumnsLst)
		
	def GetFoundAnalytesLst(self, df):
		# Checks each column of the df, each one contains at least one value that != "NotFound";
		# the corresponind analyte table string is appended to the list which gets returned
		analyte_table_ids = df.columns
		analytes_found = []
		analyte_tables = []
		
		for col in analyte_table_ids:
			table_id_value_counts_dict = df[col].value_counts().to_dict()
			NotFoundCount =  table_id_value_counts_dict.get('NotFound', 0)
			
			# Removes '_foreignkey' from Sample table analyte foreignkey column
			# to get analyte table name.
			if df[col].shape[0] != NotFoundCount:
				index = col.index('_foreignkey')
				analyte_table = col[:index]
				analyte_tables.append(analyte_table)
				
				# Revmoves '_PF' or '_TAF' from table analyte name to get analyte name.
				if analyte_table.endswith('_PF'):
					analytes_found.append(analyte_table[:-3])
				elif analyte_table.endswith('_TAF'):
					analytes_found.append(analyte_table[:-4])
				
		return list(set(analytes_found)), analyte_tables
		
	def GetAnalyteNameAndProcessingType(self, table):
		sql_statement = "SELECT AnalyteName, ProcessingType FROM %s GROUP BY 1,2" % table
		cursor = self.conn.execute(sql_statement)
		query_lst = cursor.fetchall()
		return str("%s" % query_lst[0][0]), str("%s" % query_lst[0][1]) 
		
	def Get_100fgArea(self, table, data_set):
		sql_statement = "SELECT %s.Area AS Area_100fg \
						FROM \
							Sample \
						Inner Join %s ON \
							%s.id = Sample.%s_foreignkey \
						WHERE \
							Sample.DataSetName = '%s' AND \
							%s.Concentration_pg = 0.1;"  % (table, table, table, table, data_set, table)
							
		return pd.read_sql_query(sql_statement, self.conn)
		
	def GetAveSimilarities(self, table, data_set):
		sql_statement = "SELECT AVG(%s.Similarity) AS Ave_Similarity, %s.Concentration_pg AS Conc_pg \
						FROM \
							Sample \
						Inner Join %s ON \
							%s.id = Sample.%s_foreignkey \
						WHERE \
							Sample.DataSetName = '%s' \
						GROUP BY Conc_pg;"  % (table, table, table, table, table, data_set)
							
		return pd.read_sql_query(sql_statement, self.conn)
		
	def Similarities(self, table, data_sets):
		# This query provides all the data to create the Concentration vs Similarity plot and tables 
		#condition = "DataSet = '" + "' OR DataSet = '".join(data_sets) + "' "
		condition = self.CreateConditionClause_OrSeriesStr(data_sets)
			
		sql_statement = "SELECT %s.Similarity AS Similarity, %s.Concentration_pg AS Conc_pg, \
							Sample.Instrument AS SerNo, Sample.DataSetName AS DataSet \
						FROM \
							Sample \
						Inner Join %s ON \
							%s.id = Sample.%s_foreignkey \
						WHERE \
							%s \
						ORDER BY SerNo, Conc_pg ASC;"  % (table, table, table, table, table, condition)
						
		return pd.read_sql_query(sql_statement, self.conn)
		
	def GetChromatography(self, data_set):
		sql_statement = "SELECT DISTINCT(Chromatography) \
						FROM \
							Sample \
						WHERE \
							Sample.DataSetName = '%s'"  % data_set				
		cursor = self.conn.execute(sql_statement)
		query_lst = cursor.fetchall()
		return str("%s" % query_lst[0])
				
	def GetQuantCurveData(self, table, data_sets):
		# This query provides all the data to create the Concentration vs Similarity plot and tables
		condition = self.CreateConditionClause_OrSeriesStr(data_sets)
			
		sql_statement = "SELECT %s.Area AS Area, %s.Concentration_pg AS Conc_pg, \
							%s.AnalyteName AS AnalyteName, Sample.DataSetName AS DataSet \
						FROM \
							Sample \
						Inner Join %s ON \
							%s.id = Sample.%s_foreignkey \
						WHERE \
							%s \
						ORDER BY DataSet, Conc_pg ASC;"  % (table, table, table, table, table, table, condition)
						
		return pd.read_sql_query(sql_statement, self.conn) 
		
	def ClearDataSetData(self, data_sets, analyte_table_lst):
		# Clears all the data from the database for the define data sets
		
		# append the DataSetConcentrations table so it too will be included in the data clearing
		analyte_table_lst.append('DataSetConcentrations')
		
		# Create a single string that contains all the forigen keys in the sample table
		# that has data to be removed (which is comma space delimited)
		ForeignKeyColumn_lst = [col + '_foreignkey' for col in analyte_table_lst]
		ForeignKeyColumn_Columns = ', '.join(ForeignKeyColumn_lst)
		
		# Get condition string from data sets
		data_set_condition = self.CreateConditionClause_OrSeriesStr(data_sets, "DataSetName")
		
		# Resulting df: columns correspond to tables that contain data to be removed, the values in each column
		# are the primary keys of records within that table that need to be deleted.
		sql_statement = 'SELECT %s FROM Sample WHERE %s;' % (ForeignKeyColumn_Columns, data_set_condition)
		df = pd.read_sql_query(sql_statement, self.conn)
		df.columns = analyte_table_lst
		
		# Iterate through the dataframe by column to delete each record from the db
		# note: column = table name
		for column in df:
			condition = self.CreateConditionClause_OrSeriesStr(set(df[column]), "id")
			self.conn.execute('DELETE FROM %s WHERE %s' % (column, condition))
		
		# Finally remove the defined records from the sample table as well
		self.conn.execute('DELETE FROM Sample WHERE %s' % data_set_condition)
		self.CommitDB()
	
	def CreateConditionClause_OrSeriesStr(self, data_sets, DataSetColumnName='DataSet'):
		# Creates the following string using the data_set list
		# Example string: DataSetColumnName = 'SomeDataSetName_1' OR DataSetColumnName = 'SomeDataSetName_2' ... n
		# If only one element is in the list it will return DataSetColumnName = 'SomeDataSetName_1'
		str1 = "' OR %s = '" % DataSetColumnName
		str2 = "%s = '" % DataSetColumnName
		return str2 + str1.join(data_sets) + "' "
		
	def GetRepsAtEachConcentration(self, analyte_table_lst, data_set):
		df = pd.DataFrame()
		for table in analyte_table_lst:
			sql_statement = "SELECT \
								%s.Concentration_pg AS Conc, COUNT(%s.Concentration_pg) AS %s \
							FROM \
								Sample \
							Inner Join %s ON \
								%s.id = Sample.%s_foreignkey \
							WHERE \
								DataSetName = '%s' \
							GROUP BY 1 \
							ORDER BY 1 ASC;" % (table, table, table, table, table, table, data_set)
			df1 = pd.read_sql_query(sql_statement, self.conn)
			df1.set_index('Conc', inplace=True)
			
			df = pd.concat([df, df1], axis=1)
		
		return df
		
	def AddAnalyteToDatabase(self, new_analyte):
		# Appends the database with the new analyte
		
		# Adds a 
		self.conn.execute("ALTER TABLE Sample ADD Column %s_TAF_foreignkey TEXT" % new_analyte)
		self.conn.execute("ALTER TABLE Sample ADD Column %s_PF_foreignkey TEXT" % new_analyte)
		self.CommitDB()
		
		self.conn.execute("UPDATE Sample SET %s_TAF_foreignkey = 'NotFound'" % new_analyte)
		self.conn.execute("UPDATE Sample SET %s_PF_foreignkey = 'NotFound'" % new_analyte)
		
		self.conn.execute("CREATE TABLE %s_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,\
			Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER, \
			Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL,\
			Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT)" % new_analyte)
			
		self.conn.execute("CREATE TABLE %s_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER, \
			Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER, \
			Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, \
			Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT)" % new_analyte)
		
		self.CommitDB()		
		
		
		
		