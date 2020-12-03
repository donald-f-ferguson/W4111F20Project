from py2neo import data, Graph, NodeMatcher, Node, Relationship, RelationshipMatcher
"""
See https://py2neo.org/v4/
"""

"""
NOTE:
    1. I did some basic testing, debugging, etc. but there may be errors.
    2. You can complain about the errors if you want but my response will be, "No Template for You!"
"""

import process_got_json
import uuid


class GotGraph(object):
    """
    This object provides a set of helper methods for creating and retrieving nodes and relationships from
    a Neo4j database holding information about players, teams, fans, comments and their relationships.
    """

    # Note:
    # I tend to avoid object mapping frameworks. Object mapping frameworks are fun in the beginning
    # but tend to be annoying after a while. So, I did not create types Player, Team, etc.
    #


    # Connects to the DB and sets a Graph instance variable.
    # Also creates a NodeMatcher and RelationshipMatcher, which are a py2neo framework classes.
    def __init__(self,  auth=('neo4j', 'dbuserdbuser'), host='localhost', port=7687, secure=False, ):
        self._graph = Graph(secure=secure,
                            bolt=True,
                            auth=auth,
                            host=host,
                            port=port)
        self._node_matcher = NodeMatcher(self._graph)
        self._relationship_matcher = RelationshipMatcher(self._graph)

    def run_q(self, qs, args):
        """

        :param qs: Query string that may have {} slots for parameters.
        :param args: Dictionary of parameters to insert into query string.
        :return:  Result of the query, which executes as a single, standalone transaction.
        """
        try:
            tx = self._graph.begin(autocommit=False)
            result = self._graph.run(qs, args)
            return result
        except Exception as e:
            print("Run exaception = ", e)

    def run_match(self, labels=None, properties=None):
        """
        Uses a NodeMatcher to find a node matching a "template."
        :param labels: A list of labels that the node must have.
        :param properties: A dictionary of {property_name: property_value} defining the template that the
            node must match.
        :return: An array of Node objects matching the pattern.
        """
        #ut.debug_message("Labels = ", labels)
        #ut.debug_message("Properties = ", json.dumps(properties))

        if labels is not None and properties is not None:
            result = self._node_matcher.match(labels, **properties)
        elif labels is not None and properties is None:
            result = self._node_matcher.match(labels)
        elif labels is None and properties is not None:
            result = self._node_matcher.match(**properties)
        else:
            raise ValueError("Invalid request. Labels and properties cannot both be None.")

        # Convert NodeMatch data into a simple list of Nodes.
        full_result = []
        for r in result:
            full_result.append(r)

        return full_result

    def find_nodes_by_template(self, tmp):
        """

        :param tmp: A template defining the label and properties for Nodes to return. An
         example is { "label": "Fan", "template" { "last_name": "Ferguson", "first_name": "Donald" }}
        :return: A list of Nodes matching the template.
        """
        labels = tmp.get('label', None)
        props = tmp.get("template", None)
        result = self.run_match(labels=labels, properties=props)
        return result

    def create_node(self, label, **kwargs):
        n = Node(label, **kwargs)
        tx = self._graph.begin(autocommit=True)
        tx.create(n)
        return n

    # Given a UNI, return the node for the Fan.
    def get_character(self, character_id):
        n = self.find_nodes_by_template({"label": "Character",
                "template": {"character_id": character_id}})
        if n is not None and len(n) > 0:
            # I should throw an exception here if there is more than 1.
            n = n[0]
        else:
            n = None

        return n

    def get_related_characters(self, ch_id, r_kind):

        t = self.get_character(ch_id.upper())
        nodes = set()
        nodes.add(t)
        n = self._relationship_matcher.match(nodes, r_type=r_kind.upper())
        return n

    def create_character_relationship(self, source_id, target_id, label):
        """
        Create a SUPPORTS relationship from a Fan to a Team.
        :param uni: The UNI for a fan.
        :param team_id: An ID for a team.
        :return: The created SUPPORTS relationship from the Fan to the Team
        """
        f = self.get_character(source_id)
        t = self.get_character(target_id)
        l = label.upper()
        r = Relationship(f, l, t)
        tx = self._graph.begin(autocommit=True)
        tx.create(r)
        return r

    def get_appearance(self, player_id, team_id, year_id):
        """
        Get the information about appearances for a player and team.
        :param player_id: player_id
        :param team_id: team_id
        :param year_id: The year for getting appearances.
        :return:
        """
        try:
            # Get the Nodes at the ends of the relationship representing appearances.
            p = self.get_player(player_id)
            t = self.get_team(team_id)

            # Run a match looking for relationships of a specific type linking the nodes.
            rm = self._graph.match(nodes=[p,t], r_type="APPEARED")
            result = []

            # If there is a list of relationships.
            if rm is not None:
                for r in rm:

                    # The type will be a class APPEARED() because of the OO mapping.
                    node_type = type(r).__name__
                    year = r['year']

                    # If the type and year are correct, add to result
                    if node_type == "APPEARED" and (year==year_id or year_id is None):
                        result.append(r)

                return result
            else:
                return None
        except Exception as e:
            print("get_appearance: Exception e = ", e)
            raise e


    # Create an APPEARED relationship from a player to a Team
    def create_appearance_all(self, player_id, team_id, year, games):
        """

        :param player_id: O
        :param team_id:
        :param year:
        :param games:
        :return:
        """
        try:
            tx = self._graph.begin(autocommit=False)
            q = "match (n:Player {player_id: '" + player_id + "'}), " + \
                "(t:Team {team_id: '" + team_id + "'}) " + \
                "create (n)-[r:APPEARED { games: " + str(games) + ", year : " + str(year) + \
                "}]->(t)"
            result = self._graph.run(q)
            tx.commit()
        except Exception as e:
            print("create_appearances: exception = ", e)

    # Create a FOLLOWS relationship from a Fan to another Fan.
    def create_follows(self, follower, followed):
        f = self.get_fan(follower)
        t = self.get_fan(followed)
        r = Relationship(f, "FOLLOWS", t)
        tx = self._graph.begin(autocommit=True)
        tx.create(r)

    def get_comment(self, comment_id):
        """

        :param comment_id: Comment ID
        :return: Comment
        """
        n = self.find_nodes_by_template({"label": "Comment", "template": {"comment_id": comment_id}})
        if n is not None and len(n) > 0:
            n = n[0]
        else:
            n = None

        return n

    def create_comment(self, uni, comment, team_id=None, player_id=None):
        """
        Creates a comment
        :param uni: The UNI for the Fan making the comment.
        :param comment: A simple string.
        :param team_id: A valid team ID or None. team_id and player_id cannot BOTH be None.
        :param player_id: A valid player ID or None
        :return: The Node representing the comment.
        """
        if uni is None or comment is None or (player_id is None and team_id is None):
            raise ValueError("create_comment: invalid input.")

        comment_id = str(uuid.uuid4())                      # Generate a UUID. Will explain in class.
        fan = None
        team = None
        player = None
        tx = None

        try:
            tx = self._graph.begin()  # We are going to make a transactional update.

            fan = self.get_fan(uni)                         # Get the node for the Fan.
            if fan is None:
                raise ValueError("create_comment: Fan node node found.")

            if team_id is not None:
                team = self.get_team(team_id)
                if team is None:
                    raise ValueError("create_comment: Team node node found.")

            if player_id is not None:
                player = self.get_player(player_id)
                if player is None:
                    raise ValueError("create_comment: Player node node found.")

            c = Node("Comment", comment_id=comment_id, comment=comment)
            tx.create(c)

            pc = Relationship(fan, "COMMENT_BY", c)
            tx.create(pc)

            if player is not None:
                pr = Relationship(c, "COMMENT_ON", player)
                tx.create(pr)

            if team is not None:
                p2 = Relationship(c, "COMMENT_ON", team)
                tx.create(p2)

            tx.commit()

            return c

        except Exception as e:
            if tx:
                tx.rollback()
            raise RuntimeError("create_comment: Something evil happened., e = " + str(e))

    def create_sub_comment(self, uni, origin_comment_id, comment):
        """
        Create a sub-comment (response to a comment or response) and links with parent in thread.
        :param uni: ID of the Fan making the comment.
        :param origin_comment_id: Id of the comment to which this is a response.
        :param comment: Comment string
        :return: Created comment.
        """
        if uni is None or origin_comment_id is None or comment is None:
            raise ValueError("create_sub_comment: invalid input.")

        comment_id = str(uuid.uuid4())  # Generate a UUID. Will explain in class.
        fan = None
        origin_comment = None
        tx = None

        try:
            tx = self._graph.begin()  # We are going to make a transactional update.

            fan = self.get_fan(uni)  # Get the node for the Fan.
            if fan is None:
                raise ValueError("create_sub_comment: Fan node node found.")

            origin_comment = self.get_comment(origin_comment_id)
            if origin_comment is None:
                raise ValueError("create_sub_comment: Original comment node not found.")

            c = Node("Comment", comment_id=comment_id, comment=comment)
            tx.create(c)

            sc = Relationship(c, "RESPONSE_TO", origin_comment)
            tx.create(sc)

            pc = Relationship(fan, "RESPONSE_BY", c)
            tx.create(pc)

            tx.commit()

        except Exception as e:
            if tx:
                tx.rollback()
            raise RuntimeError("create_comment: Something evil happened., e = " + str(e))

    def get_sub_comments(self, comment_id):
        """

        :param comment_id: The unique ID of the comment.
        :return: The sub-comments.
        """

        q = "match (c:Comment {comment_id: {cid}})<-[response:RESPONSE_TO]-(sc:Comment) return sc,response,c"
        c = self._graph.run(q, cid=comment_id)
        return c

    def get_roster(self, team_id, year_id):

        q = "match (t:Team {team_id: {tid}})<-[a:APPEARED {year: {yid}}]-(p:Player) " + \
            " return t.team_id, t.team_name, a.year, a.games, p.player_id, p.last_name, p.first_name"
        c = self._graph.run(q, tid=team_id, yid=year_id)

        return c

    def get_player_comments(self, player_id):
        """
        Gets all of the comments associated with a player, all of the comments on the comment and comments
        on the comments, etc. Also returns the Nodes for people making the comments.
        :param player_id: ID of the player.
        :return: Graph containing comment, comment streams and commenters.
        """

        q = 'match (fan)-[by:COMMENT_BY]->(comment)-[on:COMMENT_ON]->(player:Player {player_id: {pid}}) ' + \
            'return fan.uni, fan.last_name, fan.first_name, comment.comment_id, comment.comment,  ' + \
            " player.player_id, player.last_name, player.first_name "

        result = self._graph.run(q, pid=player_id)
        return result

    def get_player_comments_g(self, player_id):
        """
        Gets all of the comments associated with a player, all of the comments on the comment and comments
        on the comments, etc. Also returns the Nodes for people making the comments.
        :param player_id: ID of the player.
        :return: Graph containing comment, comment streams and commenters.
        """

        q = 'match (fan)-[by:COMMENT_BY]->(comment)-[on:COMMENT_ON]->(player:Player {player_id: {pid}}) ' + \
            'return fan, by, comment, on, player '

        result = self._graph.run(q, pid=player_id)
        return result

    def get_team_comments(self, team_id):
        """
        Gets all of the comments associated with a teams, all of the comments on the comment and comments
        on the comments, etc. Also returns the Nodes for people making the comments.
        :param player_id: ID of the team.
        :return: Graph containing comment, comment streams and commenters.
        """
        t = self.get_team(team_id)
        nodes = set()
        nodes.add(t)
        n = self._relationship_matcher.match(nodes, r_type="COMMENT_ON")
        return n

    def get_players_by_team(self, team_id):
        """

        :param team_id: Team ID
        :return: List of Nodes representing players who played for the team.
        """
        q = "match (p:Player)-[r:APPEARED]->(t:Team) where t.team_id={tid} return p,r,t"
        result = self._graph.run(q, tid=team_id)
        result = result.data()
        ans = []
        for r in result:
            current = dict(r['p'].items())
            current['year'] = r['r']['year']
            ans.append(current)

        return ans














"""
bryankr01   CHN
scherma01   WAS
abreujo02   CHA
ortizda01   BOS
jeterde01   NYA

"""
"""
# Create an APPEARED relationship from a player to a Team

    def create_appearance(self, player_id, team_id, year, games):
"""
"""
        :param player_id: Player ID
        :param team_id: Team ID
        :param year: Number of years
        :param games: Number of games played.
        :return: The created relationship.
"""

"""
        try:
            # This reads two nodes and then creates a relationship.
            # This has to be a transaction to avoid changes to the read nodes.
            tx = self._graph.begin(autocommit=False)

            f = self.get_player(player_id)
            t = self.get_team(team_id)
            r = self.get_appearance(player_id, team_id, year)
            if r is None:
                years = [year]
                gall = [games]
                r = Relationship(f, "APPEARED", t, years=years, games=gall)
                tx.create(r)
            else:
                if r['years'] is None:
                    r['years'] = [year]
                    r['games'] = [games]
                else:
                    r['years'].append(year)
                    r['games'].append(games)

                    tx.push(r)

            tx.commit()
            return r
        except Exception as e:
            print("create_appearances: exception = ", e)
"""
