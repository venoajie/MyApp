# -*- coding: utf-8 -*-

# built ins
from loguru import logger as log

def check_outliers (df, cols: str = None)-> None:

    """
    https://stackoverflow.com/questions/35827863/remove-outliers-in-pandas-dataframe-using-percentiles
        """

    
    if cols !=None:
        cols =[cols]
        
        log.debug (df[cols])
        Q1 = df[cols].quantile(0.25)
        Q3 = df[cols].quantile(0.75)
        IQR = Q3 - Q1
        log.info (f'{Q1=}')
        log.info (f'{Q3=}')
        log.info (cols)

        return df[~((df[cols] < (Q1 - 1.5 * IQR)) |(df[cols] > (Q3 + 1.5 * IQR))).any(axis=1)]
        
    else:
            
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1

        
        log.info (Q1)
        log.info (Q3)
        return df[~((df < (Q1 - 1.5 * IQR)) |(df > (Q3 + 1.5 * IQR))).any(axis=1)]

def outlier(df, col_name):

    """
    https://stackoverflow.com/questions/72945801/how-to-correctly-check-if-theres-at-least-one-outlier-in-a-ohlc-price-series-on
    """
    import numpy as np
    
    q1 = np.percentile(np.array(df[col_name].tolist()), 25)
    q3 = np.percentile(np.array(df[col_name].tolist()), 75)
    IQR = q3 - q1
                      
    Q3 = q1+(3*IQR)
    Q1 = q3-(3*IQR)
    outlier_num = 0
                    
    
    log.info (f'{q1=}')
    log.info (f'{q3=}')

    for value in df[col_name].values.tolist():
        if (value < Q1) | (value > Q3):
            print(f'the outlier value is {value}')
            outlier_num +=1
    return Q1, Q3, outlier_num
            
        
if __name__ == "__main__":

 
    try:

        # DBT Client ID
        resp = [10,20,30]
        #curr = (resp)[-3:]#[:3]
        instrument = check_outliers (resp)
        print (instrument)

    except Exception as error:
        print (error)

    
