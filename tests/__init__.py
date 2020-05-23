import os
import platform

from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from aiojenkins import Jenkins


def get_host():
    return os.environ.get('host', 'http://localhost:8080')


def get_login():
    return os.environ.get('login', 'admin')


def get_password():
    return os.environ.get('password', 'admin')


def is_locally():
    """
    For skipping some long tests locally, but not on completely CI
    """
    return (platform.system() == 'Darwin')


# TODO: move it as builds submodule function?
def generate_job_config(parameters: list = None) -> str:
    root = Element('project')

    SubElement(root, 'actions')
    SubElement(root, 'description')
    SubElement(root, 'keepDependencies').text = 'false'

    # add parameters here
    props = SubElement(root, 'properties')

    if parameters:
        props = SubElement(props, 'hudson.model.ParametersDefinitionProperty')
        props = SubElement(props, 'parameterDefinitions')

        for name in parameters:
            new_p = SubElement(props, 'hudson.model.StringParameterDefinition')

            SubElement(new_p, 'name').text = name
            SubElement(new_p, 'description').text = ''
            SubElement(new_p, 'defaultValue').text = ''

    SubElement(root, 'scm', attrib={'class': 'hudson.scm.NullSCM'})
    SubElement(root, 'canRoam').text = 'true'
    SubElement(root, 'disabled').text = 'false'
    SubElement(root, 'blockBuildWhenDownstreamBuilding').text = 'false'
    SubElement(root, 'blockBuildWhenUpstreamBuilding').text = 'false'
    SubElement(root, 'triggers')
    SubElement(root, 'concurrentBuild').text = 'false'

    # add commands here
    builders = SubElement(root, 'builders')
    shell = SubElement(builders, 'hudson.tasks.Shell')
    SubElement(shell, 'command')
    SubElement(root, 'publishers')
    SubElement(root, 'buildWrappers')

    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')


jenkins = Jenkins(get_host(), get_login(), get_password())
