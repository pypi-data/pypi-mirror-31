"""Auto-generated file, do not edit by hand. CW metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_CW = PhoneMetadata(id='CW', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[19]\\d{2}', possible_length=(3,)),
    emergency=PhoneNumberDesc(national_number_pattern='112|911', example_number='112', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:12|76)|911', example_number='112', possible_length=(3,)),
    carrier_specific=PhoneNumberDesc(national_number_pattern='176', example_number='176', possible_length=(3,)),
    sms_services=PhoneNumberDesc(national_number_pattern='176', example_number='176', possible_length=(3,)),
    short_data=True)
