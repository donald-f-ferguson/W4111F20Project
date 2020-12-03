import pymysql
import copy
from graphs.got.got_graph import GotGraph
import resources.rdbresource as rdb

gotg = GotGraph(auth=('neo4j', 'dbuserdbuser'),
              host="localhost",
              port=7687,
              secure=False)


def get_characters_by_query(args):

    res = rdb.get_by_by_query("W4111GoTHWClean", "characters_all", args)
    return res


def get_character_by_id(ch_id):

    common_list = [
        "character_id",
        "characterName",
        "characterIMDBID",
        "royal",
        "characterImageThumb",
        "characterImageFull",
        "nickname",
        "kingsguard"]

    shared_list = [
        "imdb_id",
        "season_info"
    ]
    q = {"character_id": ch_id}
    res = rdb.get_by_by_query("W4111GoTHWClean", "characters_all", q)

    if len(res) > 1:
        final_res = {k:res[0][k] for k in common_list}

        actors = []
        for r in res:
            tmp = {k:r[k] for k in shared_list}
            tmp["link"] = "/actors/" + r["imdb_id"]
            actors.append(tmp)
        final_res["actors"] = actors
    else:
        final_res=res

    return final_res


def get_related_characters(ch_id, r_kind):

    res = gotg.get_related_characters(ch_id, r_kind)
    retVal = []
    for r in res:
        retVal.append(dict(r.end_node))
    return retVal