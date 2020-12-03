import resources.Characters as C
import resources.Actors as A
import process_got_json

def t0():

    res = C.get_character_by_id("CH_283")
    print("Res = ", process_got_json.dumps(res, indent=3))

def t1():
    q1 = {"characterName": "Rickard Karstark"}
    res = C.get_characters_by_query(q1)
    print("Res = ", process_got_json.dumps(res, indent=3))


def t2():
    ch_id = 'CH_15'
    r_type = "KILLED"
    res = C.get_related_characters(ch_id,r_type)
    print("Res = ", res)


def t3():
    id = 'nm0000980'
    res = A.get_actor_by_query({"nconst": id})
    print("Res = ", res)

t0()
#t1()
#t2()
#t3()

