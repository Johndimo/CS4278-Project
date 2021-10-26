#!/usr/bin/env python
# coding: utf-8

# In[22]:


import pandas as pd
from sklearn.manifold import TSNE
import xlwings as xw
from sklearn.cluster import DBSCAN
from bioinfokit.visuz import cluster
import plotly.express as px
import math
import numbers
import datetime
from pandas.api.types import is_numeric_dtype

class TsnePlot:
    #Declare class variables
    path = ""
    shapeCol = ""
    colorCol = ""
    df = []
    ID = []
    
    #Constructor with given file path
    def __init__(self, newPath):
        #Open file and extract contents
        self.path = newPath
        app = xw.App(visible = False)
        book = xw.Book(self.path)
        sheet = book.sheets('Master corrected variables')
        self.df = sheet.range('A1').options(pd.DataFrame, expand='table').value
        book.close()
        app.quit()
        
        #Get first column as identifiers and fill N/A values
        self.ID = self.df.index.values
        self.df = self.df.fillna('')
        self.df = self.df.loc[:,~self.df.columns.duplicated()]
        
    
    #Set output plot columns
    def setOutputColumns(self, sCol, cCol):
        self.shapeCol = sCol
        self.colorCol = cCol
    
    def getColumns(self):
        return list(self.df)
    
    def standardize(self, dicts):
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
        return df2
                    
    def getDicts(self):
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
    
    def generateResults(self, df2):
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
        return df_results
    
    def getFigure(self, df_results):
        fig = px.scatter(df_results, x="x", y="y", color=self.colorCol, symbol=self.shapeCol, hover_data=["ID"])
        fig.update_traces(marker={'size': 7, 'line' : {'color' : 'rgba(0, 0, 0, 0.5)',
                                           'width' : 1}})

        fig.layout.legend.y = 1.05
        fig.layout.legend.x = 1.035
        fig.layout.coloraxis.colorbar.y = 0.35
        return fig

    def getPlot(self):

        dicts = self.getDicts()

        df2 = self.standardize(dicts)


        df_results = self.generateResults(df2)

        fig = self.getFigure(df_results)

        return fig


# In[23]:





# In[ ]:





# In[ ]:




