# sqlalchemy-spanner
Demo exploring how to use the spanner dialect for sqlalchemy

## How to execute this solution on Google Cloud

### Set up an environment on Google Cloud using Terraform

Life is short, so let's use Terraform to first set up an env on Google Cloud.

Change the working directory to the terraform folder

```shell
cd terraform
```

Create a file named terraform.tfvars

```shell
touch terraform.tfvars
```

Add the following configuration variables to the file, with your own values.

```shell
billing_account = "YOUR_BILLING_ACCOUNT"
organization = "YOUR_ORGANIZATION_ID"
project_create = true/false
project_id = "YOUR_PROJECT_ID"
region = "YOUR_GCP_LOCATION"
developer_email = "YOUR_EMAIL_ADDRESS"
```

Run the following command to initialize Terraform:
```shell
terraform init
```

Run the following command to apply the Terraform configuration.
```shell
terraform apply
```

### Set up environment variables

navigate up to the root of the repository
```shell
cd ..
```

execute the bash script, created by terraform, to make some env vars
```shell
source scripts/00_set_variables.sh
```

### execute the program

navigate up to the root of the repository

auth
```shell
gcloud auth application-default login
```

run the code as a python module

```shell
python -m app.main
```

## Clean up

### Spanner Studio

drop tables

### Terraform

run terraform destroy
