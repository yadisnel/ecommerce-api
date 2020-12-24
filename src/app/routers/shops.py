import imghdr
import os
import uuid

from fastapi import APIRouter
from fastapi import Body, HTTPException
from fastapi import Depends
from fastapi import File, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE

from src.app.core.config import bucket_config
from src.app.core.config import url_shops_images_on_s3_big, url_shops_images_on_s3_thumb
from src.app.core.image import resize, size
from src.app.core.path import root_path
from src.app.core.s3 import write_object_to_s3
from src.app.crud.products import update_all_products_shop_info_impl
from src.app.crud.users import add_image_to_shop_impl, remove_image_from_shop_impl, exists_image_in_shop_by_id_impl
from src.app.crud.users import update_complete_shop_by_user_id
from src.app.crud.users import remove_all_images_from_shop_impl
from src.app.core.mongodb import AsyncIOMotorClient, get_database
from src.app.models.image import Image
from src.app.models.shop import ShopIn
from src.app.models.user import UserDb
from src.app.models.user import UserOut
from src.app.routers.users import get_current_active_user
from src.app.validations.shops import RequestUpdateShop, RequestDeleteImageFromShop
from src.app.models.location import Location
from src.app.core.generics import is_valid_oid
from src.app.crud.provinces import exists_province_by_id_impl, get_province_by_id_impl
from src.app.models.province import ProvinceOut
from src.app.core.config import image_thumb_resolution, image_big_resolution, shop_max_images_count
from src.app.core.cloud_front import get_signed_url

router = APIRouter()


@router.post("/shops/update-shop", response_model=UserOut)
async def update_shop(current_user: UserDb = Depends(get_current_active_user),
                          req: RequestUpdateShop = Body(..., title="Shop"),
                          conn: AsyncIOMotorClient = Depends(get_database)):
    async with await conn.start_session() as s:
        async with s.start_transaction():
            if not is_valid_oid(oid=req.province_id):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid province id.",
                )
            exists_province: bool = await exists_province_by_id_impl(province_id=req.province_id, conn=conn)
            if not exists_province:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid province id.",
                )
            province_out: ProvinceOut = await get_province_by_id_impl(province_id=req.province_id, conn=conn)
            shop_in: ShopIn = ShopIn(**current_user.shop.dict())
            shop_in.name = req.name
            shop_in.province_id = req.province_id
            shop_in.province_name = province_out.name
            if req.location is not None:
                location: Location = Location()
                location.type = "Point"
                location.coordinates = []
                location.coordinates.append(req.location.lat)
                location.coordinates.append(req.location.long)
                shop_in.location = location
            else:
                shop_in.location = None
            shop_in.images = current_user.shop.images
            await update_all_products_shop_info_impl(user_id=current_user.id, location=shop_in.location, province_id=req.province_id, province_name=province_out.name, conn=conn)
            user_db = await update_complete_shop_by_user_id(user_id=current_user.id, shop_in=shop_in, conn=conn)
            user_out: UserOut = UserOut(**user_db.dict())
            return user_out


@router.post("/shops/add-image-to-shop", response_model=UserOut)
async def add_image_to_shop(current_user: UserDb = Depends(get_current_active_user),
                            file: UploadFile = File(...),
                            conn: AsyncIOMotorClient = Depends(get_database)):
    if current_user.shop is None or  current_user.shop.images is None or len(current_user.shop.images) == shop_max_images_count:
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
    write_object_to_s3(file_bytes=file_bytes_big, bucket=bucket_config.name(),
                       key=key_big, region_name=bucket_config.region())
    write_object_to_s3(file_bytes=file_bytes_thumb, bucket=bucket_config.name(),
                       key=key_thumb, region_name=bucket_config.region())
    original_height, original_width = size(file_bytes_big)
    original_size = len(file_bytes_big)
    thumb_height, thumb_width = size(file_bytes_thumb)
    thumb_size = len(file_bytes_thumb)
    image_in: Image = Image()
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
    user_db = await add_image_to_shop_impl(user_id=current_user.id, image_in=image_in, conn=conn)
    user_out: UserOut = UserOut(**user_db.dict())
    return user_out


@router.post("/shops/remove-image-from-shop", response_model=UserOut)
async def remove_image_from_shop(current_user: UserDb = Depends(get_current_active_user),
                                 req: RequestDeleteImageFromShop = Body(..., title="Image"),
                                 conn: AsyncIOMotorClient = Depends(get_database)):
    exists_image: bool = await exists_image_in_shop_by_id_impl(user_id=current_user.id, image_id=req.image_id,
                                                         conn=conn)
    if not exists_image:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid image id.",
        )
    user_db = await remove_image_from_shop_impl(user_id=current_user.id, image_id=req.image_id, conn=conn)
    user_out: UserOut = UserOut(**user_db.dict())
    return user_out


@router.post("/shops/remove-all-images-from-shop", response_model=UserOut)
async def remove_all_images_from_shop(current_user: UserDb = Depends(get_current_active_user),
                                 conn: AsyncIOMotorClient = Depends(get_database)):
    user_db = await remove_all_images_from_shop_impl(current_user=current_user, conn=conn)
    user_out: UserOut = UserOut(**user_db.dict())
    return user_out
