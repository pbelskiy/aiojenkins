import pytest

from aiojenkins.exceptions import JenkinsError


def test_build_start(jenkins):
    name, number = jenkins.builds.parse_url(
        'http://localhost:8080/job/jobbb/1/console'
    )
    assert name == 'jobbb'
    assert number == 1

    name, number = jenkins.builds.parse_url(
        'http://localhost:8080/job/test_folder/job/test_job/567/console'
    )
    assert name == 'test_folder/test_job'
    assert number == 567

    with pytest.raises(JenkinsError):
        jenkins.builds.parse_url('xxx')
