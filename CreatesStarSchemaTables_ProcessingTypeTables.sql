CREATE TABLE Sample (id TEXT PRIMARY KEY, Instrument CHARACTER(4), DataSetName TEXT,
	TuneAreaCounts, INTEGER, DetectorVoltage INTEGER, Sample TEXT, Chromatography TEXT, 
	SampleDateTime TEXT, OFN_TAF_foreignkey TEXT, OFN_PF_foreignkey TEXT, 
	Acenaphthene_TAF_foreignkey TEXT, Acenaphthene_PF_foreignkey TEXT, 
	Phenanthrene_TAF_foreignkey TEXT, Phenanthrene_PF_foreignkey TEXT, 
	Pyrene_TAF_foreignkey TEXT, Pyrene_PF_foreignkey TEXT, DataSetConcentrations_foreignkey TEXT,
	Chrysene_TAF_foreignkey TEXT, Chrysene_PF_foreignkey TEXT,
	Benzo_b_fluoranthene_TAF_foreignkey TEXT, Benzo_b_fluoranthene_PF_foreignkey TEXT, 
	Benzo_ghi_perylene_TAF_foreignkey TEXT, Benzo_ghi_perylene_PF_foreignkey TEXT);

CREATE TABLE OFN_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE OFN_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Acenaphthene_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Acenaphthene_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Phenanthrene_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Phenanthrene_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Pyrene_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Pyrene_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Chrysene_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Chrysene_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Benzo_b_fluoranthene_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Benzo_b_fluoranthene_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Benzo_ghi_perylene_TAF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE Benzo_ghi_perylene_PF (id TEXT PRIMARY KEY, ProcessingType TEXT, Area INTEGER,
	Height INTEGER, Peak_SN INTEGER, Quant_SN INTEGER,  
	Quant_Masses TEXT, RT_1D REAL, RT_2D REAL, Tailing_Factor REAL, FWHH REAL, 
	Similarity INTEGER, Concentration_pg REAL, AnalyteName TEXT);
	
CREATE TABLE DataSetConcentrations (id TEXT PRIMARY KEY, Concentration_pg REAL, Repetitions INTEGER);