import os

ERROR_MESSAGE = """
At least one license is not accepted. The list of invalid \
licenses are: {invalid_licenses}"""


class LicenseError(Exception):
    pass


def check_licenses():
    print("Printing all env variables:")
    print(os.environ)
    print("Printing licenses:")
    print(os.environ.get("LICENSES"))
    dummy_list = ["random lib", "more libs"]
    raise (LicenseError(ERROR_MESSAGE.format(invalid_licenses=dummy_list)))


if __name__ == "__main__":
    check_licenses()
