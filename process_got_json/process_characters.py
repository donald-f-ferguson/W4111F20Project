raise NotImplementedError("This module is not implemented.")


import os
import pandas as pd
pd.set_option('display.width', 132)
pd.set_option('display.max_columns', 15)
import json
import pymysql
import pandas

from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:dbuserdbuser@localhost/W4111GoTTest')

import src.processors.utils as utils

# There are a couple of errirs
_name_corrections = {
    "sibling": "siblings"
}

def do_it():

    characters = utils.get_file_as_json("characters.json", "characters")
    characters = utils.correct_top_elements(characters, _name_corrections)

    # Needed because names are not unique.
    character_prefix = "CH_"
    count = 0

    for c in characters:
        c["character_id"] = str(character_prefix) + str(count)
        count = count + 1


    character_cols = utils.get_top_level_elements(characters)

    print("COLS = \n", json.dumps(character_cols, indent=2, default=str))

    utils.save_json_array('characters', characters, character_cols['atomic'].keys())

    c_rels = []
    for c in characters:

        all_ls = utils.flatten_lists(c)
        if all_ls is not None:
            new_rel = {"character_id": c["character_id"], "characterName": c["characterName"]}
            for l in all_ls:
                tmp = {**new_rel, **l}
                c_rels.append(tmp)

    utils.save_json_array("character_relationships", c_rels, None)






do_it()