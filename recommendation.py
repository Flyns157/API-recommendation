from py2neo import Graph, RelationshipMatcher, Node

graphe = Graph(host="localhost")

def getHastags(id_user):
    matcher = graphe.nodes
    id_user = str(id_user)
    hashtagsNodes = matcher.match("posts").where("_.id_author = " + id_user)

    hashtags = set()
    for h in hashtagsNodes:
        for hashtag in h["keys"]:
                hashtags.add(hashtag)

    return hashtags

def profileRecommendation(id_user):
    matcher = graphe.nodes
    id_user = str(id_user)
    user = matcher.match("users").where("_.id_user = " + id_user).first()
    users = matcher.match("users").where("_.id_user <> " + id_user)

    scores = {}

    matchRelation = RelationshipMatcher(graphe)
    userRelation = matchRelation.match(nodes=(user, None), r_type="FOLLOWS")
    userFollows = {us.end_node for us in userRelation}

    for u in users:
        relation = matchRelation.match(nodes=(u, None), r_type="FOLLOWS")
        uFollows = {us.end_node for us in relation}

        recScore = len(userFollows & uFollows) / len(userFollows | uFollows)
        print(recScore)
        scores[u["id_user"]] = recScore
        print(scores)

    return sorted(scores, key=scores.get, reverse=True)
