class LicenseError(Exception):
    pass

def check_licenses():
    message = """
    At least one license is not accepted. The list of unaccepted \
    licenses are: ['test license', 'more licenses']"""
    raise(LicenseError(message))


if __name__ == '__main__':
    check_licenses()
