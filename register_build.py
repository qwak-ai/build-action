from qwak.qwak_client.builds.build import Build, BuildStatus
from qwak import QwakClient

import traceback
import subprocess
import re
import os
import time



SLEEP_BETWEEN_STATUS_QUERY = 10.0

def build_command():
    command = ["qwak", "models", "build"]

    # Model ID
    model_id = os.getenv('MODEL_ID')
    if model_id:
        command.extend(["--model-id", model_id])

    # Model Path
    model_path = os.getenv('MODEL_PATH')
    if model_path:
        command.append(model_path)

    # Main Directory Name
    main_dir_name = os.getenv('MAIN_DIR_NAME')
    if main_dir_name:
        command.extend(["--main-dir", main_dir_name])

    # Parameter List
    param_list = os.getenv('PARAM_LIST')
    if param_list:
        params = param_list.split(",")
        for param in params:
            command.extend(["-P", param])

    # Environment Variables
    env_vars = os.getenv('ENV_VARS')
    if env_vars:
        env_vars_list = env_vars.split(",")
        for env_var in env_vars_list:
            command.extend(["-E", env_var])

    # Tags
    tag_list = os.getenv('TAGS')
    if tag_list:
        tags = tag_list.split(",")
        for tag in tags:
            command.extend(["-T", tag])

    # Instance Type
    instance = os.getenv('INSTANCE')
    if instance:
        command.extend(["--instance", instance])

    # Base Image
    base_image = os.getenv('BASE_IMAGE')
    if base_image:
        command.extend(["--base-image", base_image])

    # IAM Role ARN
    iam_role_arn = os.getenv('IAM_ROLE_ARN')
    if iam_role_arn:
        command.extend(["--iam-role-arn", iam_role_arn])

    # GPU Compatible
    gpu_compatible = os.getenv('GPU_COMPATIBLE')
    if gpu_compatible and gpu_compatible.lower() == 'true':
        command.append("--gpu-compatible")

    # Environment
    environment = os.getenv('ENVIRONMENT')
    if environment:
        command.extend(["--environment", environment])

    # Logs as JSON - default TRUE
    logs_as_json = os.getenv('LOGS_AS_JSON', 'true')
    if logs_as_json.lower() != 'false':
        command.append("--json-logs")


    return " ".join(command)


def wait_for_build(build_id: str, timeout: int) -> Build:

    # Initialize the Qwak client
    qwak_client = QwakClient()

    # Record the start time to track how long we've been waiting
    start_time = time.time()

    current_status = None

    try:
        # Keep checking the build status until a timeout is reached
        while time.time() - start_time < 60 * timeout:
            # Wait a specified amount of time between each status check
            time.sleep(SLEEP_BETWEEN_STATUS_QUERY)

            # Get the current build object from the Qwak client
            build_object = qwak_client.get_build(build_id)

            verbal_build_status = build_object.build_status.name


            # Print the current build status if changed
            if verbal_build_status is not current_status:
                print(f"Current build {build_id} status is: {verbal_build_status}\n")
                current_status = verbal_build_status

            # Check if the build is successful
            if build_object.build_status is BuildStatus.SUCCESSFUL:
                elapsed_time = time.time() - start_time
                minutes, seconds = divmod(elapsed_time, 60)
                print(f"Build finished after {int(minutes)} minutes and {seconds:.2f} seconds with status {verbal_build_status}\n")
                return build_object
            
            # Check if the build has failed
            elif build_object.build_status not in [BuildStatus.IN_PROGRESS, BuildStatus.REMOTE_BUILD_INITIALIZING]:
                print(f"Build failed with status {verbal_build_status} -> Please check the logs in the Qwak dashboard for more information.")
                return build_object

        # If the loop exits without returning, the build has timed out
        raise TimeoutError(f"Build {build_id} timed out after {timeout} minutes.")
    
    except Exception as e:
        # Catch any other exceptions, print an error message, and re-raise the exception
        print(f"An error occurred while waiting for build {build_id}:\n {str(e)}")
        raise e
    


if __name__ == '__main__':

    timeout_for_failing = int(os.getenv('INPUT_TIMEOUT_AFTER', 30)) # Default 30 minutes
 
    qwak_build_model_command = build_command()
    print("Printing the qwak cli command for debug purposes:\n", qwak_build_model_command)

    build_id = None # Define build_id variable outside the try block

    try:
        
        # Create a Popen object to run the command
        process = subprocess.Popen(qwak_build_model_command, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                shell=True, 
                                text=True)


        # Wait for the process to finish and get the return code
        return_code = process.wait()
        stdout, stderr = process.communicate()

        # Print the standard output
        print(f"Command Output:\n\n{stdout}\n")

        # Check if the command was successful
        if return_code != 0:
            print(f"An error occurred while running the `qwak models build` command.\n {stderr}")
            exit(1)

        # Extract the build ID using a regular expression - careful with the escape codes!!!
        build_id_pattern = re.compile(r'Build ID \x1b\[4m([a-fA-F0-9\-]+)\x1b\[0m')
        match = build_id_pattern.search(stdout)
        
        if match:
            build_id = match.group(1).strip()
            print(f"Extracted Build ID: {build_id}\n")


            # Call the wait_for_build method with the specified build ID
            build_object = wait_for_build(build_id, timeout_for_failing)

            # Write the outputs to the GitHub environment file
            with open(os.getenv('GITHUB_ENV'), 'a') as file:
                file.write(f"build-id={build_object.build_id}\n")
                file.write(f"build-status={build_object.build_status.name}\n")

                if build_object.build_status is BuildStatus.SUCCESSFUL:
                    file.write(f"build-metrics={build_object.metrics}\n")
                else:
                    print(f"Build failed with status {build_object.build_status.name}. Failing the GitHub Action step.")
                    exit(1)

        else:
            print("Build ID not found in the command output. Please contact the Qwak team for assistance.")
            exit(1)

    except TimeoutError as timeout_error:
          # Handle the timeout exception specifically
        if build_id:
            print(f"Waiting for build {build_id} timed out: {str(timeout_error)}")

            # Write "TIMEOUT" to the build_status in the GitHub environment file
            with open(os.getenv('GITHUB_ENV'), 'a') as file:
                file.write(f"build-id={build_id}\n")
                file.write("build-status=TIMEOUT\n")
        else:
            print("Build ID not found. Cannot handle timeout exception without Build ID.")

        exit(1)    

    except Exception as general_error:
        # Handle any other exceptions that might occur
        print(f"An unexpected error occurred while waiting for build: {str(general_error)}")
        #traceback.print_exc() # This will print the stack trace
        exit(1)


