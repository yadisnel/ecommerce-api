from pydantic import Field

from models.rwmodels import RwModel


class RequestEnableAccount(RwModel):
    account_id: str = Field(..., title="Account id.")


class RequestDisableAccount(RwModel):
    account_id: str = Field(..., title="Account id.")


class RequestRegisterAccountWithEmail(RwModel):
    email: str = Field(...,
                       title="Valid email address.",
                       regex='(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
    password: str = Field(...,
                          title="Password.",
                          min_length=8,
                          max_length=64)
    locale: str = Field(..., title="Locale.Only 'es_ES',  'en_US', 'sr_Latn' and 'fr_CA' are supported.")
    country_iso_code: str = Field(..., title="Country iso code. Only 'CU','US', 'UY', 'SR','ES', and 'CA' are supported.")


class RequestConfirmRegisterAccountWithEmail(RwModel):
    email: str = Field(...,
                        title="Valid email address.",
                        regex='(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
    security_code: str = Field(...,
                               title="Security code.",
                               min_length=64,
                               max_length=64)