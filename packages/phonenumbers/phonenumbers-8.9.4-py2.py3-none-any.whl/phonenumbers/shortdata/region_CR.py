"""Auto-generated file, do not edit by hand. CR metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_CR = PhoneMetadata(id='CR', country_code=None, international_prefix=None,
    general_desc=PhoneNumberDesc(national_number_pattern='[1359]\\d{2,3}', possible_length=(3, 4)),
    emergency=PhoneNumberDesc(national_number_pattern='112|911', example_number='911', possible_length=(3,)),
    short_code=PhoneNumberDesc(national_number_pattern='1(?:0(?:00|15|2[2-4679])|1(?:1[0-35-9]|2|37|[46]6|7[57]|8[79]|9[0-379])|2(?:00|[12]2|34|55)|3(?:21|33)|4(?:0[06]|1[4-6])|5(?:15|5[15])|693|7(?:00|1[789]|2[02]|[67]7)|975)|3855|5(?:0(?:30|49)|510)|911', example_number='1022', possible_length=(3, 4)),
    sms_services=PhoneNumberDesc(national_number_pattern='3855|5(?:0(?:30|49)|510)', example_number='3855', possible_length=(4,)),
    short_data=True)
