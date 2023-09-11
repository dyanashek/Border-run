def numbers_format(value):
    """Makes a good looking numbers format."""

    return '{:,}'.format(value).replace(',', ' ')


def escape_markdown(text):
    characters_to_escape = ['_', '*', '[', ']', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)

    return text


def validate_phone(phone):
    phone = phone.replace('(', '').replace(' ', '').replace(')', '').replace('-', '').replace('_', '').replace('+', '')

    try:
        if len(phone) == 10 and phone.startswith('0'):
            int(phone)
            return phone
        else:
            return False

    except:
        return False


def generate_google_maps_link(lat, lon):
    return f'https://www.google.com/maps/place/{lat},{lon}'







