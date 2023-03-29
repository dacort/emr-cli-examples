# EMR CLI Examples

This is a set of examples that show how EMR CLI can be used to easily deploy a variety of different jobs to EMR Serverless and EMR on EC2.

## Pre-requisities

- An EMR Serverless application, job role and S3 bucket
- An EMR on EC2 cluster
- The `emr` CLI installed via `pip install emr-cli`

If you don't have EMR Serverless setup, you can use the `emr bootstrap` command to provision an S3 bucket, job role, and application.

For EMR on EC2, we'll just create a Spark cluster in the console.

We'll set a variety of environment variables to be used throughout the examples.

```bash
APPLIATION_ID=<EMR_SERVERLESS_APPLICATION_ID>
JOB_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/<JOB_ROLE>
S3_BUCKET=<S3_BUCKET_NAME>
CLUSTER_ID=<EMR_EC2_CLUSTER_ID>
```

## Single file test

Single file test is a single `.py` file that prints out hello.

```
single-file-test
└── entrypoint.py

1 directory, 1 file
```

This command, "builds" the project, which in this case does nothing. It then copies it up to the `s3-code-uri` specified and starts a new EMR Serverless job.

```bash
emr run \
    --entry-point entrypoint.py \
    --application-id ${APPLICATION_ID} \
    --job-role ${JOB_ROLE_ARN} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD) \
    --build \
    --wait
```

We can run the same code on EMR on EC2. No need to `--build` again as we're already deployed.

```bash
emr run \
    --entry-point entrypoint.py \
    --cluster-id ${CLUSTER_ID} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD) \
    --wait
```

## Multi file test

The next project uses a standard Python project structure. It's a slightly more complex Spark job that reads a CSV file from the [NOAA GSOD open dataset](https://registry.opendata.aws/noaa-gsod/).

> **Note** Because we access data in S3, your EMR Serverless application either needs to be in the `us-east-1` region or created with a VPC.

```
multi-file-test
├── entrypoint.py
└── jobs
    ├── __init__.py
    └── job1.py

2 directories, 3 files
```

We'll run the same exact command, just in the `multi-file-test` directory.


```bash
emr run \
    --entry-point entrypoint.py \
    --application-id ${APPLICATION_ID} \
    --job-role ${JOB_ROLE_ARN} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD) \
    --build \
    --wait
```

This time, we notice that a `dist/` directory is created with our job modules.

```
dist
└── pyfiles.zip

1 directory, 1 file
```

When `emr run` is called, it automatically detects this is a multi-module Python project, zips up the `jobs/` directory, and uploads it to S3.

Then when the EMR Serverless job or EMR on EC2 step is created, it sends the proper `spark-submit` settings.

```bash
emr run \
    --entry-point entrypoint.py \
    --cluster-id ${CLUSTER_ID} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD) \
    --wait
```

## Python build system

Modern Python projects can contain a `pyproject.toml` file. The EMR CLI supports building these projects and can even initialize a default project for you with the `init` command.

```bash
emr init pyproject-test
```

```
❯ emr init pyproject-test
[emr-cli]: Initializing project in pyproject-test
[emr-cli]: Project initialized.
```

```
pyproject-test
├── Dockerfile
├── entrypoint.py
├── jobs
│   └── extreme_weather.py
└── pyproject.toml

2 directories, 4 files
```

Notice that there's a `Dockerfile` in this directory - Docker is used by the `emr package` command to build a virtualenv compatible with Amazon Linux. This is required for certain Python depenencies that have operating system-specific functionality.

We can indepedently build the project using the `emr package` command.

```bash
emr package --entry-point entrypoint.py 
```

Again, we see our job dependencies in the `dist/` directory.

```
dist/
└── pyspark_deps.tar.gz

1 directory, 1 file
```

Notice that instead of a simple `pyfiles.zip` file, we have `pyspark_deps.tar.gz`. This is a bundled virtual environment that includes 

And we can also deploy it to S3 using the `emr deploy` command.

```bash
emr deploy \
    --entry-point entrypoint.py \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD)
```

A simple `emr run` command is all we need to run the deployed code in EMR Serverless or EMR on EC2. 

```bash
emr run \
    --entry-point entrypoint.py \
    --application-id ${APPLICATION_ID} \
    --job-role ${JOB_ROLE_ARN} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD)
```

I left off the `--wait` this time because this example job takes longer to run, so the `emr run` command exits immediately after submitting the job.

Same goes for EMR on EC2.

```bash
emr run \
    --entry-point entrypoint.py \
    --cluster-id ${CLUSTER_ID} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD)
```

## Python Poetry support

Finally, Poetry is a popular Python dependency management and packaging tool. The EMR CLI supports creating an example PySpark project with Poetry as well as bundling and deploying Poetry projects.

You can use the `emr init --project-type poetry` command to create a sample Poetry project in your directory of choice, or you can also use the `emr init --dockerfile` command to create a Dockerfile in your local directory that supports packaging Poetry projects. 

```bash
emr init --project-type poetry poetry-test/
```

Just make sure you do a `poetry install` in order to generate the `poetry.lock` file. This file is used by the EMR CLI to auto-detect a Poetry project.

```bash
cd poetry-test
poetry install
```

> **Warning** We specify Python 3.7.10 as that's what is used by default in EMR Serverless. You may experience different results or errors when using another Python version.

When we run `emr package` or `emr run` with the `--deploy` flag, a different stage in the `Dockerfile` is used that uses the Poetry Bundle plugin to bundle up your job's dependencies. 

```bash
emr run \
    --entry-point entrypoint.py \
    --application-id ${APPLICATION_ID} \
    --job-role ${JOB_ROLE_ARN} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD) \
    --build \
    --wait
```

There's really no difference here in the `spark-submit` parameters or how the job is run. It's really the difference in the build commands.

If your EMR cluster is running the same version as your EMR Serverless application (and sometimes, even if it's not), you can again run the same code on EMR on EC2.

```bash
emr run \
    --entry-point entrypoint.py \
    --cluster-id ${CLUSTER_ID} \
    --s3-code-uri s3://${S3_BUCKET}/tmp/emr-cli-demo/$(basename $PWD)
```

# Conclusion

That's it for now! Thanks for joining as we explored the varied ways of deploying PySpark code to EMR and how the EMR CLI can make it all as easy as a single command. 