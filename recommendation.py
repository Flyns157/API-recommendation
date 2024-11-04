from py2neo import Graph, RelationshipMatcher, Node, Relationship
import random

graphe = Graph(host="localhost")


def get_hastags(id_user):
    matcher = graphe.nodes
    id_user = str(id_user)
    hashtags_nodes = matcher.match("posts").where("_.id_author = " + id_user)

    hashtags = set()
    for h in hashtags_nodes:
        for hashtag in h["keys"]:
            hashtags.add(hashtag)

    return hashtags


def profile_recommendation(id_user):
    matcher = graphe.nodes
    id_user = str(id_user)
    user = matcher.match("users").where("_.id_user = " + id_user).first()
    users = matcher.match("users").where("_.id_user <> " + id_user)

    scores = {}

    match_relation = RelationshipMatcher(graphe)
    user_relation = match_relation.match(nodes=(user, None), r_type="FOLLOWS")
    user_follows = {us.end_node for us in user_relation}

    user_interests = {interest for interest in user["interest"]}

    for u in users:
        relation = match_relation.match(nodes=(u, None), r_type="FOLLOWS")
        u_follows = {us.end_node for us in relation}

        if (len(user_follows) == 0) or (len(u_follows) == 0):
            follows_score = 0
        else:
            follows_score = len(user_follows & u_follows) / len(user_follows | u_follows)

        u_interests = {interest for interest in u["interest"]}
        interests_score = len(user_interests & u_interests) / len(user_interests | u_interests)

        rec_score = follows_score + interests_score
        scores[u["id_user"]] = rec_score

    return sorted(scores, key=scores.get, reverse=True)

def posts_recommendation(id_user) :
    matcher = graphe.nodes
    id_user = str(id_user)
    posts = matcher.match("posts").where("_.id_author <> " + id_user)

    user_hashtags = get_hastags(id_user)

    scores = {}

    if len(user_hashtags) == 0 :
        user = matcher.match("users").where("_.id_user = " + id_user).first()
        user_interests = {interest for interest in user["interests"]}

        for post in posts :
            u = matcher.match("users").where("_.id_user = " + post["id_author"])
            u_interests = {interest for interest in u["interests"]}

            interests_score = len(user_interests & u_interests) / len(user_interests | u_interests)
            scores[post["id_post"]] = interests_score
    else :
        for post in posts :
            post_hashtags = {h for h in post["keys"]}

            score = len(user_hashtags & post_hashtags) / len(user_hashtags | post_hashtags)
            scores[post["id_post"]] = score

    scores_tab = sorted(scores, key=scores.get, reverse=True)

    for s in range(len(scores_tab)) :
        if random.random() >= 0.8 :
            scores_tab.insert(s,scores_tab[-1])
            del scores_tab[-1]

    return scores_tab