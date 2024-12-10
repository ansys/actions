import json
import re
from pathlib import Path

import toml
from parse_pr_title import get_towncrier_config_value

# from jinja2 import Environment, FileSystemLoader


def existing_changelog_to_json(changelog_json, content):
    print("Read existing changelog.rst or CHANGELOG.md file and convert to JSON format")


def fragment_files_to_json(fragment_file_dir, fragment_file_json, tag):
    # Get the minor tag version based on the tag. For example,
    # tag 0.6.0 would return minor_tag 0.6
    minor_tag = ".".join(tag.split(".")[:2])

    # Get the types listed in the [tool.towncrier.type] section in pyproject.toml
    # Formatted as {"directory": "name"}
    type_dict = get_tool_towncrier_types()

    # If "whatsnew" is missing from the [tool.towncrier.type] section in pyproject.toml,
    # add it to the type_dict dictionary
    if not type_dict.get("whatsnew", None):
        type_dict["whatsnew"] = "What's New"

    # Add the minor tag to the fragment_file_json dictionary if it does not exist
    # For example, "0.6": {}
    if not fragment_file_json.get("type", None):
        fragment_file_json[minor_tag] = {}

    # Add the "What's New" key to the fragment_file_json dictionary if it does not exist
    # For example,
    # "0.6": {
    #     "What's New": {
    #        "0.6.0": {}
    #     }
    # }
    if not fragment_file_json[minor_tag].get(type_dict["whatsnew"], None):
        # fragment_file_json[minor_tag][type_dict["whatsnew"]] = {}
        fragment_file_json[minor_tag][type_dict["whatsnew"]] = {tag: {}}

    # Add the tag key under the minor_tag to the fragment_file_json dictionary if it does not exist
    # For example,
    # "0.6": {
    #     "What's New": {
    #        "0.6.0": {}
    #     }
    #     "0.6.0": {
    #         "Changelog": {}
    #     }
    # }
    if not fragment_file_json[minor_tag].get(tag, None):
        fragment_file_json[minor_tag][tag] = {"Changelog": {}}

    # Get the markdown fragment files in the fragment_file_dir directory
    fragment_files = Path(fragment_file_dir).glob("**/*.md")
    for path in fragment_files:
        # Get the issue number and type from the name of the fragment file. For example,
        # 945.added.md would return issue_number 945 and issue_type added
        issue_number, issue_type = path.stem.split(".")

        # Open the file and read its content
        with open(path) as file:
            content = file.read()

            # If the issue type does not exist in the "Changelog" section, add it to the dictionary
            # with its corresponding title from type_dict and an empty dictionary for content
            # "0.6": {
            #     "0.6.0": {
            #         "Changelog": {
            #             "added": {
            #                 "content": {},
            #                 "title": "Features"
            #             },
            #             ...
            #         }
            #     },
            #     "What's New": {
            #        "0.6.0": {}
            #     },
            # }
            if not fragment_file_json[minor_tag][tag]["Changelog"].get(
                issue_type, None
            ):
                fragment_file_json[minor_tag][tag]["Changelog"][issue_type] = {
                    "content": {},
                    "title": type_dict[issue_type],
                }

            # Add the content of the fragment file to the fragment_file_json dictionary
            # For example,
            # "0.6": {
            #     "0.6.0": {
            #         "Changelog": {
            #             "added": {
            #                 "content": {
            #                     "945": "add what's new section",
            #                 },
            #                 "title": "Features"
            #             },
            #             ...
            #         }
            #     },
            #     ...,
            # }
            fragment_file_json[minor_tag][tag]["Changelog"][issue_type]["content"][
                issue_number
            ] = content

    # Get the rst fragment files in the fragment_file_dir directory
    whatsnew_files = (Path(fragment_file_dir) / "whatsnew").glob("**/*.rst")
    for path in whatsnew_files:
        with open(path) as file:
            # Get all lines of the whatsnew file
            lines = file.readlines()
            # Get the first line of the file as the title
            title = lines[0].strip()
            # Insert a line to indicate the version the feature is available in
            lines.insert(2, f"Available in v{tag}\n\n")
            # Skip the title and underline of the title
            content = "".join(lines[2:])

            # Add the whatsnew content to the fragment_file_json dictionary
            # For example,
            # "0.6": {
            #     ...,
            #     "What's New": {
            #         "0.6.0": {
            #             "Launch GUI": "Available in v0.6.0\n\nOpen the current project with ...",
            #             ...
            #         }
            #     }
            # }
            if lines:
                fragment_file_json[minor_tag][type_dict["whatsnew"]][tag][
                    title
                ] = content

    print(json.dumps(fragment_file_json, indent=4, sort_keys=True))

    # remove_fragment_files(fragment_file_dir, True)

    return fragment_file_json


def get_tool_towncrier_types():
    type_dict = {}
    # Load pyproject.toml file (pass in pyproject path as an argument - to do)
    with open("pyproject.toml", "a+") as file:
        config = toml.load(file)
        tool = config.get("tool", None)
        if tool:
            towncrier = tool.get("towncrier", None)
            if towncrier:
                types = towncrier.get("type", None)
                for type in types:
                    if type["name"] == "Whatsnew":
                        type["name"] = "What's New"
                    type_dict[type["directory"]] = type["name"]

    return type_dict


def remove_fragment_files(fragment_file_dir, delete_files: bool = False):
    if delete_files:
        file_types = ["*.md", "*.rst"]

        for file_type in file_types:
            fragment_files = Path(fragment_file_dir).rglob(file_type)
            for file in fragment_files:
                print(f"Removing {file}")
                # os.remove(file)


def update_changelog_file(changelog_file, updated_json):
    """Use jinja template and fragment_file_json to update the changelog file."""
    with open(changelog_file, "r") as file:
        content = file.read()

    towncrier_start_string = get_towncrier_config_value("start_string")
    beginning_of_file_regex = rf"(^)+([\W\w]*?)({towncrier_start_string})"
    print(re.search(beginning_of_file_regex, content).group())

    # # Load the templates from the hook path
    # loader = FileSystemLoader(searchpath=pathlib.PurePath.joinpath(HOOK_PATH, "templates"))
    # env = Environment(loader=loader)  # nosec
    # # Get the template for the specified file
    # template = env.get_template(file)
    # # Generate the file content from the template
    # file_content = template.render(
    #     doc_repo_name=doc_repo_name,  # pymechanical
    #     project_name=project_name,  # ansys-mechanical-core
    #     year_span=year_str,  # 2022 - 2024
    #     repository_url=repo_url,  # https://github.com/ansys/pymechanical
    #     product=product,  # mechanical
    #     config_file=config_file,  # pyproject
    # )

    # return file_content


def main():
    fragment_file_dir = get_towncrier_config_value(
        "directory"
    )  # , pyproject_path: str = "pyproject.toml")
    changelog_file = get_towncrier_config_value(
        "filename"
    )  # , pyproject_path: str = "pyproject.toml")
    changelog_json = Path(fragment_file_dir) / "changelog.json"
    tag = "0.6.0"

    if not changelog_json.exists():
        with open(changelog_json, "w") as file:
            file.write("{}")

    with open(changelog_json, "rb") as file:
        fragment_file_json = json.load(file)

    # updated_json = existing_changelog_to_json(fragment_file_json, changelog)
    updated_json = fragment_files_to_json(fragment_file_dir, fragment_file_json, tag)
    # print(updated_json)
    update_changelog_file(changelog_file, updated_json)

    # print(json.dumps(updated_json, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()

# sample_json = {
#     "0.6": {
#         "0.6.0": {
#             "Changelog": {
#                 "added": {
#                     "content": {
#                         "945": "add what's new section",
#                         "979": "Version input type check"
#                     },
#                     "title": "Features"
#                 },
#                 "fixed": {
#                     "content": {
#                         "974": "Update embedding script tests"
#                     },
#                     "title": "Bug fixes"
#                 },
#                 "maintenance": {
#                     "content": {
#                         "963": "update CHANGELOG for v0.11.9",
#                         "965": "Modify how job success is verified for CI/CD",
#                         "966": "Bump mikepenz/action-junit-report from 4 to 5",
#                         "967": "Bump grpcio from 1.67.0 to 1.67.1 in the core group",
#                         "968": "Bump the doc group with 2 updates",
#                         "969": "Bump pytest-cov from 5.0.0 to 6.0.0",
#                         "971": "Update docs build action container",
#                         "977": "pre-commit automatic update"
#                     },
#                     "title": "Maintenance"
#                 }
#             }
#         },
#         "What's New": {
#             "0.6.0": {
#                 "Launch GUI": "Available in v0.6.0\n\nOpen the current project with Mechanical GUI.\n\n.. code:: python\n\n    from ansys.mechanical.core import App\n\n    app = App()\n    app.save()\n    app.launch_gui()\n\nAbove code opens up the temporarily saved ``.mechdb`` or ``.mechdat`` files.\nThe files are deleted when GUI is closed . For more info check\n`launch_gui() <../api/ansys/mechanical/core/embedding/launch_gui/index.html>`_ function\n\nOpens up the specified project file.\n\n.. code:: python\n\n  launch_gui(\"path/to/project.mechdb\")",
#                 "Prints mechanical project tree": "Available in v0.6.0\n\nThis feature let you see the hierarchy of the mechanical project.\nIt also shows whether an object is suppressed or not.\n\n.. code:: python\n\n  import ansys.mechanical.core as mech\n\n  app = mech.App()\n  app.update_globals(globals())\n  app.print_tree()"
#             }
#         }
#     }
# }
