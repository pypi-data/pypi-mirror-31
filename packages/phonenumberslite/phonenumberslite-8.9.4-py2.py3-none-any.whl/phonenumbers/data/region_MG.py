"""Auto-generated file, do not edit by hand. MG metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_MG = PhoneMetadata(id='MG', country_code=261, international_prefix='00',
    general_desc=PhoneNumberDesc(national_number_pattern='[23]\\d{8}', possible_length=(9,), possible_length_local_only=(7,)),
    fixed_line=PhoneNumberDesc(national_number_pattern='20(?:2\\d{2}|4[47]\\d|5[3467]\\d|6[279]\\d|7(?:2[29]|[35]\\d)|8[268]\\d|9[245]\\d)\\d{4}', example_number='202123456', possible_length=(9,), possible_length_local_only=(7,)),
    mobile=PhoneNumberDesc(national_number_pattern='3[2-49]\\d{7}', example_number='321234567', possible_length=(9,)),
    voip=PhoneNumberDesc(national_number_pattern='22\\d{7}', example_number='221234567', possible_length=(9,)),
    national_prefix='0',
    national_prefix_for_parsing='0',
    number_format=[NumberFormat(pattern='([23]\\d)(\\d{2})(\\d{3})(\\d{2})', format='\\1 \\2 \\3 \\4', leading_digits_pattern=['[23]'], national_prefix_formatting_rule='0\\1')])
