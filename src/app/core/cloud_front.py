import datetime
import os

from botocore.signers import CloudFrontSigner
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from src.app.core.path import root_path


def rsa_signer(message):
    root_dir = root_path()
    cloud_front_pem_dir = os.path.join(root_dir, 'core', 'credentials', 'pk-APKAJFSR76AO5IEYH6TQ.pem')
    #### .pem is the private keyfile downloaded from CloudFront keypair
    with open(cloud_front_pem_dir, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())
        signer = private_key.signer(padding.PKCS1v15(), hashes.SHA1())
        signer.update(message)
        return signer.finalize()


def get_signed_url(s3_key):
    key_id = 'APKAJFSR76AO5IEYH6TQ'
    url = 'https://d3dgdgroldjn7d.cloudfront.net/' + s3_key
    current_time = datetime.datetime.utcnow()
    expire_date = current_time + datetime.timedelta(days=365000)
    cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)
    # Create a signed url that will be valid until the specfic expiry date
    # provided using a canned policy.
    signed_url = cloudfront_signer.generate_presigned_url(url, date_less_than=expire_date)
    return signed_url
