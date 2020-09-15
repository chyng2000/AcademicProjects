from os import system, name
import pandas as pd

def isfloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def isstartwith_(s):
    if s[:2] == "_C":
        return 'constraint'
    elif s[:1] == "_":
        return 'variable'
    else:
        return 'unknown'

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def convertsensitivityreport(source, month):
    master_list = []
    constraint_list = []
    variable_list = []
    output_dict = {}

    # Using readlines()
    file1 = open(source, 'r')
    Lines = file1.readlines()

    for line in Lines:
        words = line.strip().split()
        if len(words) > 0:
            master_list.append(words)

    for i in range(len(master_list)):
        temp_list = []
        if (isfloat(master_list[i][0]) and isstartwith_(master_list[i][1]) == 'constraint'):
            # append constraint number
            temp_list.append(master_list[i][0])
            # append constraint name
            temp_list.append(master_list[i][1])
            # append final value
            temp_list.append(master_list[i][3])
            # append shadow price
            temp_list.append(master_list[i + 1][0])
            # append constraint RHS1
            temp_list.append(master_list[i][5])
            # append constraint RHS2
            temp_list.append(master_list[i + 1][1])
            # append activity range
            temp_list.append(master_list[i][6])
            temp_list.append(master_list[i + 1][2])

            constraint_list.append(temp_list)

        elif (isfloat(master_list[i][0]) and isstartwith_(master_list[i][1]) == 'variable' and len(
                master_list[i]) == 2.0):
            # append variable number
            temp_list.append(master_list[i][0])
            # append variable name
            temp_list.append(master_list[i][1])
            # append final value
            temp_list.append(master_list[i + 1][1])
            # append reduced cost
            temp_list.append(master_list[i + 2][0])
            # append objective coefficient
            temp_list.append(master_list[i + 1][2])
            # append objective coefficient range
            temp_list.append(master_list[i + 1][5])
            temp_list.append(master_list[i + 2][3])

            variable_list.append(temp_list)

        elif (isfloat(master_list[i][0]) and isstartwith_(master_list[i][1]) == 'variable'):
            # append variable number
            temp_list.append(master_list[i][0])
            # append variable name
            temp_list.append(master_list[i][1])
            # append final value
            temp_list.append(master_list[i][3])
            # append reduced cost
            temp_list.append(master_list[i + 1][0])
            # append objective coefficient
            temp_list.append(master_list[i][4])
            # append objective coefficient range
            temp_list.append(master_list[i][7])
            temp_list.append(master_list[i + 1][3])

            variable_list.append(temp_list)

    df_constraint = pd.DataFrame(constraint_list, columns=['No', 'Constraint Name', 'Final Value', 'Shadow Price',
                                                           'RHS 1', 'RHS 2', 'Range 1', 'Range 2']).replace('.', 0.0)
    df_constraint['month'] = month

    df_variable = pd.DataFrame(variable_list, columns=['No', 'Variable Name', 'Final Value', 'Reduced Cost',
                                                       'Objective Coeficient', 'Lower Range', 'Upper Range']).replace(
        '.', 0.0)
    df_variable['month'] = month

    output_dict['sensitivity_constraint'] = df_constraint
    output_dict['sensitivity_variable'] = df_variable

    return output_dict