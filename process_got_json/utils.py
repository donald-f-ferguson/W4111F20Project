
raise NotImplementedError("This module is not implemented.")

import json
import pymysql
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:dbuserdbuser@localhost/W4111GoTTest')

data_dir = "/Users/donaldferguson/ansys_one_drive/Columbia/IntroToDBHWs/GoT/game-of-thrones/data"

local_cnx = pymysql.connect(
    host="localhost",
    user="root",
    password="dbuserdbuser",
    db="W4111GoTTest",
    cursorclass=pymysql.cursors.DictCursor)


def get_top_level_elements(j_data_list):

    basic = {}
    compound = {}

    for j in j_data_list:
        for k,v in j.items():

            if type(v) == list or type(v) == dict:
                compound[k] = type(v)
                if basic.get(k, None) is not None:
                    del basic[k]
            else:
                if compound.get(k, None) is None:
                    basic[k] = type(v)

    result = {
        "atomic": basic,
        "compound": compound
    }
    return result


def get_file_as_json(fn, top_level_element):

    j_data = None

    with open(data_dir + "/" + fn, "r") as j_file:
        j_data = json.load(j_file)
        if top_level_element is not None:
            j_data = j_data[top_level_element]

    return j_data


def correct_top_elements(j_data, corrections):

    for r in j_data:
        for k in r.keys():
            for c in corrections.keys():
                map_it = r.get(c, None)
                if map_it is not None:
                    r[corrections[c]] = r[c]
                    del r[c]

    return j_data


def save_json_array(t_name, elements, field_list):
    df = pd.DataFrame(elements)

    if field_list is not None:
        df_f = pd.DataFrame(df, columns=field_list)
    else:
        df_f = df

    df_f.fillna(value=pd.np.nan, inplace=True)
    df_f.to_sql(name=t_name, con=engine, if_exists='replace', index_label="id")


def flatten_lists(element):

    result = []
    for k,v in element.items():
        if type(v) == list:
            for le in v:
                result.append({"label": k, "value": str(le)})

    return result


def create_table_from_cols(t_name, cols, drop_it=False):

    cur = local_cnx.cursor()

    try:
        if drop_it:
            res = cur.execute("drop table if exists " + t_name)

        sql = "create table " + t_name + "("

        col_terms = []
        for c in cols:
            c_name = c[0]
            if c[1] == str:
                c_clause = c_name + " TEXT"
            elif c[1] == bool:
                c_clause = c_name + " BOOLEAN"
            elif c[1] == int:
                c_clause = c_name + " INT"
            elif c[1] == float:
                c_clause = c_name + " DOUBLE"
            else:
                c_clause = c_name + " TEXT"

            col_terms.append(c_clause)

        c_clause = ",".join(col_terms)

        sql += c_clause + ");"

        res = cur.execute(sql)
        local_cnx.commit()
        print("Created table.")
    except Exception as e:
        print("Exception e =", e)
        local_cnx.rollback()





