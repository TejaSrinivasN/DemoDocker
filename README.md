Exercise for AWS ECS - Fargate with Docker images - Beginner's step by step guide.
In this exercise you will be building a simple python flask Docker image, store it in AWS ECR(Container Regsitry) and run the container in Fargate managed by AWS ECS.

Setup
A valid AWS account is required.

The IAM user account should have the Administrator Access to management console.

VPC setup (Can use the default if it is already setup)

Setup Steps Here

AWS CLI must be setup to configure AWS config

Demo Project
Use the following Github link to clone the Python Flask app from the repo. A very simple app with a single path mapping that returns a hello world page with a counter.

git@github.com:invisibl-labs/python-flask-docker.git
Use these commands to run the app and check. Make changes to the commands based on your OS.

cd python-flask-docker
// install dependencies
python3 -m pip install -r requirements.txt
// run the app
flask run
Use the URL shown in the output.

Screenshot 2022-06-15 at 7 39 18 AM

Should see a page like this.

Screenshot 2022-06-15 at 7 38 57 AM

Create a Docker Image
We need to create a Docker image to run the container on AWS Fargate. A basic knowledge of Docker commands is required for this step. Dockerfile is available in the project root folder. The docker file uses python 3.9.2 base image.

FROM python:3.9.2

WORKDIR python-docker

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
Run the following docker commands to build and check the images.

// build the image. By default uses the Dockerfile in the "." current path
docker build -t python-flask-app:1.0 .
// check images
docker images
Should see the python-flask-app image in the list.

Run the Docker Image
Test the image by running it.

// Run the docker image
docker run -d -p 5000:5000 python-flask-app

// Check if container has started
docker ps

// Check container logs to see if the app is running. use the container id listed
docker logs <container id>
Check if you are able to access the app using http://localhost:5000

Push the Docker image to AWS ECR(Elastic Container Registry)
AWS ECR is a container repository where the docker images can be stored and retrieved and also used to run the containers on AWS ECS.

This requires an account with IAM role having Administrator access.

Create a repository
You can create a repository using AWS console or AWS CLI

Using AWS console
Navigate to ECR service page and click on 'Get Started'. Create a private repository as shown below.

Screenshot 2022-06-15 at 8 12 06 AM

Screenshot 2022-06-15 at 8 12 18 AM

Should see the repository created. Screenshot 2022-06-15 at 8 15 16 AM

Using AWS CLI
First, you need to authenticate to AWS ECR. Replace the region and aws_account_id in the following command

aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
After login, create a new repository using the following command.

aws ecr create-repository --repository-name python-flask-app --image-scanning-configuration scanOnPush=false --image-tag-mutability IMMUTABLE --region ap-south-1
Should see the response in CLI Screenshot 2022-06-15 at 8 25 30 AM

You can check the AWS console as well.

Tag and Push the docker image to ECR repository
Tag the image

docker tag python-flask-app:1.0 812455318414.dkr.ecr.ap-south-1.amazonaws.com/python-flask-app:1.0
Push the image

docker push 812455318414.dkr.ecr.ap-south-1.amazonaws.com/python-flask-app:latest
You can also refer to the "Push Commands" shown by ECR console. Screenshot 2022-06-15 at 9 30 36 AM

After pushing the docker image, you can view the image in the AWS ECR console.

Screenshot 2022-06-15 at 9 50 05 AM

Deploy the image to AWS ECS
AWS ECS (Elastic Container Service) allows easy deployment and management of containers. Schedules the containers to run on the cluster according to the resource needs. Integrates seamlessly with other AWS services like ELB, Security groups, EBS and IAM roles.

Recommend reading the documentation AWS ECS

Setup the required IAM role permissions
The container instances in the cluster are managed by agents that use ECS API. The agent services require access to the APIs. Setup the necessary IAM role policies for the same

Screenshot 2022-06-15 at 10 21 54 AM

Setup the ECS cluster
Before running through the next steps, recommend recollecting the main concepts like Cluster, Service, Tasks, Containers. Refer to the documentation ECS Components

For this exercise we will be creating a ECS cluster with Fargate to run the containers. Recommend reading about Fargate to recollect the concepts. AWS Fargate

Create a new cluster. Select the one with AWS Fargate.

Screenshot 2022-06-15 at 10 48 45 AM

Provide a cluster name and create

Screenshot 2022-06-15 at 10 51 32 AM

Created cluster details

Screenshot 2022-06-15 at 11 00 48 AM

Create a Task definition
Screenshot 2022-06-15 at 11 26 42 AM

Select Fargate from the options

Screenshot 2022-06-15 at 11 27 11 AM

Enter Task definition details

Screenshot 2022-06-15 at 11 34 57 AM

Enter Task size

Screenshot 2022-06-15 at 11 40 46 AM

Add Container
Screenshot 2022-06-15 at 11 41 46 AM

Provide the container service details. Change the image url as per your setup.

Screenshot 2022-06-15 at 12 00 25 PM

Leave the rest of the container details to default and hit 'Add'. Should see the container created.

Leave the rest of the Task definition fields and hit 'Create'. Should create Exceution role, Task definition and CloudWatch log group.

Screenshot 2022-06-15 at 12 05 32 PM

View the Task defintion details

Screenshot 2022-06-15 at 12 10 44 PM

Create a Service
Once the Task definition and Container are configured, we are ready to create a service.

Navigate to the 'python-app' cluster details page and hit 'Create' under the 'Service' tab.

Enter the service details

Screenshot 2022-06-15 at 1 01 35 PM

Screenshot 2022-06-15 at 1 01 49 PM

Use the default deployment strategy - Rolling update Screenshot 2022-06-15 at 1 01 58 PM

Select the default VPC and select Subnets that are configured Screenshot 2022-06-15 at 1 04 59 PM

Leave the load balancer setting to 'None' Screenshot 2022-06-15 at 1 05 10 PM

Leave the Auto scaling setting to default Screenshot 2022-06-15 at 1 05 26 PM

Once the service is created, you can see the Service and Tasks created under the respective tabs in the cluster details.

Screenshot 2022-06-15 at 1 06 14 PM

You can see the 'Task' is in running state.

Screenshot 2022-06-15 at 1 11 30 PM

Updating the Security Groups
Navigate to the python-service details page and click on the security groups link to open the security groups page.

Screenshot 2022-06-15 at 1 17 21 PM

Add an inbound rule to allow port 5000 to allow access to the python app.

Screenshot 2022-06-15 at 1 20 05 PM

Access the python app
We need the public IP to access the app as we have not setup the load balancer.

Open the 'Task' details from the cluster details page and look for public IP under the Network section.

Screenshot 2022-06-15 at 1 13 57 PM

Use the public IP to access the python app on browser. If you see the page as shown below, your ECS Fargate setup is complete.

http://public-ip:5000

Screenshot 2022-06-15 at 1 24 22 PM

Don't forget to clean up the resources
Clean up the repository created in ECR
Clean up the ECS cluster
