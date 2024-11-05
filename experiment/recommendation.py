from neo4j import GraphDatabase
import random

# Initialize the Neo4j driver
uri = "bolt://localhost:7687"  # Adjust the URI as needed
driver = GraphDatabase.driver(uri)  # no auth here else add : auth=("neo4j", "password")

def get_hastags(id_user:int)->set:
    """
    Retrieve hashtags used by a specific user.

    Args:
        id_user (int): The ID of the user.

    Returns:
        set: A set of hashtags used by the user.
    """
    with driver.session() as session:
        hashtags = session.run(
            "MATCH (p:posts) WHERE p.id_author = $id_user RETURN p.keys AS hashtags",
            id_user=str(id_user)
        )
        hashtag_set = set()
        for record in hashtags:
            hashtag_set.update(record["hashtags"])
        return hashtag_set

def profile_recommendation(id_user:int)->list[int]:
    """
    Generate profile recommendations for a specific user based on mutual follows and interests.

    Args:
        id_user (int): The ID of the user.

    Returns:
        list: A sorted list of recommended user IDs.
    """
    with driver.session() as session:
        user = session.run(
            "MATCH (u:users) WHERE u.id_user = $id_user RETURN u",
            id_user=str(id_user)
        ).single()

        users = session.run(
            "MATCH (u:users) WHERE u.id_user <> $id_user RETURN u"
        )

        scores = {}
        user_follows = {rel.end_node for rel in session.run(
            "MATCH (u:users)-[f:FOLLOWS]->(f2:users) WHERE u.id_user = $id_user RETURN f2",
            id_user=id_user
        )}

        user_interests = set(user["u"]["interest"])

        for u in users:
            u_follows = {rel.end_node for rel in session.run(
                "MATCH (u:users)-[f:FOLLOWS]->(f2:users) WHERE u.id_user = $id_user RETURN f2",
                id_user=u["u"]["id_user"]
            )}

            follows_score = len(user_follows & u_follows) / len(user_follows | u_follows) if user_follows and u_follows else 0
            u_interests = set(u["u"]["interest"])
            interests_score = len(user_interests & u_interests) / len(user_interests | u_interests) if user_interests and u_interests else 0

            rec_score = follows_score + interests_score
            scores[u["u"]["id_user"]] = rec_score

        return sorted(scores, key=scores.get, reverse=True)

def posts_recommendation(id_user:int)->list[int]:
    """
    Generate post recommendations for a specific user based on hashtags and interests.

    Args:
        id_user (int): The ID of the user.

    Returns:
        list: A sorted list of recommended post IDs.
    """
    with driver.session() as session:
        posts = session.run(
            "MATCH (p:posts) WHERE p.id_author <> $id_user RETURN p",
            id_user=str(id_user)
        )

        user_hashtags = get_hastags(id_user)
        scores = {}

        if not user_hashtags:
            user_interests = session.run(
                "MATCH (u:users) WHERE u.id_user = $id_user RETURN u.interests AS interests",
                id_user=id_user
            ).single()["interests"]

            for post in posts:
                u = session.run(
                    "MATCH (u:users) WHERE u.id_user = $id_author RETURN u.interests AS interests",
                    id_author=post["id_author"]
                ).single()["interests"]

                interests_score = len(set(user_interests) & set(u)) / len(set(user_interests) | set(u))
                scores[post["id_post"]] = interests_score
        else:
            for post in posts:
                post_hashtags = set(post["keys"])
                score = len(user_hashtags & post_hashtags) / len(user_hashtags | post_hashtags)
                scores[post["id_post"]] = score

        scores_tab = sorted(scores, key=scores.get, reverse=True)

        for s in range(len(scores_tab)):
            if random.random() >= 0.8:
                scores_tab.insert(s, scores_tab[-1])
                del scores_tab[-1]

        return scores_tab

# Close the driver when done
driver.close()
