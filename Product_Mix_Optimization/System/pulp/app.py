import pandas as pd
from Package import chan_method
from pulp import *
from datetime import datetime
import timeit
import warnings
warnings.filterwarnings("ignore")

choice = ''
while choice != 'q':
    chan_method.clear()
    print("\n------ Please contact huan-yang.chan@student.usm.my if any queries ------")
    print("\nWhat would you like to do?")
    print("1 - Solve model using monthly forecast")
    print("q - Quit")

    choice = input("\nPlease enter your choice: ")

    if choice == '1':
        chan_method.clear()
        choice1 = ''
        while choice1 != 'b':
            print("\n------ Solve model using monthly forecast ------")
            print("1 - Run")
            print("b - Back")
            choice1 = input("\nPlease enter your choice: ")
            if choice1 == '1':
                start = timeit.default_timer()
                chan_method.clear()
                # model start ######################################

                # model start date and time
                sdate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Import raw data
                df1 = pd.read_csv("RawMonth.csv", usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]).dropna(subset=['product', 'cpn'])
                df2 = (pd.read_csv("Calendar.csv", usecols=[0, 1, 2, 3, 4])).drop_duplicates(subset=['month'],keep='last').dropna(how='any')
                df3 = (pd.read_csv("EQ.csv", usecols=[0, 1, 2, 3, 4, 5, 6])).drop_duplicates(subset=['product', 'process', 'eqp'], keep='last').dropna(how='any')
                df4 = (pd.read_csv("AvailEQ.csv", usecols=[0, 1])).drop_duplicates(subset=['eqp'], keep='last').dropna(how='any')
                df5 = (pd.read_csv("Update.csv", usecols=[0, 1, 2, 3, 4, 5, 6])).drop_duplicates(subset=['item', 'product', 'process', 'eqp', 'startMonth'], keep='last').dropna(how='any')

                # Process raw data
                t1 = df1.melt(['product', 'cpn'], var_name='month', value_name='inQty')
                t1 = t1.dropna(how='any')
                t1 = t1.groupby(['product', 'month'], as_index=False)['inQty'].sum()
                EQ0 = pd.merge(t1, df2, on=['month'], how='left')
                EQ0 = pd.merge(EQ0, df3, on=['product'], how='left')
                EQ0 = pd.merge(EQ0, df4, on=['eqp'], how='left')
                EQ0['eqpTimeAvailable'] = EQ0['timeAvailable'] * EQ0['eqpQty']
                EQ0["inQty"] = EQ0["inQty"].astype(int)

                # CHECK NA
                na = EQ0[EQ0.isna().any(axis=1)].reset_index(drop=True)
                countna = EQ0.isnull().sum(axis=1)
                if max(countna) > 0:
                    print("!!! Operation aborted as there is NA item in dataset !!!")
                    print('...........................................................................')
                    print('Summary of Na')
                    print('...........................................................................')
                    print(na)
                # Run solver if there is no missing value
                else:
                    # # Create subcon info to prevent non-feasible solution
                    # df3a = df3.groupby(['product', 'process']).agg({'cost': "min"}).reset_index()
                    # df3a['cost'] = df3a['cost'] * 5
                    # df3a['ct'] = 0.0
                    # df3a['oee'] = 1.0
                    # df3a['pass'] = 1.0
                    # df3a['eqp'] = df3a['process'] + "_subcon"
                    #
                    # # Append subcon info to original table
                    # df3 = df3.append(df3a, ignore_index=True).drop_duplicates(subset=['product', 'process', 'eqp'],keep='last')
                    #
                    # # Create subcon info to prevent non-feasible solution
                    # df4a = df3a[['eqp']].drop_duplicates(keep='last')
                    # df4a['eqpQty'] = 1.0
                    #
                    # # Append subcon tool to original table
                    # df4 = df4.append(df4a, ignore_index=True).drop_duplicates(subset=['eqp'], keep='last')

                    # UPDATE EQ
                    for i in df5.index:

                        if df5.at[i, 'item'] == 'eqpQty' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['eqp'] == df5.at[i, 'eqp']) & (
                                        EQ0['month'] >= df5.at[i, 'startMonth']), 'eqpQty'] = \
                                df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'cost' and df5.at[i, 'eqp'] == 'All' and df5.at[
                            i, 'status'] == 'Plan':
                            EQ0.loc[
                                (EQ0['product'] == df5.at[i, 'product']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                        EQ0['month'] >= df5.at[i, 'startMonth']), 'cost'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'ct' and df5.at[i, 'eqp'] == 'All' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[
                                (EQ0['product'] == df5.at[i, 'product']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                        EQ0['month'] >= df5.at[i, 'startMonth']), 'ct'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'oee' and df5.at[i, 'eqp'] == 'All' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[
                                (EQ0['product'] == df5.at[i, 'product']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                        EQ0['month'] >= df5.at[i, 'startMonth']), 'oee'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'pass' and df5.at[i, 'eqp'] == 'All' and df5.at[
                            i, 'status'] == 'Plan':
                            EQ0.loc[
                                (EQ0['product'] == df5.at[i, 'product']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                        EQ0['month'] >= df5.at[i, 'startMonth']), 'pass'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'cost' and df5.at[i, 'product'] == 'All' and df5.at[
                            i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['eqp'] == df5.at[i, 'eqp']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                    EQ0['month'] >= df5.at[i, 'startMonth']), 'cost'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'ct' and df5.at[i, 'product'] == 'All' and df5.at[
                            i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['eqp'] == df5.at[i, 'eqp']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                    EQ0['month'] >= df5.at[i, 'startMonth']), 'ct'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'oee' and df5.at[i, 'product'] == 'All' and df5.at[
                            i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['eqp'] == df5.at[i, 'eqp']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                    EQ0['month'] >= df5.at[i, 'startMonth']), 'oee'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'pass' and df5.at[i, 'product'] == 'All' and df5.at[
                            i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['eqp'] == df5.at[i, 'eqp']) & (EQ0['process'] == df5.at[i, 'process']) & (
                                    EQ0['month'] >= df5.at[i, 'startMonth']), 'pass'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'cost' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['product'] == df5.at[i, 'product']) & (EQ0['eqp'] == df5.at[i, 'eqp']) & (
                                    EQ0['process'] == df5.at[i, 'process']) & (
                                            EQ0['month'] >= df5.at[i, 'startMonth']), 'cost'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'ct' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['product'] == df5.at[i, 'product']) & (EQ0['eqp'] == df5.at[i, 'eqp']) & (
                                    EQ0['process'] == df5.at[i, 'process']) & (
                                            EQ0['month'] >= df5.at[i, 'startMonth']), 'ct'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'oee' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['product'] == df5.at[i, 'product']) & (EQ0['eqp'] == df5.at[i, 'eqp']) & (
                                    EQ0['process'] == df5.at[i, 'process']) & (
                                            EQ0['month'] >= df5.at[i, 'startMonth']), 'oee'] = df5.at[i, 'newValue']

                        elif df5.at[i, 'item'] == 'pass' and df5.at[i, 'status'] == 'Plan':
                            EQ0.loc[(EQ0['product'] == df5.at[i, 'product']) & (EQ0['eqp'] == df5.at[i, 'eqp']) & (
                                    EQ0['process'] == df5.at[i, 'process']) & (
                                            EQ0['month'] >= df5.at[i, 'startMonth']), 'pass'] = df5.at[i, 'newValue']

                    EQ0['eqpTimeAvailable'] = EQ0['timeAvailable'] * EQ0['eqpQty']

                    # Prepare to loop through month
                    cm = t1['month'].unique()
                    feasible_list =[]
                    final_df = pd.DataFrame()
                    constraint_definition = pd.DataFrame()
                    sensitivity_constraint = pd.DataFrame()
                    sensitivity_variable = pd.DataFrame()

                    for m in cm:
                        # Populate Variable and Contraint Dictionary
                        EQ = EQ0[(EQ0.month == m)].reset_index(drop=True)
                        EQ['prodProcess'] = EQ[['month', 'product', 'process']].apply(lambda x: ''.join(x), axis=1)
                        EQ['variable'] = EQ[['month', 'product', 'process', 'eqp']].apply(lambda x: ''.join(x), axis=1)
                        EQ = EQ.drop_duplicates(subset=['variable'], keep='last')
                        variables = EQ['variable']
                        inQtys = EQ['inQty']
                        costs = dict(zip(EQ.variable, EQ.cost))

                        # SET THE VARIABLE
                        x = LpVariable.dicts('', variables, lowBound=0, cat='Continuous')

                        # INIT LP SOLVER
                        prob = pulp.LpProblem('Reduce Cost', LpMinimize)

                        # SET THE OBJECTIVE FUNCTION
                        prob += sum([x[v] * costs[v] for v in variables]), 'Sum_of_cost'

                        # CONSTRAINT 1 - IN QTY SAME WITH SOLVER QTY
                        products = EQ['prodProcess'].unique()
                        for i in products:
                            prob += lpSum(x[p] for p in EQ.loc[(EQ['prodProcess'] == i), 'variable']) == \
                                    EQ.loc[(EQ['prodProcess'] == i), 'inQty'].unique()[0]

                        # CONSTRAINT 2 - EQP HOUR WITHIN LIMIT
                        eqps = EQ['eqp'].unique()
                        for i in eqps:
                            prob += lpSum(x[e] * EQ.loc[(EQ['variable'] == e), 'ct'].unique()[0] *
                                          EQ.loc[(EQ['variable'] == e), 'pass'].unique()[0] /
                                          EQ.loc[(EQ['variable'] == e), 'oee'].unique()[0] for e in
                                          EQ.loc[(EQ['eqp'] == i), 'variable']) <= \
                                    EQ.loc[(EQ['eqp'] == i), 'eqpTimeAvailable'].unique()[0]

                        # Solve the optimization problem using the specified Solver
                        arg1 = '--ranges sensit_{}.sen'.format(m)
                        arg2 = 'sensit_{}.lp'.format(m)
                        prob.writeLP(arg2)
                        prob.solve(GLPK(options=[arg1]))

                        # Save solver result
                        if pulp.LpStatus[prob.status] == 'Optimal':
                            var_list = []
                            qty_list = []

                            for variable in prob.variables():
                                # print ("{} = {}".format(variable.name, variable.varValue))
                                var_list.append(variable.name[1:])
                                qty_list.append(variable.varValue)

                            solver_df = {'variable': var_list, 'solver_qty': qty_list}
                            df = pd.DataFrame(solver_df)
                            df1 = pd.merge(EQ, df, on=['variable'], how='left')
                            df1['Remark'] = 'First Optimal'
                            final_df = final_df.append(df1, ignore_index=True)
                            # Compile constraint definition
                            constraint_df = pd.DataFrame(list(prob.constraints.items()), columns=['Constraint Name', 'Description'])
                            constraint_df['month'] = m
                            constraint_definition = constraint_definition.append(constraint_df, ignore_index=True)
                            # Compile sensitivity_constraint
                            sensitivity_constraint = sensitivity_constraint.append(
                                chan_method.convertsensitivityreport('sensit_{}.sen'.format(m),m)['sensitivity_constraint'],
                                ignore_index=True)
                            sensitivity_variable = sensitivity_variable.append(
                                chan_method.convertsensitivityreport('sensit_{}.sen'.format(m),m)['sensitivity_variable'],
                                ignore_index=True)
                            feasible_list.append(m)

                    # COMPILE FINAL TABLE
                    final_df['eqpTimeAvailable'] = final_df['timeAvailable'] * final_df['eqpQty']
                    final_df['hourRequired'] = (final_df['solver_qty'] * final_df['ct'] * final_df['pass']) / (
                            final_df['oee'] * 3600)
                    final_df['hourAvailable'] = final_df['eqpTimeAvailable'] / 3600
                    final_df['eqpUtilisation'] = final_df['hourRequired'] / final_df['hourAvailable']
                    final_df = final_df[(final_df.eqp != 'NoCapacityAvailable')].reset_index(drop=True)
                    final_df['eqpRequired'] = final_df['eqpUtilisation'] * final_df['eqpQty']
                    eqp_df = final_df.groupby(['month', 'eqp'], as_index=False)[
                        'solver_qty', 'eqpUtilisation'].sum()
                    eqp_df['eqpCapacity'] = eqp_df['solver_qty'] / eqp_df['eqpUtilisation']
                    eqp_df = eqp_df[['month', 'eqp', 'eqpCapacity']]
                    final_df = pd.merge(final_df, eqp_df, on=['month', 'eqp'], how='left')
                    final_df['TCost'] = final_df['cost']*final_df['solver_qty']
                    final_df['reportDate'] = sdate
                    final_df.to_csv("PULP_month.csv", index=False)
                    sensitivity_variable.to_csv("sensitivity_variable.csv", index=False)
                    sensitivity_constraint = pd.merge(sensitivity_constraint, constraint_definition,
                                                      on=['month', 'Constraint Name'], how='left')
                    sensitivity_constraint.to_csv("sensitivity_constraint.csv", index=False)

                    # Print feasible list
                    print('-------------------------------------------------------------------------------------------')
                    print('Company XYZ   -    Department of Industrial Engineering')
                    print('-------------------------------------------------------------------------------------------')
                    for i in feasible_list:
                        print("{}-feasible".format(i))

                # model end

                stop = timeit.default_timer()
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print("Solve model using monthly forecast successfully in {}s at {}".format(str(stop-start)[:4],dt_string))

            else:
                chan_method.clear()
                print("\nI don't understand that choice, please try again.\n")
        chan_method.clear()

    elif choice == 'q':
        print("\nThanks for using. See you later.\n")
    else:
        chan_method.clear()
        print("\nI don't understand that choice, please try again.\n")
