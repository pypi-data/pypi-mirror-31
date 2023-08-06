# pytest-forcefail

pytest-forcefail is a plugin providing

- the method `pytest_forcefail.forcefail`
- the exception class `pytest_forcefail.ForceFailed`

These two will make the test failing **regardless of pytest.mark.xfail**.

See test\_forcefail.py for example.
