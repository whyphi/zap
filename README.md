# Zap

Zap is whyphi's temporary (maybe permanent) serverless API solution.

Zap is created using:

- AWS Chalice: Framework that abstracts Python code as serverless functions
- AWS Lambda
- AWS API Gateway
- AWS DynamoDB: AWS's NoSQL Database
- AWS S3: Handles data for application
- AWS IAM: Managing permissions and policies within AWS services

## To get started

Ensure that you have [AWS CLI](https://aws.amazon.com/cli/) installed. Then, set the necessary AWS configuration within your system using:

```bash
aws configure
```

## Local Development

Within Zap, Python dependences are managed using [`pipenv`](https://pipenv.pypa.io/en/latest/). Ensure you have `pipenv` installed within your machine.

To turn on the virtual environment using `pipenv`:

```bash
pipenv shell
```

To install necessary dependencies within `pipenv`:

```bash
pipenv shell
```

To install any additional dependenceis within `pipenv`:

```bash
pipenv install {dependency name}
```

To enable local server for Chalice:

```bash
chalice local
```

## Deployment

### PR Strategy

PRs should be made in the following order:

    Personal PR -> `dev/*` -> `staging` -> `prod`

### CI/CD

This work exists to minimize potential errors being pushed to production. All deployments will happen when PRs are pushed to `dev`, `staging`, and `prod` automatically as GitHub Actions has been already setup.

To find `dev` and `prod` API endpoints, access AWS Lambda and find the respective API Gateway link.
