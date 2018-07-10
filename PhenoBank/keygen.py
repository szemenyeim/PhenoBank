from django.utils.crypto import get_random_string


def generate_secret_key(filename):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = get_random_string(50, chars)
    with open(filename, "w+") as fp:
        fp.write("SECRET_KEY = \"%s\"" % SECRET_KEY)