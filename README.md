# Build Qwak Model Action

This GitHub Action triggers a machine learning model build in Qwak Cloud. It provides a seamless integration with Qwak's platform, allowing you to configure, build, and monitor your models directly from your GitHub repository.

## Requirements

- A [Qwak API key](https://app.qwak.ai/qwak-admin#personal-api-keys) must be set up as a repository secret named `QWAK_API_KEY`.

## Inputs

- `sdk-version`: The Qwak-SDK version required to trigger this build. Default: `latest`.
- `model-id`: **(Required)** Model ID.
- `model-path`: **(Required)** Path to the project's directory. By default, Qwak searches for the `main` directory in the specified path.
- `main-dir-name`: Model main directory name. Default: `main`.
- `param-list`: A list of key-value pairs representing build parameters, specified in the format NAME=VALUE, separated by a comma.
- `env-vars`: Environment variables for the build, specified in the format NAME=VALUE, separated by a comma.
- `tags`: One or multiple tags for the model build, separated by a comma.
- `cpu`: Number of CPUs to use on the remote build. Default (If GPU not configured): 2.
- `memory`: Memory to use on the remote build.
- `gpu-type`: Type of GPU to use on the remote build (NVIDIA_A10G, NVIDIA_K80, NVIDIA_A100, NVIDIA_V100, NVIDIA_T4).
- `gpu-amount`: Amount of GPU to use on the remote build. Default: None.
- `base-image`: Used for customizing the Docker container image built for training, building, and deploying. Docker images should be based on Qwak images.
- `iam-role-arn`: Custom IAM Role ARN Qwak should assume to access external resources in the build process.
- `gpu-compatible`: Whether to build an image that is compatible to be deployed on a GPU. Default: `false`.
- `logs-as-json`: Output logs as JSON for easier parsing. Default: `false`.
- `timeout-after`: How many minutes to wait for the build before timing out. Default: 30.


## Outputs

- `build-id`: The ID of the build.
- `build-status`: The status of the build once it finished execution or times out.
- `build-metrics`: **(if successful)** A list of key=value pairs representing build metrics.


## Example Usage

### Basic Example

```yaml
- name: Build Qwak Model
  uses: your-username/your-repo@v1
  with:
    model-id: 'your-model-id'
    model-path: 'path/to/your/model'
```

### Example with GPU configuration

```yaml
- name: Build Qwak Model with GPU
  uses: your-username/your-repo@v1
  with:
    model-id: 'your-model-id'
    model-path: 'path/to/your/model'
    gpu-type: 'NVIDIA_V100'
    gpu-amount: '2'
```

### Example with Custom Parameters and Environment Variables

```yaml
- name: Build Qwak Model with Custom Parameters
  uses: your-username/your-repo@v1
  with:
    model-id: 'your-model-id'
    model-path: 'path/to/your/model'
    param-list: 'iterations=1000,loss_function=MAE'
    env-vars: 'PATH=/custom/path,CONFIG=/custom/config'
```

### Example with Timeout Configuration

```yaml
- name: Build Qwak Model with Timeout
  uses: your-username/your-repo@v1
  with:
    model-id: 'your-model-id'
    model-path: 'path/to/your/model'
    timeout-after: '60'
```

### Example with a specific Qwak SDK version

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Build Qwak Model
      uses: qwak-ai/build-action@v1
      with:
        model-id: 'my-model-id'
        model-path: 'path/to/model'
        sdk-version: '0.5.18'
        # other inputs as needed
```

## Support

For support or any questions related to this action, please contact the Qwak team.