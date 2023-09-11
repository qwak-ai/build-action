# Qwak Model `BUILD` Action (v1)

This GitHub Action triggers a machine learning model build in Qwak Cloud. It provides a seamless integration with Qwak's platform, allowing you to configure, build, and monitor your models directly from your GitHub repository.

## Action flow:
1. Trigger build using the `qwak models build` CLI command
2. Extracts the Build ID from the command output
3. Pulls the Build status every 10 seconds from the Qwak Cloud while still IN_PROGRESS or INITIALIZING
4. Once finished returns Build ID, STATUS and METRICS as Action Outputs

## Inputs

- `qwak-api-key`: A [Qwak API key](https://app.qwak.ai/qwak-admin#personal-api-keys). Recommended to be set up as a repository secret.
- `sdk-version`: The Qwak-SDK version required to trigger this build. Default: `latest`.
- `model-id`: **(Required)** Model ID.
- `model-path`: Path to the project's directory inside the Github Actions Runner. Default `'.'`.
- `main-dir-name`: Model main directory name. Default: `main`.
- `param-list`: A list of key-value pairs representing build parameters, specified in the format NAME=VALUE, separated by a comma.
- `env-vars`: Environment variables for the build, specified in the format NAME=VALUE, separated by a comma.
- `tags`: One or multiple tags for the model build, separated by a comma.
- `instance`: [Instance sizes](https://docs-saas.qwak.com/docs/instance-sizes) allow simple selection of GPU/CPU compute and memory resources when building and deploying models. Default: `small`.
- `base-image`: Used for customizing the Docker container image built for training, building, and deploying. Docker images should be based on Qwak images.
- `iam-role-arn`: Custom IAM Role ARN Qwak should assume to access external resources in the build process.
- `gpu-compatible`: Whether to build an image that is compatible to be deployed on a GPU. Default: `false`.
- `environment`: The Qwak environment to use. For example, `dev`, `staging`, or `production`.
- `logs-as-json`: Output logs as JSON for easier parsing. Default: `false`.
- `timeout-after`: How many minutes to wait for the build before timing out. Default: 30.
- `from-file`: Build model with configuration as code from the specified file. Github Action arguments will overwrite any file configs.


## Outputs

- `build-id`: The ID of the build.
- `build-status`: The status of the build once it finished execution or times out.
- `build-metrics`: **(if successful)** A list of key=value pairs representing build metrics.

Output Example 
```bash
build-id=bc3ceeca-e4ed-48b9-8ff1-80427923f1cf
build-status=SUCCESSFUL
build-metrics={'val_accuracy': 0.6753646731376648}
```


## Example Usage

Let's assume the following project structure:

```bash
.
|
├── main                   # Main directory containing core code
│   ├── __init__.py        # An empty file that indicates this directory is a Python package
│   ├── model.py           # Defines the QwakModel code
│   └── conda.yaml         # Conda environment configurationdata
|
├── tests                  # Test directory
└──
```

### Basic Example

```yaml
- name: Build Qwak Model
  uses: qwak-ai/build-action@v1
  with:
    qwak-api-key: <your qwak key>
    model-id: 'your-model-id'
```

### Example with GPU configuration

```yaml
- name: Build Qwak Model with GPU
  uses: qwak-ai/build-action@v1
  with:
    qwak-api-key: <your qwak key>
    model-id: 'your-model-id'
    instance: 'gpu.t4.xl'
```

### Example with Hyperparameters

```yaml
- name: Build Qwak Model with Custom Parameters
  uses: qwak-ai/build-action@v1
  with:
    qwak-api-key: <your qwak key>
    model-id: 'your-model-id'
    param-list: 'iterations=1000,loss_function=MAE'
```

### Example with Timeout Configuration

```yaml
- name: Build Qwak Model with Timeout
  uses: qwak-ai/build-action@v1   
  with:
    qwak-api-key: <your qwak key>
    model-id: 'your-model-id'
    timeout-after: 60
```

### Trigger a build when a pull request is opened or edited

```yaml

name: Build and Test ML Model on Pull Request

on:
  pull_request:
    branches:
      - main  # or whichever branches you want to run this on

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Build Qwak Model
      uses: qwak-ai/build-action@v1
      with:
        qwak-api-key: <your qwak key>
        model-id: 'my-model-id'
        model-path: 'feature-store-example-project'
        sdk-version: '0.5.18'
        instance: 'medium'
        tags: <ml-experiment-branch>
        iam-role-arn: 'arn:aws:iam::<account-id>:role/<role-name>'
        # other inputs as needed
```

## Support

For support or any questions related to this action, please contact the Qwak team.