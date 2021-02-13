from databases import DatabaseURL

# Database config local
db_host: str = '127.0.0.1'
admin_user: str = "boukker"
admin_pass: str = "Boukker.123"
db_port: int = 27017
db_user_db = "admin"

# Database config prod
# db_host: str = '18.158.96.25'
# db_port: int = 27017
# admin_user: str = "admin"
# admin_pass: str = "HyperMongoDb2021*"
# db_user_db = "admin"

db_url = DatabaseURL(
    f"mongodb://{admin_user}:{admin_pass}@{db_host}:{db_port}/{db_user_db}"
)
max_connections_count: int = 100
min_conections_count: int = 10

# Database collections
ecommerce_database_name = "ecommercedb"
accounts_collection_name = "accounts"
pending_accounts_collection_name = "pending_accounts"

shops_collection_name = "shops"
products_collection_name = "products"
categories_collection_name = "categories"
zones_collection_name = "zones"
countries_collection_name = "countries"
product_favorites_collection_name = "product_favorites"
conversations_collection_name = "conversations"
messges_collection_name = "messages"

# Broker config
broker_host: str = "192.168.1.104"
broker_port: int = 1883

# User roles
users_roles = {'admin': 'admin', 'user': 'user'}

# Images  resulutions
image_big_resolution: int = 800
image_thumb_resolution: int = 250

# S3 url keys
url_shops_images_on_s3_big: str = "shops/big/"
url_shops_images_on_s3_thumb: str = "shops/thumb/"
url_products_images_on_s3_big: str = "products/big/"
url_products_images_on_s3_thumb: str = "products/thumb/"
url_users_images_on_s3_big: str = "users/big/"
url_users_images_on_s3_thumb: str = "users/thumb/"

# Payload types
PAYLOAD_TYPE_ZONE: str = "PAYLOAD_TYPE_ZONE"
PAYLOAD_TYPE_COUNTRY: str = "PAYLOAD_TYPE_COUNTRY"
PAYLOAD_TYPE_PRODUCT: str = "PAYLOAD_TYPE_PRODUCT"
PAYLOAD_TYPE_CATEGORY: str = "PAYLOAD_TYPE_CATEGORY"

# Testing config
test_facebook_user_id: str = "10215843908959707"
test_facebook_user_token: str = "EAAL9ehJnWAABADMFJx7qZBi7zBvcAZC4rH8OLayZBIZATIkEZAzgJYnBfVq4X2BM1l1gM3ko5x1ByKjlQVtxSYGTVZBUIsYxMs0c8ZA771XKDEZBMR1kHGzws8sBoY5Fx7H0YWysfblX4VwnVRK3vhqjOSNUXdYme6oscxcrysWV14qmMICDZCmyXgHx9cHAMgAD3nXddx6eSGR2EahLNugYr6boQXkvb6Wt7cZBjtebzVbAZDZD"


# Bucket config
class BucketConfig(object):

    def __init__(self, bucket_name, region_name):
        self.bucket_name = bucket_name
        self.region_name = region_name

    def name(self):
        return self.bucket_name

    def region(self):
        return self.region_name

    def __repr__(self):
        return "BucketConfig[Bucket = " + self.bucket_name + "," + "Region = " + self.region_name


# Shop images
shop_max_images_count = 10

# Product images
product_max_images_count = 10

bucket_config = BucketConfig(bucket_name="ecommerce-db", region_name='eu-central-1')
