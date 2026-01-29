# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Script to clean up GitHub Packages container images except given tags or number of days."""

import os
import re
from datetime import datetime, timedelta

from ghapi.all import GhApi
from ghapi.core import print_summary
from ghapi.page import paged

PACKAGE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

org_str = os.environ.get("PACKAGE_ORG")
pck_str = os.environ.get("PACKAGE_NAME")
last_days_str = os.environ.get("ALLOW_LAST_DAYS")
valid_tags_str = os.environ.get("VALID_TAGS_STR")

last_days = int(last_days_str) if last_days_str != "" else None
valid_tags = [x.strip() for x in valid_tags_str.split(",")]

api = GhApi(debug=print_summary, token=os.getenv("PACKAGE_DELETION_TOKEN"))

if last_days:
    delete_before_date = datetime.now() - timedelta(days=last_days)

paged_packages = paged(
    api.packages.get_all_package_versions_for_package_owned_by_org,
    org=org_str,
    package_name=pck_str,
    package_type="container",
    state="active",
    per_page=100,
)

# Loop over all pages
for page in paged_packages:
    for package in page:
        # If keeping last days is requested, then check
        if (
            last_days
            and datetime.strptime(package.created_at, PACKAGE_TIME_FORMAT).timestamp()
            > delete_before_date.timestamp()
        ):
            continue

        # Check if the given package has valid tags
        package_tags = package.metadata.container.tags
        delete = True
        match = ""
        for tag in package_tags:
            for pattern in valid_tags:
                if re.fullmatch(pattern, tag):
                    delete = False
                    match = f"(matched tag '{tag}' with pattern '{pattern}')"
                    break
            if not delete:
                break

        # In case it should, delete it
        if delete:
            print(f"Deleting package: {package}")
            api.packages.delete_package_version_for_org(
                org=org_str,
                package_name=pck_str,
                package_type="container",
                package_version_id=package["id"],
            )
        else:
            print(
                f"Keeping package {package['name']} with tags {package_tags} - {match}"
            )
