.. _pyansys_dashboard_upload:

Uploading vulnerabilities to the PyAnsys Dashboard
==================================================

The PyAnsys Dashboard is a web application that allows PyAnsys repository
maintainers to upload and view the vulnerabilities in their repository. This
allows maintainers to track the vulnerabilities in their repository and
determine if they are being addressed.

It also provides a way for Ansys employees to view the vulnerabilities in the
repositories they are responsible for and determine if they need to take
action.

.. warning::

    This feature is only available to Ansys employees and PyAnsys repository
    maintainers. You can access the PyAnsys Dashboard at the following URL:
    https://github.com/ansys-internal/pyansys-dashboard


In order to upload vulnerabilities to the PyAnsys Dashboard, you will need to
configure your workflow as follows:

.. code:: yaml

    name: Upload vulnerabilities to the PyAnsys Dashboard
    on:
      pull_request:
      push:
        branches:
          - main
    jobs:
      vulnerabilities:
        runs-on: ubuntu-latest
        steps:
        - name: PyAnsys Vulnerability check
          if: github.ref != 'refs/heads/main'
          uses: ansys/actions/check-vulnerabilities@main
          with:
            python-version: ${{ env.MAIN_PYTHON_VERSION }}
            python-package-name: ${{ env.PACKAGE_NAME }}
            token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}
            dev-mode: true

        - name: PyAnsys Vulnerability check (on main)
          if: github.ref == 'refs/heads/main'
          uses: ansys/actions/check-vulnerabilities@main
          with:
            python-version: ${{ env.MAIN_PYTHON_VERSION }}
            python-package-name: ${{ env.PACKAGE_NAME }}
            token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}
            pyansys-dashboard-upload: true
            pyansys-dashboard-token: ${{ secrets.PYANSYS_DASHBOARD_TOKEN }}
            pyansys-dashboard-credentials: ${{ secrets.PYANSYS_DASHBOARD_DB_CREDENTIALS }}

The above workflow will run the vulnerability check on every push and pull
request to the repository. If the push is to the main branch, it will also
upload the vulnerabilities to the PyAnsys Dashboard.

For more information on how to configure the ``ansys/actions/check-vulnerabilities`` action, see the
corresponding section in this documentation at :ref:`pyansys_check_vulnerabilities`.
