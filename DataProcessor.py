import pandas as pd
import statistics
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

class Calculator():
	def __init__(self):
		self.sensitivity_threshold = 0.5
		self.T_Table_99Confidence = {1: 31.82, 2: 6.965, 3: 4.541, 4: 3.747, 5: 3.365, 6: 3.143, 7: 2.998, 8: 2.896, 9: 2.821, 10: 2.764, 
									11: 2.718, 12: 2.681, 13: 2.650, 14: 2.624, 15: 2.602, 16: 2.583, 17: 2.567, 18: 2.552, 19: 2.539, 20: 2.528}
		self.color_codes = ['#1a1aff', '#00cc00', '#a300cc', '#808000', '#527a7a', '#663300', '#33ff33', '#ff8080']
		self.red_hex_code = '#ff0000'
	
	def SensitivityFinder(self, df):
		found_ratio_series = df.apply(self.AnalyteFoundRatio, axis=1)
		df['FoundRatio'] = found_ratio_series
		df_passing_ratios = df[df['FoundRatio'] >= self.sensitivity_threshold]
		return df_passing_ratios['Conc_pg'].min()
		
	def AnalyteFoundRatio(self, row):
		found_ratio = row['Count']/row['Repetitions']
		return found_ratio
		
	def calculate_IDL(self, data_lst, Concentration):
		DegreesOfFreedom = len(data_lst) - 1
		Ta = self.T_Table_99Confidence.get(DegreesOfFreedom, "TooMany")
		if Ta == "TooMany":
			raise Exception('There are more than 21 data values for the IDL calculation and therefore not enough degrees of freedom in T_Table_99Confidence dictionary.')
		Averge = statistics.mean(data_lst)
		StandardDeviation = statistics.stdev(data_lst)
		RSD = (StandardDeviation/Averge) * 100
		return round(((Ta * RSD * Concentration)/100),2)
		
	def Lowest800Similarity(self, df):
		df_Similarity_GreaterThan_800 = df[df['Ave_Similarity'] >= 800]
		return df_Similarity_GreaterThan_800['Conc_pg'].min()
	
	def BuildSimilarity_PlotsTables(self, df, data_sets, analyte_name):
		SpectralDict = self.SliceFilterSpectralDF(df, data_sets, analyte_name)
		self.SimilarityPlot(SpectralDict)
		self.SimilarityTable(SpectralDict)
	
	def SimilarityPlot(self, SpectralDict):
		fig = plt.figure(figsize=(18,9))
		
		# Add each data set to the Spectral Qualithy Plot
		for n, data_set in enumerate(SpectralDict['data_sets']):
			plt.scatter(SpectralDict['x_data'][n], SpectralDict['y_data'][n], color=self.color_codes[n], label=data_set)

		# Horizontal 800 Similarity line
		plt.axhline(y=800, xmin=0, xmax=1, hold=None, color=self.red_hex_code, label='800 Similarity')
		
		# Make your plot pretty
		plt.legend(loc='upper left')
		plt.ylabel('Similarity vs. Main NIST Hit')
		plt.xlabel('Concentration (pg)')
		plt.title('%s - Spectral Quality' % SpectralDict['analyte_name'])
		plt.xscale('log')
		plt.xlim(SpectralDict['x_axis_min'], SpectralDict['x_axis_max'])
		plt.savefig(SpectralDict['file_name'], bbox_inches='tight')
		
	def SimilarityTable(self, SpectralDict):
		df1 = pd.DataFrame()
		for n, df in enumerate(SpectralDict['df_data_set']):
			df2 = df.pivot_table(values='Similarity', index='Conc_pg', aggfunc=np.mean)
			df2 = df2.rename(columns ={'Similarity': SpectralDict['data_sets'][n]})
			df1 = pd.concat([df1, df2], axis=1)
		
		print(df1)
		
	def SliceFilterSpectralDF(self, df, data_sets, analyte_name):
		# slices and filters df to get x and y data
		# then adds to spectral dictionary. Also, builds
		# png file name based on analyte name and set names
		
		# Initialize SpectralDict & create file name
		SpectralDict = {'x_data': [], 'y_data': [], 'analyte_name': analyte_name, 'data_sets': data_sets, 'df_data_set': []}
		SpectralDict['file_name'] = '%s_SpectralQuality_%s.png' % (analyte_name, "_".join(data_sets))
		
		# X-axis Max Value
		Conc_pg_max = df['Conc_pg'].max()
		SpectralDict['x_axis_max'] = (Conc_pg_max * 0.25) + Conc_pg_max
		
		# X-axis Max Value
		Conc_pg_min = df['Conc_pg'].min()
		SpectralDict['x_axis_min'] = Conc_pg_min - (Conc_pg_min * 0.25)
		
		for data_set in data_sets:
			df_data_set = df[df['DataSet'] == data_set]
			SpectralDict['df_data_set'].append(df_data_set)
			SpectralDict['y_data'].append(df_data_set['Similarity'])
			SpectralDict['x_data'].append(df_data_set['Conc_pg'])
		
		return SpectralDict
			
	def BuildQuantCurves(self, df):
		# http://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
		analytes_lst = df['AnalyteName'].value_counts().index
		
		for analyte in analytes_lst:
			analyte_df = df[df['AnalyteName'] == analyte]
			data_sets = analyte_df['DataSet'].value_counts().index
			file_name = analyte + "-QuantCurve-" + '+'.join(data_sets)
			
			# Calculate axis scalers
			x_max = analyte_df['Conc_pg'].max()
			x_max += (x_max * 0.25)
			
			x_min = analyte_df['Conc_pg'].min()
			x_min -= (x_min * 0.25)
			
			y_max = analyte_df['Area'].max()
			y_max += (y_max * 0.25)
			
			y_min = analyte_df['Area'].min()
			y_min -= (y_min * 0.25)
			
			fig = plt.figure(figsize=(18,9))
			
			for n, data_set in enumerate(data_sets):
				DataSet_df = analyte_df[analyte_df['DataSet'] == data_set]
				x_values = DataSet_df['Conc_pg']
				y_values = DataSet_df['Area']
				plt.scatter(x_values, y_values, color=self.color_codes[n], label=data_set)
				
			plt.legend(loc='upper left')
			plt.ylabel('Integrated Area')
			plt.xlabel('Concentration (pg)')
			plt.title('%s Linearity' % analyte)
			plt.xlim(x_min, x_max)
			plt.ylim(y_min, y_max)
			plt.savefig(file_name, bbox_inches='tight')
			
			
			
		