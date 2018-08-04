import numpy as np
import pandas as pd

loan_path = "loan.csv"

loan = pd.read_csv(loan_path, low_memory = False)

# Filter df to 36 month loans. n.b. leading space.
loan_36 = loan[loan.term == " 36 months"]

# issue_d is a date string like Mar-2012. Parse as pandas DateTime
loan_36['issue_dt'] = pd.to_datetime(loan_36['issue_d'], format='%b-%Y')

# filter to loans with complete history.
# note that Charged Off or Prepayed loans may have less that 36 months of history.
loan_36_ret = loan_36[loan_36['issue_dt'] <= '2014-01-01']

# # calculate total cash returned to investor on loan
# loan_36_ret['cash_in'] = loan_36_ret[loan_36_ret['total_rec_prncp'] + loan_36_ret['total_rec_int'] + loan_36_ret['total_rec_late_fee']]

# total return is defined as (cash in - cash invested) / (cash invested)
loan_36_ret['total_return'] = loan_36_ret[(loan_36_ret['total_pymnt_inv'] - loan_36_ret['funded_amnt_inv']) / loan_36_ret['funded_amnt_inv']]

# annualized return assumes holding period of 3 years (even if loan prepays or charged off)
# this underestimates returns, as prepayed principal could be re-invested
loan_36_ret['annualized_return'] = loan_36_ret[(loan_36_ret['total_return'] + 1) ^ (1.0/3)]

loan_36.groupby('grade').agg({
		'funded_amnt_inv': ['min', 'mean', 'max', 'sum'],
		'int_rate': 'mean',
		'cash_in' : 'sum',
		'total_rec_prncp': 'sum',
		'total_rec_int': 'sum',
		'total_rec_late_fee': 'sum',
		'annualized_return' : 'mean'
	})




num_loans = len(loan_36)
loan_36['sample'] = p.Series(np.random.randn(sLength), index=df1.index)