import win32com.client
import os

class Macros():

	def __init__(self, ExcelFilePath, VBAModule):
		self.ExcelMarcoFilePath = ExcelFilePath
		excel_file = os.path.basename(ExcelFilePath)
# 		excel_file = ExcelFilePath.split('\\')[-1]
		self.Macro_Prefix = excel_file + "!" + VBAModule + "."
		self.xl = win32com.client.Dispatch("Excel.Application")
		self.xl.Visible = False
	
	def BuildPrettyTableWorkbook(self, csvFilesString, PrettyTablesWkBkFilePath):
		Macro_Name = self.Macro_Prefix + "ConvertCSVToPrettyTables"
		self.xl.Workbooks.Open(Filename=self.ExcelMarcoFilePath)
		self.xl.Application.Run(Macro_Name, csvFilesString, PrettyTablesWkBkFilePath)
		self.xl.Quit()
		