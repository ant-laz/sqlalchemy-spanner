#  Copyright 2025 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

// Terraform local variables
// https://developer.hashicorp.com/terraform/language/values/locals
// to avoid repeating the same values or expr multiple times in this config
//
locals {
  repo_codename = "sqlalcspan"
  image_name = "sqlalcspan-image"
  image_tag = "tag1"
}

// Google Cloud Project
// https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/project
// IF var.project_create = TRUE THEN project_reuse = null THEN new project made
// IF var.project_create = FALSE THEN project_reuse = {} THEN existing proj used
module "google_cloud_project" {
  source          = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/project?ref=v39.1.0"
  billing_account = var.billing_account
  project_reuse   = var.project_create ? null : {}
  name            = var.project_id
  parent          = var.organization
  services = [
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "compute.googleapis.com",
    "spanner.googleapis.com",
  ]
}

// Google Cloud Artifact Registry
// https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/artifact-registry
module "docker_artifact_registry" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/artifact-registry?ref=v39.1.0"
  project_id = var.project_id
  location   = var.region
  name       = local.repo_codename
  format     = { docker = { standard = {} } }
}

// Google Cloud Service Account
// To use for cloud build
// https://cloud.google.com/compute/docs/access/service-accounts#default_service_account
// https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/iam-service-account
 module "build_sa" {
   source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account?ref=v39.1.0"
   project_id = module.google_cloud_project.project_id
   name       = "build-sa"
   //If set to true, skip service account creation if a service account with the same email already exists.
   create_ignore_already_exists = true 
   # authoritative roles granted *on* the service accounts to other identities
   iam = {
     "roles/iam.serviceAccountUser" = ["user:${var.developer_email}"]  //The developer executes build as this SA
   }
   # non-authoritative roles granted *to* the service accounts on other resources
   iam_project_roles = {
     (module.google_cloud_project.project_id) = [
       "roles/storage.objectUser",
       "roles/artifactregistry.writer",
       "roles/artifactregistry.reader",
       "roles/storage.admin",
       "roles/logging.logWriter",
       "roles/run.developer"
     ]
   }
}

// Google Cloud Service Account
// Used as the Cloud Run "Service Identity" https://cloud.google.com/run/docs/configuring/services/service-identity
// https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/iam-service-account
module "api_sa" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/iam-service-account?ref=v39.1.0"
  project_id = module.google_cloud_project.project_id
  name       = "${local.repo_codename}-sa"
   //If set to true, skip service account creation if a service account with the same email already exists.
  create_ignore_already_exists = true
  # authoritative roles granted *on* the service accounts to other identities
  iam = {
    "roles/iam.serviceAccountUser" = ["serviceAccount:${module.build_sa.email}"]  //The build SA deploys so needs this role on this SA
  }
  # non-authoritative roles granted *to* the service accounts on other resources
  iam_project_roles = {
    (module.google_cloud_project.project_id) = [
      "roles/spanner.databaseUser",
    ]
  }
}

// Google Cloud Spanner Instance & Database
// https://github.com/GoogleCloudPlatform/cloud-foundation-fabric/tree/master/modules/spanner-instance
module "spanner_instance" {
  source     = "github.com/GoogleCloudPlatform/cloud-foundation-fabric//modules/spanner-instance?ref=v39.1.0"
  instance_create = true
  project_id = var.project_id
  instance = {
    name         = "${local.repo_codename}-instance"
    display_name = "TF instance in ${var.region}"
    config = {
      name = "regional-${var.region}"
    }
    num_nodes = 1
  }
  databases = {
    sqlalcspan-database = {

    }
  }
}

// https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file
// Generates a local file with the given content.
// Makes devops easier as bash scripts will use IDs of terraformed resources
// Example bash script create environmental variables will use IDs of
// Google Cloud resources created by Terraform.
resource "local_file" "variables_script" {
  filename        = "${path.module}/../scripts/00_set_variables.sh"
  file_permission = "0644"
  content         = <<FILE
# This file is generated by the Terraform code of this Solution Guide.
# We recommend that you modify this file only through the Terraform deployment.

export PROJECT_ID=${module.google_cloud_project.project_id}
export CLOUDSDK_CORE_PROJECT=${module.google_cloud_project.project_id}
export LOCATION=${var.region}
export API_SERVICE_ACCOUNT_EMAIL=${module.api_sa.email}
export BUILD_SERVICE_ACCOUNT_ID=${module.build_sa.id}
export CODE_REPO_NAME=${local.repo_codename}
export IMAGE_NAME=${local.image_name}
export IMAGE_TAG=${local.image_tag}
export SPANNER_INSTANCE_ID=$(echo "${module.spanner_instance.spanner_instance_id}" | xargs basename)
export SPANNER_DATABASE_ID=$(echo "${module.spanner_instance.spanner_database_ids.sqlalcspan-database}" | xargs basename)
FILE
}