import win32com.client
import os

class Macros():

	def __init__(self, MacroContainingExcelFilePath, VBAModule):
		self.ExcelMarcoFilePath = MacroContainingExcelFilePath
		excel_file = os.path.basename(MacroContainingExcelFilePath)
		self.Macro_Prefix = excel_file + "!" + VBAModule + "."
		self.xl = win32com.client.Dispatch("Excel.Application")
		self.xl.Visible = False
	
	def BuildPrettyTableWorkbook(self, *args):
		# args[0] the comma seperated csv file string
		# args[1] file path/name with file extension to save resulting Pretty Table workbook 
		Macro_Name = self.Macro_Prefix + "ConvertCSVToPrettyTables"
		self.xl.Workbooks.Open(Filename=self.ExcelMarcoFilePath)
		self.xl.Application.Run(Macro_Name, args[0], args[1])
		self.xl.Quit()
		