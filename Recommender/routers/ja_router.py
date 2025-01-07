"""
This file contains the API routes for Jean-Alexis Recommendation Engine.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer

from ..core.ja_engine import JA_engine
from ..database import get_database
from ..utils.config import Config

from .. import main_logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/recommend/JA", tags=["Jean-Alexis Recommendation"])


def get_current_user(token: str = Depends(oauth2_scheme)):
    # This function would contain the logic to verify the user token
    # For now, we just simulate it by returning the token as the user
    if Config.NO_AUTH:
        return None
    return token

@router.get("/users")
async def recommend_users(
    user_id: str = Query(..., description="The ID of the user requesting recommendations."),
    follow_weight: float = Query(0.5, description="The weight given to mutual followers in scoring."),
    interest_weight: float = Query(0.5, description="The weight given to shared interests in scoring."),
    page: int = Query(1, description="The page number for pagination."),
    page_size: int = Query(10, description="The number of recommendations per page.")
) -> dict[str, list[str]]:
    """
    Recommend user profiles based on shared interests and mutual connections with pagination.
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id parameter")

    try:
        recommendations = JA_engine(get_database()).recommend_users(user_id, follow_weight, interest_weight)
        
        # Implement pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_recommendations = recommendations[start_index:end_index]

        return {"recommended_users": paginated_recommendations}
    except Exception as e:
        main_logger.error(f"Error in recommend_users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts")
async def recommend_posts(
    user_id: str = Query(..., description="The ID of the user requesting recommendations."),
    interest_weight: float = Query(0.7, description="The weight given to shared interests in scoring."),
    interaction_weight: float = Query(0.3, description="The weight given to user interactions (likes, comments) in scoring."),
    page: int = Query(1, description="The page number for paginated results."),
    page_size: int = Query(10, description="The number of recommendations to return per page."),
) -> dict[str, list[str]]:
    """
    Recommend posts based on shared interests and user interactions.
    Pagination is implemented to manage the number of results returned.
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id parameter")

    try:
        recommendations = JA_engine(get_database()).recommend_posts(user_id)
        
        # Implement pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_recommendations = recommendations[start_index:end_index]

        return {"recommended_posts": paginated_recommendations}
    except Exception as e:
        main_logger.error(f"Error in recommend_posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
