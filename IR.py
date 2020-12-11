import pandas as pd
import numpy as np
from prepare import *


# In[Calculation]: Some preparation calculation 
def Calculation(IR):
    
    
    """
    This function is to determine Positions, supervisory delta and Adjusted Notional
    
    Inputs:
        IR DataFrame: input from IR.xlsx file
    Output:
        DataFrame: hedging set information after some important attributes calculation
    
    """
    

    # Foreign Exchange Rate    
    RATE = pd.DataFrame({'HEDGING_SET': ['USD','CNY','EUR','CAD','GBP'],'RATE': [1.32,0.2,1.56,1,1.73]})
    IR = pd.merge(IR, RATE, on = 'HEDGING_SET', how = 'inner')

    # Use adjusted_notional function to compute Adjusted Notional and Supervisory Duration
    IR_Notional = adjusted_notional(IR)
    
    # Determine Buy and Sell Positions by property of 
    IR_Position = IR_Notional.apply(lambda x: Position(x), axis=1)
    
    # Calculate Supervisory Delta and Maturity Factor
    
    IR_ALL = IR_Position.apply(lambda x: sup_delta(x), axis=1)
    
    IR_ALL['MATURITY_FACTOR'] = np.sqrt(np.minimum(1,IR_ALL['END_DATE'])/1) 
    
    # Calculate Effective Notional 
    IR_ALL['EFFECTIVE_NOTIONAL'] = IR_ALL['ADJUSTED_NOTIONAL'] * \
                                    IR_ALL['MATURITY_FACTOR'] * IR_ALL['SUPERVISORY_DELTA']
    
    # Classify Time Bucket
    IR_ALL['TIME_BUCKET'] = np.where(IR_ALL['END_DATE']<=1, 1, 
                                      np.where((IR_ALL['END_DATE']>1) & (IR_ALL['END_DATE']<=5), 2, 3))
    
    
    return IR_ALL

# In[Aggregation]: Aggregation Calculator
def Aggregation(Inputs):
    
    """
    This function is to aggregate different hedging set.
    
    Inputs:
        IR DataFrame: output from Calculation function.
    Output:
        Hedging Set Results: output of effective notional, addon for different hedging set.
        Netting Set Results (Final): Output of RC and PFE
    
    """
    
    Inputs = Inputs[['HEDGING_SET','TIME_BUCKET','EFFECTIVE_NOTIONAL','MTM','COLLATERAL']]
    
    Outputs = Inputs.groupby(['HEDGING_SET']).apply(effective)
    HEDGE_SET = Outputs[['HEDGING_SET','EFF_NOTIONAL_HEGDE',\
                           'MTM_HEDGE','COLLATERAL_HEDGE']].drop_duplicates(keep='first')
    HEDGE_SET['NETTING_SET'] = 'ABC'
    
    NETG_SET = HEDGE_SET.groupby(['NETTING_SET']).sum().reset_index(drop = False)
    NETG_SET['ADDON'] = NETG_SET['EFF_NOTIONAL_HEGDE'] * 0.005
    NETG_SET['PFE_MULTIPLIER'] = np.minimum(1, 0.05+(1-0.05)*\
                                    np.exp((NETG_SET['MTM_HEDGE']-NETG_SET['COLLATERAL_HEDGE'])\
                                           /(2*(1-0.05)*NETG_SET['ADDON'])))
    
	# Final Exposure  
    NETG_SET['SACCR_RC'] = np.maximum(0,NETG_SET['MTM_HEDGE']-NETG_SET['COLLATERAL_HEDGE'])
    NETG_SET['SACCR_PFE'] = NETG_SET['ADDON'] * NETG_SET['PFE_MULTIPLIER']
    NETG_SET['SACCR_EAD'] = 1.4*(NETG_SET['SACCR_RC']+NETG_SET['SACCR_PFE'])
    
    return HEDGE_SET, NETG_SET



# In[Final]
if __name__ == '__main__':
    
    
    IR = pd.read_excel('Interest Rate.xlsx')
    
    Trade_Detail = Calculation(IR)
    
    HEDGE_SET, NETG_SET = Aggregation(Trade_Detail)
    
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter('Output.xlsx', engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    Trade_Detail.to_excel(writer, sheet_name='TRADE_LEVEL_DETAIL', index = False)
    HEDGE_SET.to_excel(writer, sheet_name='HEDGING_SET', index = False)
    NETG_SET.to_excel(writer, sheet_name='FINAL_RESULT', index = False)
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()