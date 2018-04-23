Attribute VB_Name = "VBA_Macros"
Sub ConvertCSVToPrettyTables(ByVal csvFileString As String, ByVal PrettyTablesWkBkFilePath As String)

Application.ScreenUpdating = False

Dim FinalWkbk As Workbook
Dim csvWkBk As Workbook

Dim csvFiles As Variant
Dim csvNo As Integer

Dim row As Integer
Dim BottomRow As Integer

    ' Create new workbook which will be the final
        Workbooks.Add
        Set FinalWkbk = ActiveWorkbook
        
    ' Parce comma delimited string to an array of csv file paths
        csvFiles = Split(csvFileString, ",")
    
    For Each csvFile In csvFiles
        ' Open csv File
        Workbooks.Open Filename:=csvFile
        Set csvWkBk = ActiveWorkbook
        
        ' Determine bottom row of the data set
        Range("A1").Select
        Selection.End(xlDown).Select
        BottomRow = ActiveCell.row + 5
        
        ' Move Table 2 columns left 5 rows down
        Columns("A:B").Select
        Selection.Insert Shift:=xlToRight, CopyOrigin:=xlFormatFromLeftOrAbove
        Rows("1:5").Select
        Selection.Insert Shift:=xlDown, CopyOrigin:=xlFormatFromLeftOrAbove
        
        ' Rename bottom level headers
        Range("C6").Value = "Conc (pg)"
        Range("D6").Value = "PV1"
        Range("E6").Value = "PV2"
        Range("F6").Value = "PV1"
        Range("G6").Value = "PV2"
        
        ' Merge cells and drop in top level headers
        Range("C5:C6").Merge
        Range("D5:E5").Merge
        Range("F5:G5").Merge
        Range("C4:G4").Merge
        Range("C4").Value = "Average Similarity"
        Range("D5").Value = "1D"
        Range("F5").Value = "GCxGC"
        
        ' Format headers
            ' Font size - 12
            ' Font color - white
            ' Inner Borders
            ' Fill - black
        Range("C4:G6").Select
        Call FormatHeaders
        
        ' Format data
            ' Fill - Alternating greys
            ' Borders - Group 1D & GCxGC
            ' Format numbers to show no decimals
        For row = 7 To BottomRow
            Range("C" & row & ":G" & row).Select
            If row Mod 2 = 1 Then
                Call OddDataRow
            Else
                Call EvenDataRow
            End If
        Next row
        
        Range("D7:E" & BottomRow & ",F7:G" & BottomRow).Select
        Call FormatSimilarityDataRows
        
        Range("C7:C" & BottomRow).Select
        Call FormatIndexDataRows
        
        ' Whole table formatting
            ' Center all text
            ' Heavy black border
        Range("C4:G" & BottomRow).Select
        Call WholeTableFormatting
        Cells(1, 1).Select
        
        ' Copy Pretty Table Sheet to Final workbook then close csv workbook
        ActiveSheet.Copy After:=FinalWkbk.Sheets(FinalWkbk.Sheets.Count)
        csvWkBk.Close False

    Next csvFile
    
    FinalWkbk.Close True, Filename:=PrettyTablesWkBkFilePath
End Sub

Private Sub FormatHeaders()
    With Selection.Font
        .Name = "Calibri"
        .FontStyle = "Bold"
        .Size = 12
        .Strikethrough = False
        .Superscript = False
        .Subscript = False
        .OutlineFont = False
        .Shadow = False
        .Underline = xlUnderlineStyleNone
        .ThemeColor = xlThemeColorDark1
        .TintAndShade = 0
        .ThemeFont = xlThemeFontMinor
    End With
    
    With Selection.Borders(xlEdgeBottom)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    
    With Selection.Borders(xlInsideVertical)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    
    With Selection.Interior
        .Pattern = xlSolid
        .PatternColorIndex = xlAutomatic
        .ThemeColor = xlThemeColorLight1
        .TintAndShade = 0
        .PatternTintAndShade = 0
    End With
End Sub

Private Sub OddDataRow()

    With Selection.Interior
        .Pattern = xlSolid
        .PatternColorIndex = xlAutomatic
        .ThemeColor = xlThemeColorDark1
        .TintAndShade = -0.149998474074526
        .PatternTintAndShade = 0
    End With
    

End Sub

Private Sub EvenDataRow()

    With Selection.Interior
        .Pattern = xlSolid
        .PatternColorIndex = xlAutomatic
        .ThemeColor = xlThemeColorDark1
        .TintAndShade = -0.349986266670736
        .PatternTintAndShade = 0
    End With

End Sub

Private Sub FormatSimilarityDataRows()

    Selection.NumberFormat = "0"
    
    With Selection.Borders(xlEdgeLeft)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    With Selection.Borders(xlEdgeTop)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    
    With Selection.Borders(xlEdgeRight)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    With Selection.Borders(xlInsideVertical)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlThin
    End With
    With Selection.Borders(xlInsideHorizontal)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlThin
    End With
    
End Sub

Private Sub FormatIndexDataRows()
    With Selection.Borders(xlEdgeTop)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    
    With Selection.Borders(xlEdgeRight)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlMedium
    End With
    
    With Selection.Borders(xlInsideHorizontal)
        .LineStyle = xlContinuous
        .ThemeColor = 1
        .TintAndShade = 0
        .Weight = xlThin
    End With
    
    Columns("C:C").ColumnWidth = 10

End Sub

Private Sub WholeTableFormatting()

    With Selection
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlBottom
        .WrapText = False
        .Orientation = 0
        .AddIndent = False
        .IndentLevel = 0
        .ShrinkToFit = False
        .ReadingOrder = xlContext
    End With
    
    With Selection.Borders(xlEdgeLeft)
        .LineStyle = xlContinuous
        .ColorIndex = xlAutomatic
        .TintAndShade = 0
        .Weight = xlThick
    End With
    With Selection.Borders(xlEdgeTop)
        .LineStyle = xlContinuous
        .ColorIndex = xlAutomatic
        .TintAndShade = 0
        .Weight = xlThick
    End With
    With Selection.Borders(xlEdgeBottom)
        .LineStyle = xlContinuous
        .ColorIndex = xlAutomatic
        .TintAndShade = 0
        .Weight = xlThick
    End With
    With Selection.Borders(xlEdgeRight)
        .LineStyle = xlContinuous
        .ColorIndex = xlAutomatic
        .TintAndShade = 0
        .Weight = xlThick
    End With
    
End Sub

