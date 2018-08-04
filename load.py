import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load():
	loan_path = "loan.csv"

	loan = pd.read_csv(loan_path, low_memory = False)

	# issue_d column is a string, i.e. Apr-2012. format as datetime:
	loan['vintage_month'] = pd.to_datetime(loan['issue_d'], format='%b-%Y')
	loan['vintage_year'] = loan['vintage_month'].map(lambda x: x.year)

def summarize():
	loans_by_grade = loan.groupby(['term', 'grade']).agg({
			'funded_amnt_inv': ['min', 'mean', 'max', 'sum'],
			'int_rate': 'mean',
			'annual_inc': 'mean',
			'dti': 'mean'
		})
	loans_by_grade.columns = ['Funded_amnt', 'avg_int_rate', 'avg_annual_income', 'avg_dti']

	# show some summary borrower statistics by grade and term
	loans_by_grade_term

	## chart avg interest rate by vintage_month, grade
	fig, ax = plt.subplots(figsize = (16, 8))
	loan.groupby(['vintage_month','grade']).mean()['int_rate'].unstack().plot(ax = ax)
	ax.set_xlabel('Vintage Month')
	ax.set_ylabel('Avg. Interest Rate')
	# plt.show()

	## origination volume by month by grade
	fig, ax = plt.subplots(figsize = (16, 8))
	loan.groupby(['vintage_month','grade']).sum()['funded_amnt'].unstack().plot(ax = ax)
	ax.set_xlabel('Vintage Month')
	ax.set_ylabel('Total Funded Amount')
	# plt.show()

def calculate_returns_36():
	# Filter df to 36 month loans. n.b. leading space.
	loan_36 = loan[loan.term == " 36 months"]

	# group by loan status to find the latest vintage_month for which loans have all either paid off or charged off
	loan_36.groupby('loan_status').agg({'vintage_month': ['min', 'max']})

	# filter to loans with 36 months of history. Note: some loans are still outstanding (i.e. Late or Defaulted)
	# at 36 months maturity, so returns may be underestimated
	loan_36_ret = loan_36[(loan_36['vintage_month'] < '2012-12-01') & (loan_36['funded_amnt_inv'] > 0)]

	# total cash returned to investor on loan is the payments rec'd plus the recoveries minus recovery fees
	loan_36_ret['total_cash_in'] = loan_36_ret['total_pymnt_inv'] + loan_36_ret['recoveries'] - loan_36_ret['collection_recovery_fee']

	loans_by_grade = loan_36_ret.groupby('grade').agg({
			'funded_amnt_inv': ['min', 'mean', 'max', 'sum'],
			'int_rate': 'mean',
			'funded_amnt_inv' : 'sum',
			'total_cash_in': 'sum'
		})

	# total return is defined as (cash in - cash invested) / (cash invested)
	loans_by_grade['total_return_wt'] = (loans_by_grade['total_cash_in'] - loans_by_grade['funded_amnt_inv']) / loans_by_grade['funded_amnt_inv']

	# annualized return assumes holding period of 3 years (even if loan prepays or charged off)
	# this underestimates returns, as prepayed principal could be re-invested
	loans_by_grade['annualized_return_wt'] = ((loans_by_grade['total_return_wt'] + 1) ** (1.0/3)) - 1


load()
summarize()
# calculate_returns_36()

# num_loans = len(loan_36)
# loan_36['sample'] = p.Series(np.random.randn(sLength), index=df1.index)