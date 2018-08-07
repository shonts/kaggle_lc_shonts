import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf

def load():
	loan_path = "loan.csv"

	print("Loading csv . . .")
	loan_df = pd.read_csv(loan_path, low_memory = False)
	print("Done loading csv. Adding return columns")

	# issue_d column is a string, i.e. Apr-2012. format as datetime:
	loan_df['vintage_month'] = pd.to_datetime(loan_df['issue_d'], format='%b-%Y')
	loan_df['vintage_year'] = loan_df['vintage_month'].map(lambda x: x.year)

	# total cash returned to investor on loan is the payments rec'd plus the recoveries minus recovery fees
	loan_df['total_cash_in'] = loan_df['total_pymnt_inv'] + loan_df['recoveries'] - loan_df['collection_recovery_fee']

	# total return is defined as (cash in - cash invested) / (cash invested)
	loan_df['total_return'] = (loan_df['total_cash_in'] - loan_df['funded_amnt_inv']) / loan_df['funded_amnt_inv']

	# annualized return assumes holding period of full 36 months (even if loan prepays or charges off)
	# this underestimates returns, as prepayed principal could be re-invested
	loan_df['annualized_return'] = ((loan_df['total_return'] + 1) ** (1.0/3)) - 1

	print("Done adding return columns")
	return loan_df

def summarize(loan_df):
	loans_by_grade = loan_df.groupby(['term', 'grade']).agg({
			'funded_amnt': ['min', 'mean', 'max', 'sum'],
			'int_rate': 'mean',
			'annual_inc': 'mean',
			'dti': 'mean'
		})

	# write out some summary borrower statistics by grade and term
	loans_by_grade.to_csv("loans_by_grade.csv")

	## chart avg interest rate by vintage_month, grade
	fig, ax = plt.subplots(figsize = (16, 8))
	loan_df.groupby(['vintage_month','grade']).mean()['int_rate'].unstack().plot(ax = ax)
	ax.set_xlabel('Vintage Month')
	ax.set_ylabel('Avg. Interest Rate')
	ax.set_title('Average Interest Rate by Vintage Month, Grade')
	plt.show()

	## origination volume by month by grade
	fig, ax = plt.subplots(figsize = (16, 8))
	loan_df.groupby(['vintage_month','grade']).sum()['funded_amnt'].unstack().plot(ax = ax)
	ax.set_yscale('log')
	ax.set_xlabel('Vintage Month')
	ax.set_ylabel('Total Funded Amount (log scale, hundred million USD)')
	ax.set_title('Funded Amount by Vintage Month, Grade')
	plt.show()

def calculate_returns_36(loan_df):
	# Filter df to 36 month loans. NOTE there's a leading space in the string " 36 months"
	loan_36 = loan_df[loan_df.term == " 36 months"]

	# Filter to loans with 36 months of history. Note: some loans are still outstanding (i.e. Late or Defaulted)
	# at 36 months maturity, so returns are slightly underestimated
	loan_36_ret = loan_36[(loan_36['vintage_month'] < '2012-12-01') & (loan_36['funded_amnt_inv'] > 0)]

	loans_by_grade_year = loan_36_ret.groupby(['grade', 'vintage_year']).agg({
			'funded_amnt_inv': ['min', 'mean', 'max', 'sum'],
			'int_rate': 'mean',
			'funded_amnt_inv' : 'sum',
			'total_cash_in': 'sum'
		})

	# Calculate returns after aggregation because returns should be cash-weighted
	#    ($35k loan matters more than $1k loan)
	# Total return over period is defined as (cash in - cash invested) / (cash invested)
	loans_by_grade_year['total_return_wt'] = (loans_by_grade_year['total_cash_in'] - loans_by_grade_year['funded_amnt_inv']) / loans_by_grade_year['funded_amnt_inv']

	# annualized return assumes holding period of 3 years (even if loan prepays or charged off)
	# this underestimates returns, as principal payments could be re-invested continuously
	loans_by_grade_year['annualized_return_wt'] = ((loans_by_grade_year['total_return_wt'] + 1) ** (1.0/3)) - 1

	loans_by_grade_year.to_csv("loans_by_grade_year_returns.csv")

def model_calculation(loan_df):
	loan_df_cleaned = loan_df[(loan_df['annualized_return'] > -1) & (loan_df['annualized_return'] < 2)]
	result = smf.ols(formula="annualized_return ~ dti + annual_inc + funded_amnt", data = loan_df_cleaned).fit()
	print result.params
	print result.summary()

	loan_df_cleaned_pre_2010 = loan_df_cleaned[loan_df_cleaned['vintage_year'] <= 2010]
	result = smf.ols(formula="annualized_return ~ dti + annual_inc + funded_amnt", data = loan_df_cleaned_pre_2010).fit()
	print result.params
	print result.summary()

	loan_df_cleaned_post_2010 = loan_df_cleaned[loan_df_cleaned['vintage_year'] > 2010]
	result = smf.ols(formula="annualized_return ~ dti + annual_inc + funded_amnt", data = loan_df_cleaned_post_2010).fit()
	print result.params
	print result.summary()

loan_df = load()
summarize(loan_df)
calculate_returns_36(loan_df)
model_calculation(loan_df)
