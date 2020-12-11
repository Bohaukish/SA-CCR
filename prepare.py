# This script is used to do some preparations before heading into EAD calculations
# As we all know, value of EAD is determined by Replacement cost(RC) and Potential
# Future Exposure(PFE). As a result, I will prepare data and some useful functions 
# in this script.

import pandas as pd
import numpy as np
from scipy.stats import norm
import logging


# In[Position]: Determine Buy or Sell position
def Position(df):
    
    """
    Used to determine Buy/Sell Positions for each records
    
    """
    
    # For option product, if we can short primary risk, then we can consider: Buy put
    # For option product, if we can short primary risk, then we can consider: Buy Call
    if (df['OPTION TYPE'] == "PUT" or df['OPTION TYPE'] == "CALL") and \
                             df['START_DATE'] != 0:
        df['POSITION'] = 'BUY'
    
    # For Interest Rate Swap, if we pay fix rate then we consider: buy
    # For Interest Rate Swap, if we pay fix rate then we consider: Sell
    else:
        if df['PAY_LEG'] == 'Fix' and df['RECEIVE_LEG'] == 'Floating':
            df['POSITION'] = 'BUY'
        elif df['PAY_LEG'] == 'Floating' and df['RECEIVE_LEG'] == 'Fix':
            df['POSITION'] = 'SELL'
    
    # In the real situation, we have many special cases.    
        else:
            df['POSITION'] = 'Please Check with Trader'
    
    return df
	

# In[sup_delta]: Calculate Supervisory Delta
def sup_delta(df):
    
    """
    This function is to compute delta value
    Inputs:
        Interest Rate DataFrame
    output:
        Supervisory delta for each transactions
    """
    
    # calculate delta value according to option's type and position
    if df['PRODUCT'] == 'European swaption' and df['START_DATE'] != 0:
        # Black Shcoles Delta formula only apply for option products
        
        d1 = (np.log(df['PRICE']/df['STRIKE']) + (np.square(df['VOLATILITY'])/2)*\
                          df['START_DATE'])/(df['VOLATILITY']/np.sqrt(df['START_DATE']))
        
        # Calculate Put Supervisory Delta
        if df['OPTION TYPE'] == 'PUT':
            if df['POSITION'] == 'BUY':
                df['SUPERVISORY_DELTA'] = -norm.cdf(-d1)
            else:
                df['SUPERVISORY_DELTA'] = norm.cdf(-d1)
                
        # Calculate Call Supervisory Delta       
        if df['OPTION TYPE'] == 'CALL':
            if df['POSITION'] == 'BUY':
                df['SUPERVISORY_DELTA'] = norm.cdf(d1)
            else:
                df['SUPERVISORY_DELTA'] = -norm.cdf(d1)
    
    # Supervisory Delta for Interest rate Swap
    else:
        if df['POSITION'] == 'BUY':
            df['SUPERVISORY_DELTA'] = 1
        else:
            df['SUPERVISORY_DELTA'] = -1
            
    return df

# In[adjusted_notional]: Calculate Adjusted Notional
def adjusted_notional(table):
    
    """
    This function is to compute adjusted notional amount and supervisory duration
    
    Input: 
        table: netting set infomation
    
    outputs:
        Revised table: with Supervisory Duration and Adjusted Notional added
    """
    
    #abstract start date and end date:
    S = table['START_DATE']
    E = table['END_DATE']
    
    #supervisory duration calculation based on S and E 
    table['SUPERVISORY_DURATION'] = (np.exp(-0.05*np.array(S)) - \
                                         np.exp(-0.05*np.array(E)))/0.05

    table['ADJUSTED_NOTIONAL'] = table['TRADE_NOTIONAL']*table['SUPERVISORY_DURATION']*table['RATE']
    return table


# In[effective]: Calculate effective Notional
def effective(df):
    
    """
    This function is to compute the effective notional value for each hedging set
    
    Inputs:
        D is a list which consists:
            D1: effective notional for bucket 1
            D2: effective notional for bucket 2
            D3: effective notional for bucket 3
        offset: True means banks choose to recognise offset across maturity buckets
        
    Output:
        e_notional: total effective notional amount within a bucket
    
    """
    
    # effective notonal amount for each bucket (1,2,3)
    D1 = df[df['TIME_BUCKET'] == 1]['EFFECTIVE_NOTIONAL'].sum()
    D2 = df[df['TIME_BUCKET'] == 2]['EFFECTIVE_NOTIONAL'].sum()
    D3 = df[df['TIME_BUCKET'] == 3]['EFFECTIVE_NOTIONAL'].sum()
    
    base = np.square(D1)+np.square(D2)+np.square(D3)+1.4*D1*D2+1.4*D2*D3+0.6*D1*D3
    EFF_NOTIONAL = np.sqrt(base)
        
    df['EFF_NOTIONAL_HEGDE'] = EFF_NOTIONAL
    
    df['MTM_HEDGE'] = sum(df['MTM'])
    df['COLLATERAL_HEDGE'] = sum(df['COLLATERAL'])
    
    return df

    

    
    
    
    
    
    
    
    
    
    
		