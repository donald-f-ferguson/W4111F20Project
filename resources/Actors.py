import pymysql
import copy
import resources.rdbresource as rdb

conn = pymysql.connect(
    user="dbuser",
    password="dbuserdbuser",
    host="localhost",
    cursorclass=pymysql.cursors.DictCursor,
    db="W4111GoTHWClean"
)

def get_actor_by_query(args):

    q_string = dict(copy.copy(args))
    terms = []
    vals = []

    for k,v in q_string.items():
        terms.append(str(k) + "=%s")
        vals.append(v)

    wc = " WHERE " + " AND ".join(terms)

    q = "SELECT * FROM imdbnew.name_basics " + wc;
    cur = conn.cursor()
    res = cur.execute(q, args=vals)
    res = cur.fetchall()
    return res


def get_actor_by_id(id):
    props = ['nconst', 'primary_name', 'birth_year', 'death_year']

    q = {"nconst": id}
    res = rdb.get_by_by_query("imdbnew", "name_basics", q)

    if len(res) == 1:
        r = res[0]
        final_res = {k:r[k] for k in props}
        profs = set(r["primary_profession"].split(","))
        final_res["primary_professions"] = list(profs)

    else:
        final_res = None

    return final_res