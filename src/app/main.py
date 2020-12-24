from fastapi import FastAPI

from src.app.core.mongodb import connect_to_mongo, close_mongo_connection
from src.app.core.emqx import conect_to_broker, close_broker_cnx
from src.app.routers import users, products, shops, categories, provinces, messages, sync
from src.app.routers.dasboard.dashboard import router as dashboard_router


async def startup():
    await connect_to_mongo()
    await conect_to_broker()


async def shutdown():
    await close_mongo_connection()
    await close_broker_cnx()


app = FastAPI(title="Dtodo E-Commerce Platform API", version="0.1")
app.include_router(users.router, tags=["users"])
app.include_router(products.router, tags=["products"])
app.include_router(shops.router, tags=["shops"])
app.include_router(categories.router, tags=["categories"])
app.include_router(provinces.router, tags=["provinces"])
app.include_router(messages.router, tags=["messages"])
app.include_router(sync.router, tags=["sync"])
app.include_router(dashboard_router, tags=["dashboard"])
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
