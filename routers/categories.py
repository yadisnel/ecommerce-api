from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from starlette.status import HTTP_404_NOT_FOUND

from core.mongodb import AsyncIOMotorClient, get_database
from crud.categories import search_categories_impl
from crud.countries import exists_country_by_iso_code_impl
from erequests.categories import RequestFilterCategories
from models.categories import CategoryOut
from typing import List

router = APIRouter()


@router.get("/categories/{country_iso_code}", response_model=List[CategoryOut])
async def list_categories(country_iso_code: str = Path(..., title="Country iso code"),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    filter_categories: RequestFilterCategories = RequestFilterCategories(load_enabled=True,
                                                                         load_disabled=False,
                                                                         country_iso_code=country_iso_code)
    filter_categories.country_iso_code = filter_categories.country_iso_code.upper()
    exists_country: bool = await exists_country_by_iso_code_impl(
        country_iso_code=filter_categories.country_iso_code,
        conn=conn)
    if not exists_country:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Country does not exist.",
            )
    categories = await search_categories_impl(conn=conn, filter_categories=filter_categories)
    response: List[CategoryOut] = []
    for category in categories:
        response.append(CategoryOut(**category.dict()))
    return response
