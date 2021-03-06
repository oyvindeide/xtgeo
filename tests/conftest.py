"""Setup common stuff for pytests."""
import os
import platform
import pytest

ALLPLATF = set("darwin linux windows".split())
SKIPPED = set("skipdarwin skiplinux skipwindows".split())


def pytest_runtest_setup(item):
    """Called for each test."""

    markers = [value.name for value in item.iter_markers()]

    # pytest.mark.xtgshow (showing plots):
    if "xtgshow" in markers:
        if any(word in os.environ for word in ["XTGSHOW", "XTG_SHOW"]):
            pytest.skip("Skip test if outside ROXENV (env variable ROXENV is present)")

    # pytest.mark.bigtest
    if "bigtest" in markers:
        if "XTG_BIGTEST" not in os.environ:
            pytest.skip("Skip big test (no env variable XTG_BIGTEST)")

    # pytest.mark.skipifroxar:
    if "skipifroxar" in markers:
        if "ROXENV" in os.environ:
            pytest.skip("Skip test in ROXENV (env variable ROXENV is present)")

    # pytest.mark.skipunlessroxar:
    if "skipunlessroxar" in markers:
        if "ROXENV" not in os.environ:
            pytest.skip("Skip test if outside ROXENV (env variable ROXENV is present)")

    # pytest.mark.linux ...
    supported = ALLPLATF.intersection(mark.name for mark in item.iter_markers())
    plat = platform.system().lower()
    if supported and plat not in supported:
        pytest.skip("cannot run on platform {}".format(plat))

    # pytest.mark.skiplinux ...
    skipped = SKIPPED.intersection(mark.name for mark in item.iter_markers())
    plat = "skip" + platform.system().lower()
    if skipped and plat in skipped:
        pytest.skip("cannot run on platform {}".format(plat))


def assert_equal(this, that, txt=""):
    """Assert equal wrapper function."""
    assert this == that, txt


def assert_almostequal(this, that, tol, txt=""):
    """Assert almost equal wrapper function."""
    assert this == pytest.approx(that, abs=tol), txt


@pytest.fixture(name="xtgshow")
def fixture_xtgshow():
    """For eventual plotting, to be uses in an if sence inside a test."""
    if any(word in os.environ for word in ["XTGSHOW", "XTG_SHOW"]):
        return True
    return False


@pytest.fixture(name="demo")
def fixture_demo():
    """Fixture demo for later usage.

    In the test script run like:

    def test_whatever(demo):
        demo
    """
    print("THIS IS A DEMO")


def pytest_addoption(parser):
    parser.addoption(
        "--testdatapath",
        help="path to xtgeo-testdata, defaults to ../xtgeo-testdata"
        "and is overriden by the XTG_TESTPATH environment variable."
        "Experimental feature, not all tests obey this option.",
        action="store",
        default="../xtgeo-testdata",
    )


@pytest.fixture()
def testpath(request):
    testdatapath = request.config.getoption("--testdatapath")
    environ_path = os.environ.get("XTG_TESTPATH", None)
    if environ_path:
        testdatapath = environ_path

    return testdatapath
