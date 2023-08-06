# envaws

Run application with environment loaded from AWS SSM.

# usage

```
usage: envaws.py [-h] [-p PROFILE] [-r REGION] -k KEY_PREFIX command ...

Run application with environment loaded from AWS SSM.

positional arguments:
  command               Child command to run.
  arg                   Child command arguments.

optional arguments:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        Override AWS config profile (omit to auto-detect.)
  -r REGION, --region REGION
                        Override region (omit to auto-detect)
  -k KEY_PREFIX, --key-prefix KEY_PREFIX
                        SSM key prefix
```

