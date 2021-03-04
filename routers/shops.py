import imghdr
import os
import uuid

from fastapi import APIRouter
from fastapi import Body, HTTPException, Path
from fastapi import Depends
from fastapi import File, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE, HTTP_401_UNAUTHORIZED

from core.config import bucket_config
from core.config import url_shops_images_on_s3_big, url_shops_images_on_s3_thumb
from core.image import resize, size
from core.path import root_path
from core.s3 import write_object_to_s3
from crud.countries import exists_country_by_iso_code_impl
from crud.products import update_all_products_shop_info_impl
from crud.shops import (
    add_image_to_shop_impl, remove_image_from_shop_impl, exists_image_in_shop_by_id_impl,
    add_shop_impl, get_shop_by_id_impl, update_shop_by_id, exists_shop_by_id_impl,
    )
from crud.shops import remove_all_images_from_shop_impl
from core.mongodb import AsyncIOMotorClient, get_database
from models.images import ImageDb
from models.shops import ShopOut, ShopDb
from models.accounts import AccountDb
from models.accounts import AccountOut
from models.zones import ZoneDb
from routers.accounts import get_current_active_user
from erequests.shops import RequestUpdateShop, RequestAddShop
from core.generics import is_valid_oid
from crud.zones import exists_zone_by_id_impl, get_zone_by_id_impl
from core.config import image_thumb_resolution, image_big_resolution, shop_max_images_count
from core.cloud_front import get_signed_url

router = APIRouter()


@router.post("/shops", response_model=ShopOut)
async def add_shop(current_user: AccountDb = Depends(get_current_active_user),
                   e_request: RequestAddShop = Body(..., title="body request"),
                   conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            if not is_valid_oid(oid=e_request.zone_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                    )
            exists_zone: bool = await exists_zone_by_id_impl(zone_id=e_request.zone_id, conn=conn)
            if not exists_zone:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                    )
            zone_db: ZoneDb = await get_zone_by_id_impl(zone_id=e_request.zone_id, conn=conn)
            exists_country: bool = await exists_country_by_iso_code_impl(
                country_iso_code=zone_db.country_iso_code, conn=conn)
            if not exists_country:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Country code not supported.",
                    )
            return await add_shop_impl(e_request=e_request, account_id=current_user.id, conn=conn)


@router.put("/shops/{shop_id}", response_model=ShopOut)
async def update_shop(current_user: AccountDb = Depends(get_current_active_user),
                      shop_id: str = Path(..., title="Shop id"),
                      e_request: RequestUpdateShop = Body(..., title="body request"),
                      conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            if not is_valid_oid(oid=e_request.zone_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                    )
            exists_zone: bool = await exists_zone_by_id_impl(zone_id=e_request.zone_id, conn=conn)
            if not exists_zone:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid zone id.",
                    )
            shop_db: ShopDb = await get_shop_by_id_impl(shop_id=shop_id, conn=conn)
            if current_user.id != shop_db.account_id:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="User is unauthorized to change this shop.",
                    )
            shop_db = await update_shop_by_id(shop_id=shop_id, e_request=e_request, conn=conn)
            await update_all_products_shop_info_impl(shop_db=shop_db, conn=conn)
            return ShopOut(**shop_db.dict())


@router.post("/shops/{shop_id}/images/", response_model=ShopOut)
async def add_image_to_shop(current_user: AccountDb = Depends(get_current_active_user),
                            shop_id: str = Path(..., title="Shop id"),
                            file: UploadFile = File(...),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    exists_shop: bool = await exists_shop_by_id_impl(shop_id=shop_id, conn=conn)
    if not exists_shop:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Shop does not exists.",
            )
    shop_db: ShopDb = await get_shop_by_id_impl(shop_id=shop_id, conn=conn)
    if current_user.id != shop_db.account_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is unauthorized to change this shop.",
            )
    if len(shop_db.images) == shop_max_images_count:
        raise HTTPException(
            status_code=HTTP_406_NOT_ACCEPTABLE,
            detail="Only 10 images per shop are allowed.",
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
    key_big = url_shops_images_on_s3_big + filename_big
    key_thumb = url_shops_images_on_s3_thumb + filename_thumb
    write_object_to_s3(
        file_bytes=file_bytes_big,
        bucket=bucket_config.name(),
        key=key_big,
        region_name=bucket_config.region())
    write_object_to_s3(
        file_bytes=file_bytes_thumb,
        bucket=bucket_config.name(),
        key=key_thumb,
        region_name=bucket_config.region())
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
    shop_db = await add_image_to_shop_impl(
        shop_id=current_user.id,
        image_in=image_in,
        conn=conn)
    return ShopOut(**shop_db.dict())


@router.delete("/shops/{shop_id}/images/{image_id}", response_model=ShopOut)
async def remove_image_from_shop(current_user: AccountDb = Depends(get_current_active_user),
                                 shop_id: str = Path(..., title="Shop id."),
                                 image_id: str = Path(..., title="Image id."),
                                 conn: AsyncIOMotorClient = Depends(get_database)):
    exists_shop: bool = await exists_shop_by_id_impl(shop_id=shop_id, conn=conn)
    if not exists_shop:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Shop does not exists.",
            )
    shop_db: ShopDb = await get_shop_by_id_impl(shop_id=shop_id, conn=conn)
    if current_user.id != shop_db.account_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is unauthorized to change this shop.",
            )
    exists_image: bool = await exists_image_in_shop_by_id_impl(
        shop_id=shop_db.id,
        image_id=image_id,
        conn=conn)
    if not exists_image:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid image id.",
            )
    user_db = await remove_image_from_shop_impl(shop_id=shop_id,
                                                image_id=image_id,
                                                conn=conn)
    user_out: AccountOut = AccountOut(**user_db.dict())
    return user_out


@router.delete("/shops/{shop_id}/images", response_model=ShopOut)
async def remove_all_images_from_shop(current_user: AccountDb = Depends(get_current_active_user),
                                      shop_id: str = Path(..., title="Shop id."),
                                      conn: AsyncIOMotorClient = Depends(get_database)):
    exists_shop: bool = await exists_shop_by_id_impl(shop_id=shop_id, conn=conn)
    if not exists_shop:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Shop does not exists.",
            )
    shop_db: ShopDb = await get_shop_by_id_impl(shop_id=shop_id, conn=conn)
    if current_user.id != shop_db.account_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User is unauthorized to change this shop.",
            )
    shop_db = await remove_all_images_from_shop_impl(shop=shop_db,
                                                     conn=conn)
    return ShopOut(**shop_db.dict())
