"""Auto-generated file, do not edit by hand. CC metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_CC = PhoneMetadata(id='CC', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[01]\\d{2}', possible_length=(3,)),
    emergency=PhoneNumberDesc(national_number_pattern='000|112', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='000|112', example_number='112', possible_length=(3,)),
    short_data=True)
