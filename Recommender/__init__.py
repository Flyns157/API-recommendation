"""
__init__.py

This file is the entry point of the API. It initializes the FastAPI app and registers the routers.
"""
__version__ = "0.2.5"

from fastapi import FastAPI, Request

import logging
import time

# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),  # Log to a file
                        logging.StreamHandler()          # Also log to console
                    ])
main_logger = logging.getLogger(__name__)


class RecommenderFastAPI(FastAPI):
    def __init__(self, title: str = "Recommender-FastAPI", version: str = __version__, *args, **kwargs):
        super().__init__(title=title, version=version, *args, **kwargs)
        self.setup()

    def setup(self) -> None:
        self.setup_logging()
        self.setup_middleware()
        self.setup_routes()

    def setup_logging(self) -> None:
        self.logger = main_logger

    def setup_middleware(self) -> None:
        @self.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.perf_counter()
            self.logger.info(f"Request: {request.method} {request.url}")  # Log the request method and URL
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            self.logger.info(f"Processed {request.method} {request.url} in {process_time:.4f} secs")  # Log the processing time
            return response

    def setup_routes(self) -> None:
        # Import and register blueprints
        from .routers.em_router import router as em_router
        self.include_router(em_router)

        from .routers.mc_router import router as mc_router
        self.include_router(mc_router)

        from .routers.ja_router import router as ja_router
        self.include_router(ja_router)

        # from .auth import bp as auth_bp
        # self.register_blueprint(auth_bp)
        
        # from .routers import mc_recommendation_bp
        # self.register_blueprint(mc_recommendation_bp)
        
        # from .routers import em_recommendation_bp
        # self.register_blueprint(em_recommendation_bp)
        
        # from .routers import ja_recommendation_bp
        # self.register_blueprint(ja_recommendation_bp)

app = RecommenderFastAPI()
