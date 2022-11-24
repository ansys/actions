import argparse

ERROR_MESSAGE = """
At least one license is not accepted. The list of invalid \
licenses are: {invalid_licenses}"""


class LicenseError(Exception):
    pass


def check_licenses(args):
    print("Print argument received from yml file:")
    print(args.licenses)
    invalid_licenses = []

    if invalid_licenses:
        raise (LicenseError(ERROR_MESSAGE.format(invalid_licenses=invalid_licenses)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="check that all licenses used are valid"
    )
    parser.add_argument("--licenses", "-l")
    args = parser.parse_args()
    check_licenses(args)
