
"""

NOTE: I have not run this code for a while. It is for example purposes only and does not work.

"""

raise NotImplementedError("This module is not implemented.")


import pandas as pd
import process_got_json
import pymysql
from sqlalchemy import create_engine


json_dir = '../../data/json'

conn = pymysql.connect(
    host='localhost',
    user='dbuser',
    password='dbuserdbuser',
    db='W4111GoT',
    cursorclass=pymysql.cursors.DictCursor)

def get_json_entity(fn, top_element=None):

    full_fn = json_dir + "/" + fn
    f = open(full_fn, "r")
    j_data = process_got_json.load(f)
    if top_element is not None:
        j_data = j_data[top_element]
    return j_data


def get_columns_from_json_entities(entities):

    columns = []

    for e in entities:
        cols = e.keys()
        columns.extend(cols)

    cols = set(columns)
    return cols


def json_entities_to_df(entities):

    df = pd.DataFrame(entities)
    return df


def df_to_table(table_name, df, index_name):
    engine = create_engine('mysql+pymysql://dbuser:dbuserdbuser@localhost/W4111GoT')
    df2 = df.astype(str)
    #data.to_sql(name='sample_table2', con=cnx, if_exists='append', index=False)
    res = df2.to_sql(con=engine, name=table_name, if_exists='replace', index_label="id")


def get_character_relationships(c_json, rel_names):

    result = []

    for c in c_json:
        for rel_name in rel_names:
            r_data = c.get(rel_name, None)
            if r_data is not None and len(r_data) > 0:
                for e in r_data:
                    new_r = {"label": rel_name, "source_name": c['characterName'], "target_name": e}
                    result.append(new_r)

    return result


def process_locations(locations_info):

    locations_json = []
    for l in locations_info:
        new_l = {"location": l["location"]}
        locations_json.append(new_l)
        sub_ls = l.get("subLocation")
        if sub_ls is not None:
            for sl in sub_ls:
                new_sl = {"location": l["location"], "subLocation": sl}
                locations_json.append(new_sl)

    locations_df = json_entities_to_df(locations_json)
    res = df_to_table('locations', locations_df, 'id')



def process_scenes(episodes_info):

    scenes_json = []
    scene_characters_json = []

    for e in episodes_info:

        seasonNumber = e["seasonNum"]
        episodeNumber = e["episodeNum"]

        scenes = e.get('scenes', None)
        if scenes is not None:
            for s in scenes:
                new_s = s
                new_s["seaonNumber"] = seasonNumber
                new_s['episodeNumber'] = episodeNumber

                characters = s.get('characters', None)
                if characters is not None:
                    for c in characters:
                        new_c = c
                        new_c["seaonNumber"] = seasonNumber
                        new_c['episodeNumber'] = episodeNumber
                        scene_characters_json.append(new_c)
                scenes_json.append(new_s)


    scenes_df = json_entities_to_df(scenes_json)
    scene_characters_df = json_entities_to_df(scene_characters_json)
    res = df_to_table('scenes', scenes_df, 'id')
    res = df_to_table('scenes_characters', scene_characters_df, 'id')


def tt():

    locations_json = get_json_entity('locations.json', 'regions')
    res = process_locations(locations_json)

    characters_json = get_json_entity('characters.json', 'characters')
    characters_df = json_entities_to_df(characters_json)
    #character_cols = get_columns_from_json_entities(characters_json)
    #for c in character_cols:
    #    print("'"+c+"',")

    character_col_names = [
        'nickname',
        'characterName',
        'royal',
        'characterImageFull',
        'kingsguard',
        'characterImageThumb',
        'houseName',
        'actorLink',
        'characterLink',
        'actorName'
    ]
    character_rel_names = [
        'abductedBy',
        'marriedEngaged',
        #'actors'
        'killed',
        'abducted',
        'guardedBy',
        'killedBy',
        'siblings',
        'parentOf',
        'allies',
        'servedBy',
        'serves',
        'sibling'
        'guardianOf'
        'parents'
    ]

    characters_json = get_json_entity('characters.json', 'characters')
    characters_df = json_entities_to_df(characters_json)
    characters_cols_df = pd.DataFrame(characters_df, columns=character_col_names)
    characters_cols_df = characters_cols_df.replace({pd.np.nan: None})
    res = df_to_table('characters', characters_cols_df, 'id')

    episodes_json = get_json_entity('episodes.json', 'episodes')
    episodes_df = json_entities_to_df(episodes_json)
    episodes_cols = ['seasonNum','episodeNum','episodeLink','episodeAirDate','episodeDescription']
    episodes_cols_df = pd.DataFrame(episodes_df, columns=episodes_cols)
    episodes_cols_df = episodes_cols_df.replace({pd.np.nan: None})
    res = df_to_table('episodes', episodes_cols_df, 'id')

    res = process_scenes(episodes_json)

    """
    locations_json = get_json_entity('locations.json', 'regions')
    locations_df = json_entities_to_df(locations_json)
    """

    characters_rel_json = get_character_relationships(characters_json,
            [
                'killed', 'killedBy',
                'serves', 'servedBy',
                'parentOf', 'parents',
                'guardedBy','guardianOf',
                'marriedEngaged'
                'allies',
                'abducted', 'abductedBy',
                'siblings'])


    #res = df_to_table('locations', locations_df, 'id')
    rels_df = json_entities_to_df(characters_rel_json)
    res = df_to_table('character_relationships', rels_df, 'id')




tt()


