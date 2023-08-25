import unittest
from unittest.mock import patch, Mock
import os
from register_build import build_command, wait_for_build
from qwak.qwak_client.builds.build import Build, BuildStatus

class TestBuildCommand(unittest.TestCase):

    @patch.dict(os.environ, {
        'INPUT_MODEL-ID': '123',
        'INPUT_MODEL-PATH': '/path/to/model',
        'INPUT_CPU': '2',
        'INPUT_MEMORY': '4G',
        'INPUT_GPU-COMPATIBLE': 'true',
        'INPUT_LOGS-AS-JSON': 'true'
    })
    def test_build_command(self):
        command = build_command()
        expected_command = "qwak models build --model-id 123 /path/to/model --cpus 2 --memory 4G --gpu-compatible --json-logs"
        self.assertEqual(command, expected_command)

class TestWaitForBuild(unittest.TestCase):

    @patch('register_build.QwakClient')
    def test_wait_for_build_successful(self, MockQwakClient):
        build_id = 'test-build-id'
        timeout = 5

        # Mocking the Build object with a SUCCESSFUL status
        build_object = Build(build_id=build_id, build_status=BuildStatus.SUCCESSFUL)
        mock_qwak_client = MockQwakClient()
        mock_qwak_client.get_build.return_value = build_object

        result = wait_for_build(build_id, timeout)
        self.assertEqual(result.build_status, BuildStatus.SUCCESSFUL)

    @patch('register_build.QwakClient')
    def test_wait_for_build_timeout(self, MockQwakClient):
        build_id = 'test-build-id'
        timeout = 0 # Setting timeout to 0 to trigger a TimeoutError

        with self.assertRaises(TimeoutError):
            wait_for_build(build_id, timeout)

# Run the tests
if __name__ == '__main__':
    unittest.main()
