"""Auto-generated file, do not edit by hand. NZ metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_NZ = PhoneMetadata(id='NZ', country_code=64, international_prefix='0(?:0|161)',
    general_desc=PhoneNumberDesc(national_number_pattern='6[235-9]\\d{6}|[2-57-9]\\d{7,9}', possible_length=(8, 9, 10), possible_length_local_only=(7,)),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:3[2-79]|[49][2-9]|6[235-9]|7[2-57-9])\\d{6}|24099\\d{3}', example_number='32345678', possible_length=(8,), possible_length_local_only=(7,)),
    mobile=PhoneNumberDesc(national_number_pattern='2(?:[028]\\d{7,8}|1\\d{6,8}|[79]\\d{7})', example_number='211234567', possible_length=(8, 9, 10)),
    toll_free=PhoneNumberDesc(national_number_pattern='508\\d{6,7}|80\\d{6,8}', example_number='800123456', possible_length=(8, 9, 10)),
    premium_rate=PhoneNumberDesc(national_number_pattern='90\\d{6,7}', example_number='900123456', possible_length=(8, 9)),
    personal_number=PhoneNumberDesc(national_number_pattern='70\\d{7}', example_number='701234567', possible_length=(9,)),
    pager=PhoneNumberDesc(national_number_pattern='[28]6\\d{6,7}', example_number='26123456', possible_length=(8, 9)),
    preferred_international_prefix='00',
    national_prefix='0',
    national_prefix_for_parsing='0',
    number_format=[NumberFormat(pattern='(\\d)(\\d{3})(\\d{4})', format='\\1-\\2 \\3', leading_digits_pattern=['240|[346]|7[2-57-9]|9[1-9]'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='(\\d{2})(\\d{3})(\\d{3})', format='\\1 \\2 \\3', leading_digits_pattern=['21'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='(\\d{2})(\\d{3})(\\d{3,5})', format='\\1 \\2 \\3', leading_digits_pattern=['2(?:1[1-9]|[69]|7[0-35-9])|70|86'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='(2\\d)(\\d{3,4})(\\d{4})', format='\\1 \\2 \\3', leading_digits_pattern=['2[028]'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='(\\d{3})(\\d{2})(\\d{3})', format='\\1 \\2 \\3', leading_digits_pattern=['90'], national_prefix_formatting_rule='0\\1'),
        NumberFormat(pattern='(\\d{3})(\\d{3})(\\d{3,4})', format='\\1 \\2 \\3', leading_digits_pattern=['2(?:10|74)|5|[89]0'], national_prefix_formatting_rule='0\\1')],
    mobile_number_portable_region=True)
