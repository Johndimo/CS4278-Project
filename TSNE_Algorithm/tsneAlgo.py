#!/usr/bin/env python
# coding: utf-8

# In[26]:


import pandas as pd
from sklearn.manifold import TSNE
import xlwings as xw
import plotly.express as px
import math
import numbers
import datetime
from pandas.api.types import is_numeric_dtype
import numpy as np

class TsnePlot:
    """Initialize class variables to default values

    """
    path = ""
    shapeCol = ""
    colorCol = ""
    df = []
    ID = []
    sheets = []
    priorityCols = []
    weight = 5
    df_results = []
    
    
    def __init__(self, newPath):
        """Initializes a new TsnePlot by trying to set the path

        :param newPath: the path to the excel file
        """
        self.setPath(newPath)
            
    def setPath(self, newPath):
        """Tries to set the path of the excel file, if it is found.
           Will also store the sheets of the file if found.

        :param newPath: the path to the excel file
        """
        try:
            app = xw.App(visible = False)
            book = xw.Book(newPath)
            for sheet in book.sheets:
                self.sheets.append(sheet.name)
            book.close()
            app.quit()
            self.path = newPath
        except Exception:
            print('Path not found')
        
        
    def setSheet(self, sheetName):
        """Sets the current sheet, if the sheet name is valid

        :param sheetName: the name of the sheet to be set
        """
        if len(self.path) > 0:
            try:
                self.sheet = sheetName
                app = xw.App(visible = False)
                book = xw.Book(self.path)

                sheet = book.sheets(sheetName)
                self.df = sheet.range('A1').options(pd.DataFrame, expand='table').value
                book.close()
                app.kill()


                self.df = self.df.fillna('')
                self.df = self.df.loc[:,~self.df.columns.duplicated()]
                self.ID = self.df.index.values
            except Exception:
                print('Sheet not found')
        else:
            print('Path not set')
    
    def getSheets(self):
        """Gets the list of sheets, stored from the workbook
        
        :returns: the list of sheets
        """
        return self.sheets
    
    def setOutputColumns(self, sCol, cCol):
        """Sets the columns to be shown as shape and color scales on the output graph, if valid columns

        :param sCol: the shape output column name
        :param cCol: the color output column name
        """
        
        columns = self.getColumns()
        try:
            if sCol in columns and cCol in columns:
                self.shapeCol = sCol
                self.colorCol = cCol
            else:
                raise()
        except Exception:
            print("Invalid output columns")
    
    def getColumns(self):
        """Gets the columns of the data, if the data has been set
        
        :returns: the list of columns if data has been stored, or 'None' if not 
        """
        if len(self.df) > 0:
            return list(self.df)
        else:
            print('Columns not found')
            return None
    
    def setPrioCols(self, newCols):
        """Sets the columns to prioritize when running the algorithm

        :param newCols: the list of columns to prioritize
        """
        
        self.priorityCols = newCols
    
    def standardize(self, dicts):
        """Standardizes the data and weights the priority columns

        :param dicts: the dictionary of unique numbers that represent each piece of data stored in the dataframe
        :returns: the standardized and weighted dataframe of numbers and dates if data has been set, 'None' if not
        """
        if len(self.df) > 0:
            df2 = self.df

            i = 0
            for item in dicts:
                if not is_numeric_dtype(self.df[item]):
                    replacement = {item: dicts[item]}
                    df2 = df2.replace(replacement)
                i = i + 1


            for column in df2:
                df2[column] = df2[column].fillna(0)
                if not isinstance(df2[column][0],datetime.datetime):
                    if df2[column].std() != 0:
                        df2[column] = (df2[column] - df2[column].mean()) / df2[column].std()
                    if column in self.priorityCols:
                        df2[column] = df2[column] * self.weight

            return df2
        else:
            print('Data has not been set, cannot run standarize()')
            return None
                    
    def getDicts(self):
        """Gets the dictionary of dictionaries that stores the unique values (and dummied values for non-numeric columns)
           for each column of the dataframe, if set
           
        :returns: the final resultant dictionary if data has been stored, 'None' if not
        """
        if len(self.df) > 0:
            columns = list(self.df)
            columnNumber = 0
            dicts = {}
            for column in self.df:
                i = 1
                thisDict = {}
                uniques = self.df[column].unique()
                for item in uniques:
                    if not item in thisDict:
                        if isinstance(item, numbers.Number):
                            thisDict[item] = item
                        else:
                            if i in uniques:
                                j = i
                                while j not in uniques:
                                    j = j + 1
                                thisDict[item] = j
                            else:
                                thisDict[item] = i
                                i = i + 1
                dicts[columns[columnNumber]] =  thisDict
                columnNumber = columnNumber + 1
            return dicts
        else:
            print('Data has not been set, cannot run getDicts()')
            return None
        
            
    def generateResults(self, df2):
        """Runs the TSNE algorithm and stores results in df_results as long as the algorithm has not been run yet

        :param df2: the fitted dataframe as input for the algorithm
        """
        
        if len(self.df_results) == 0:
            tsne_em = TSNE(n_components=2, perplexity=38.0, n_iter=5000, verbose=1).fit_transform(df2)

            df_results = self.df
            df_results['x'] = tsne_em[:,0]
            df_results['y'] = tsne_em[:,1]
            df_results['ID'] = self.ID
            for row in df_results:
                df_results[row] = df_results[row].astype(float, errors = 'ignore')
            df_results['dob'] = df_results['dob'].astype(object)

            df_results.drop(df_results.loc[df_results['DM']=='null'].index, inplace=True)

            df_results = df_results.apply(pd.to_numeric, errors='ignore')
            self.df_results = df_results
            
        else:
            print("You have run the algorithm already.")
            print("If you want to view using different columns, set the columns and run getFigure().")
        
    
    def getFigure(self):
        """Formats the output graph with the output columns if the class has result data stored

        :returns: the figure if data has been set, 'None' if not
        """
        try:
            if len(self.df_results) > 0:
                if len(self.shapeCol) == 0:
                    self.shapeCol = self.getColumns[0]
                if len(self.colorCol) == 0:
                    self.colorCol = self.getColumns[0]


                symbolOut = self.shapeCol
                colorOut = self.colorCol
                if isinstance(self.df_results[self.shapeCol][0],datetime.datetime):
                    name = self.shapeCol + " as Number"
                    self.df_results[name] = self.df_results[self.shapeCol].map(pd.Series(data=np.arange(len(self.df_results)), index=self.df_results[self.shapeCol].values).to_dict())
                    symbolOut = name
                if isinstance(self.df_results[self.colorCol][0],datetime.datetime):
                    name = self.colorCol + " as Number"
                    self.df_results[name] = self.df_results[self.colorCol].map(pd.Series(data=np.arange(len(self.df_results)), index=self.df_results[self.colorCol].values).to_dict())
                    colorOut = name

                fig = px.scatter(self.df_results, x="x", y="y", color=colorOut, symbol=symbolOut, hover_data=["ID"])
                fig.update_traces(marker={'size': 7, 'line' : {'color' : 'rgba(0, 0, 0, 0.5)',
                                                   'width' : 1}})

                fig.layout.legend.y = 1.05
                fig.layout.legend.x = 1.035
                fig.layout.coloraxis.colorbar.y = 0.35
                return fig
            else:
                print('You have not run the algorithm yet.')
                return None
        except:
            return None

    def getPlot(self):
        """Links the workflow of the class together to produce the output
        
        :returns: the output figure 
        """
        if len(self.df_results) == 0:
            dicts = self.getDicts()

            df2 = self.standardize(dicts)


            self.generateResults(df2)

        fig = self.getFigure()

        return fig

