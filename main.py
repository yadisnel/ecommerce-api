from fastapi import FastAPI

from core.mongodb import connect_to_mongo, close_mongo_connection
from core.emqx import conect_to_broker, close_broker_cnx
from routers import zones, chat, sync
from routers import shops
from routers import products, accounts, categories
from routers.dasboard import router as dashboard_router


async def startup():
    await connect_to_mongo()
    await conect_to_broker()


async def shutdown():
    await close_mongo_connection()
    await close_broker_cnx()


app = FastAPI(title="E-Commerce Platform API", version="v1.0-beta.1")
app.include_router(accounts.router, tags=["accounts"])
app.include_router(products.router, tags=["products"])
app.include_router(shops.router, tags=["shops"])
app.include_router(categories.router, tags=["categories"])
app.include_router(zones.router, tags=["zones"])
app.include_router(chat.router, tags=["chat"])
app.include_router(sync.router, tags=["sync"])
app.include_router(dashboard_router, tags=["dashboard"])
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
