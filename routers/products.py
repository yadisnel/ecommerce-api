import imghdr
import os
import uuid
from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Path
from fastapi import Body, HTTPException
from fastapi import Depends
from fastapi import File, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_412_PRECONDITION_FAILED, HTTP_406_NOT_ACCEPTABLE

from core.cloud_front import get_signed_url
from core.config import bucket_config
from core.config import image_big_resolution, image_thumb_resolution, product_max_images_count
from core.config import url_products_images_on_s3_big, url_products_images_on_s3_thumb
from core.generics import is_valid_oid
from core.image import size, resize
from core.mongodb import AsyncIOMotorClient, get_database
from core.path import root_path
from core.s3 import write_object_to_s3
from crud.categories import exists_category_by_id_impl
from crud.categories import get_category_by_id_impl, exists_sub_category_by_id_impl
from crud.categories import get_sub_category_by_id_impl
from crud.products import add_image_to_product_impl, remove_image_from_product_impl
from crud.products import add_product_impl, exists_product_by_id_impl, get_product_by_id_impl
from crud.products import exists_image_in_product_impl
from crud.products import remove_product_by_id_impl
from crud.products import search_products_impl
from crud.products import search_products_pagination_params_impl
from crud.products import set_product_favorited_impl, get_user_products_favorited_in_array
from crud.products import update_complete_product_by_id
from crud.zones import get_zone_by_id_impl
from models.categories import CategoryOut
from models.categories import SubCategoryOut
from models.images import ImageDb
from models.pagination_params import PaginationParams
from models.products import ProductIn, ProductDb, ProductOut, ProductFavoriteIn, ProductFavoriteOut
from models.zones import ZoneOut
from models.accounts import AccountDb
from routers.accounts import get_current_active_user
from erequests.paginations import RequestPagination, RequestPaginationParams
from erequests.products import RequestAddProduct, RequestUpdateProduct, RequestSetProductFavorited
from erequests.products import RequestSearchProducts

router = APIRouter()


@router.post("/products/", response_model=ProductOut)
async def add_one_product(current_user: AccountDb = Depends(get_current_active_user),
                          req: RequestAddProduct = Body(..., title="Product"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    if current_user.shop.zone_id is None:
        raise HTTPException(
            status_code=HTTP_412_PRECONDITION_FAILED,
            detail="Shop creation is incomplete.",
        )
    if not is_valid_oid(oid=req.category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_category: bool = await exists_category_by_id_impl(category_id=req.category_id, conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_subcategory: bool = await exists_sub_category_by_id_impl(category_id=req.category_id,sub_category_id=req.sub_category_id, conn=conn)
    if not exists_subcategory:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid sub-category id.",
        )
    category_out: CategoryOut = await get_category_by_id_impl(category_id=req.category_id, conn=conn)
    sub_category_out: SubCategoryOut = await get_sub_category_by_id_impl(category_id=req.category_id,sub_category_id=req.sub_category_id, conn=conn)
    zone_out: ZoneOut = await get_zone_by_id_impl(zone_id=current_user.shop.zone_id, conn=conn)
    product_in: ProductIn = ProductIn()
    product_in.local_id = req.local_id
    product_in.user_id = current_user.id
    product_in.name = req.name
    product_in.description = req.description
    product_in.category_id = req.category_id
    product_in.category_name = category_out.name
    product_in.sub_category_id = req.sub_category_id
    product_in.sub_category_name = sub_category_out.name
    product_in.zone_id = zone_out.id
    product_in.zone_name = zone_out.name
    product_in.price = req.price
    product_in.isNew = req.isNew
    product_in.currency = req.currency
    product_in.views = 0
    product_in.likes = 0
    product_in.score = 0
    product_in.created = datetime.utcnow()
    product_in.location = current_user.shop.location
    product_in.images = []
    product_in.promoted = False
    product_in.deleted = False
    product_db : ProductDb = await add_product_impl(user_id=current_user.id, product_in=product_in, conn=conn)
    products_ids: List[str] = [product_db.id]
    dict_favorite: Dict = await get_user_products_favorited_in_array(user_id=current_user.id, products_ids=products_ids,conn=conn)
    product_out: ProductOut = ProductOut(**product_db.dict())
    if product_out.id in dict_favorite:
        product_out.favorited = dict_favorite[product_out.id]
    else:
        product_out.favorited = False
    return product_out


@router.put("/products/{product_id}", response_model=ProductOut)
async def update_one_product(current_user: AccountDb = Depends(get_current_active_user),
                             product_id: str = Path(..., title="Product id"),
                             req: RequestUpdateProduct = Body(..., title="Product"),
                             conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=req.category_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    if not is_valid_oid(oid=product_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    exists_product: bool = await exists_product_by_id_impl(
        user_id=current_user.id,
        product_id=product_id,
        conn=conn)
    if not exists_product:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    exists_category: bool = await exists_category_by_id_impl(
        category_id=req.category_id,
        conn=conn)
    if not exists_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid category id.",
        )
    exists_subcategory: bool = await exists_sub_category_by_id_impl(
        category_id=req.category_id,
        sub_category_id=req.sub_category_id,
        conn=conn)
    if not exists_subcategory:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid sub-category id.",
        )
    category_out: CategoryOut = await get_category_by_id_impl(
        category_id=req.category_id,
        conn=conn)
    sub_category_out: SubCategoryOut = await get_sub_category_by_id_impl(
        category_id=req.category_id,
        sub_category_id=req.sub_category_id,
        conn=conn)
    product_db: ProductDb = await get_product_by_id_impl(
        user_id=current_user.id,
        product_id=product_id,
        conn=conn)
    product_db.name = req.name
    product_db.description = req.description
    product_db.category_id = req.category_id
    product_db.category_name = category_out.name
    product_db.sub_category_name = sub_category_out.name
    product_db.price = req.price
    product_db.isNew = req.isNew
    product_db.currency = req.currency
    product_db.location = current_user.shop.location
    product_db : ProductDb = await update_complete_product_by_id(
        user_id=current_user.id,
        product_id=product_id,
        product_in=ProductIn(**product_db.dict()),
        conn=conn)
    products_ids: List[str] = [product_db.id]
    dict_favorited: Dict = await get_user_products_favorited_in_array(
        user_id=current_user.id,
        products_ids=products_ids,
        conn=conn)
    product_out: ProductOut = ProductOut(**product_db.dict())
    if product_out.id in dict_favorited:
        product_out.favorited = dict_favorited[product_out.id]
    else:
        product_out.favorited = False
    return product_out


@router.delete("/products/{product_id}")
async def remove_product(current_user: AccountDb = Depends(get_current_active_user),
                         product_id: str = Path(..., title="Product id"),
                         conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=product_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    exists_product: bool = await exists_product_by_id_impl(user_id=current_user.id, product_id=product_id,
                                                           conn=conn)
    if not exists_product:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    await remove_product_by_id_impl(user_id=current_user.id, product_id=product_id, conn=conn)
    return {"success": True}


@router.post("/products/{product_id}/images", response_model=ProductOut)
async def add_image_to_product(current_user: AccountDb = Depends(get_current_active_user),
                               product_id: str = Path(..., title="Product id"),
                               file: UploadFile = File(...),
                               conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=product_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    exists_product: bool = await exists_product_by_id_impl(user_id=current_user.id, product_id=product_id, conn=conn)
    if not exists_product:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    product_product_out = await get_product_by_id_impl(user_id=current_user.id, product_id=product_id, conn=conn)
    if product_product_out.images is None or len(product_product_out.images)  == product_max_images_count:
        raise HTTPException(
            status_code=HTTP_406_NOT_ACCEPTABLE,
            detail="Only 10 images per product are allowed.",
        )
    filename_original = str(uuid.UUID(bytes=os.urandom(16), version=4)) + "_original_.png"
    filename_big = str(uuid.UUID(bytes=os.urandom(16), version=4)) + "_big_.png"
    filename_thumb = str(uuid.UUID(bytes=os.urandom(16), version=4)) + "_thumb_.png"
    file_path = os.path.join(root_path(), 'tmp', filename_original)
    file_bytes_original = await file.read()
    file_bytes_big = resize(file_bytes_original, image_big_resolution)
    file_bytes_thumb = resize(file_bytes_original, image_thumb_resolution)
    with open(file_path, 'wb') as f:
        f.write(file_bytes_original)
    isvalid = imghdr.what(os.path.join(file_path)) is not None
    os.remove(file_path)
    if not isvalid:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="File must be image type.",
        )
    key_big = url_products_images_on_s3_big + filename_big
    key_thumb = url_products_images_on_s3_thumb + filename_thumb
    write_object_to_s3(file_bytes=file_bytes_big, bucket=bucket_config.name(),
                       key=key_big, region_name=bucket_config.region())
    write_object_to_s3(file_bytes=file_bytes_thumb, bucket=bucket_config.name(),
                       key=key_thumb, region_name=bucket_config.region())
    original_height, original_width = size(file_bytes_big)
    original_size = len(file_bytes_big)
    thumb_height, thumb_width = size(file_bytes_thumb)
    thumb_size = len(file_bytes_thumb)
    image_in: ImageDb = ImageDb()
    image_in.id = str(uuid.UUID(bytes=os.urandom(16), version=4))
    image_in.original_key = key_big
    image_in.original_url = get_signed_url(s3_key=image_in.original_key)
    image_in.original_width = original_width
    image_in.original_height = original_height
    image_in.original_size = original_size
    image_in.thumb_key = key_thumb
    image_in.thumb_url = get_signed_url(s3_key=image_in.thumb_key)
    image_in.thumb_width = thumb_width
    image_in.thumb_height = thumb_height
    image_in.thumb_size = thumb_size
    product_db: ProductDb = await add_image_to_product_impl(user_id=current_user.id, product_id=product_id,
                                                            image_in=image_in, conn=conn)
    products_ids: List[str] = [product_db.id]
    dict_favorited: Dict = await get_user_products_favorited_in_array(user_id=current_user.id,
                                                                      products_ids=products_ids, conn=conn)
    product_out: ProductOut = ProductOut(**product_db.dict())
    if product_out.id in dict_favorited:
        product_out.favorited = dict_favorited[product_out.id]
    else:
        product_out.favorited = False
    return product_out


@router.delete("/products/{product_id}/images/{image_id}", response_model=ProductOut)
async def remove_image_from_product(current_user: AccountDb = Depends(get_current_active_user),
                                    product_id: str = Path(..., title="Product id"),
                                    image_id: str = Path(..., title="Image id"),
                                    conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=product_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    exists_image: bool = await exists_image_in_product_impl(
        user_id=current_user.id, product_id=product_id,
        image_id=image_id,
        conn=conn)
    if not exists_image:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid image id.",
        )
    exists_product: bool = await exists_product_by_id_impl(
        user_id=current_user.id,
        product_id=product_id,
        conn=conn)
    if not exists_product:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    product_db: ProductDb = await remove_image_from_product_impl(
        user_id=current_user.id,
        product_id=product_id,
        image_id=image_id, conn=conn)
    products_ids: List[str] = [product_db.id]
    dict_favorited: Dict = await get_user_products_favorited_in_array(
        user_id=current_user.id,
        products_ids=products_ids,
        conn=conn)
    product_out: ProductOut = ProductOut(**product_db.dict())
    if product_out.id in dict_favorited:
        product_out.favorited = dict_favorited[product_out.id]
    else:
        product_out.favorited = False
    return product_out


@router.get("/products/pagination-params", response_model=PaginationParams)
async def list_products_pagination_params(current_user: AccountDb = Depends(get_current_active_user),
                                          filter: RequestSearchProducts = Body(..., title="Filter"),
                                          request_pagination_params: RequestPaginationParams = Body(...,title="Pagination params"),
                                          conn: AsyncIOMotorClient = Depends(get_database)):
    if filter is not None:
        if filter.zone_id is not None:
            if not is_valid_oid(oid=filter.zone_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                )
    if filter is not None:
        if filter.category_id is not None:
            if not is_valid_oid(oid=filter.category_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid category id.",
                )
    return await search_products_pagination_params_impl(user_id=current_user.id, filter=filter, request_pagination_params=request_pagination_params, conn=conn)


@router.get("/products", response_model=List[ProductOut])
async def list_products(current_user: AccountDb = Depends(get_current_active_user),
                        filter: RequestSearchProducts = Body(None, title="Filter"),
                        pagination: RequestPagination = Body(..., title="Pagination"),
                        conn: AsyncIOMotorClient = Depends(get_database)):
    if filter is not None:
        if filter.zone_id is not None:
            if not is_valid_oid(oid=filter.zone_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                )
    if filter is not None:
        if filter.category_id is not None:
            if not is_valid_oid(oid=filter.category_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid category id.",
                )
    return await search_products_impl(
        user_id=current_user.id,
        filter=filter,
        pagination=pagination,
        conn=conn)


@router.put("/products/{product_id}/favorited", response_model=ProductFavoriteOut)
async def set_product_favorited(
        current_user: AccountDb = Depends(get_current_active_user),
        product_id: str = Path(..., title="Product id"),
        favorited: RequestSetProductFavorited = Body(..., title="Favorited"),
        conn: AsyncIOMotorClient = Depends(get_database)):
    if not is_valid_oid(oid=product_id):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    exists_product: bool = await exists_product_by_id_impl(
        user_id=current_user.id,
        product_id=product_id,
        conn=conn)
    if not exists_product:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid product id.",
        )
    product_favorited_in: ProductFavoriteIn = ProductFavoriteIn()
    product_favorited_in.product_id = product_id
    product_favorited_in.user_id = current_user.id
    product_favorited_in.favorited= favorited
    return await set_product_favorited_impl(
        product_favorited=product_favorited_in,
        conn=conn)