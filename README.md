<h1 align="center"> Phipps Conservatory Pass Server </h1> <br>

## Table of Contents
* [Introduction](#introduction)
* [Features](#features)
* [How does it work](#how-does-it-work)
* [Getting started](#getting-started)
* [Future work](#future-work)
* [Built with](#built-with)
* [Acknowledgments](#acknowledgments)
* [License](#license)

## Introduction
This independent project that was done in collaboration with Professor Heimann and Professor Moussawi from the Carnegie
Mellon University Information Systems Department. Along with Mr. Cassidy from the Phipps Conservatory & Botanical Garden in Pittsburgh. 
Phipps Conservatory has already won numerous awards and honors regarding
[green sustainability](https://www.phipps.conservatory.org/green-innovation/at-phipps/center-for-sustainable-landscapes-greenest-building-museum-garden-in-the-world).
Their mission is to to "*advance sustainability and promote human and environmental well-being through action and research*".
To help continue their mission, this independent project's goal is to create a relatively automated way of generating and updating *passes*, which
can be opened on digital devices for both Apple and Android (Apple comes with a pre-installed wallet that can automatically add and open passes, and the Google Play Market has an comparable [app](https://play.google.com/store/apps/details?id=io.walletpasses.android&hl=en). This is achieved through a rest API service that follows Apple's PassKit Web Service [specification](https://developer.apple.com/library/archive/documentation/PassKit/Reference/PassKit_WebService/WebService.html).
For this particular project, at its current state, all passes are created specifically as digital membership cards. Further applications can be available in the future, and are discussed more below.

## Features
  * Automated Creation and Updating of *passes*

*Passes* are generated and created automatically for membership records on a 1-1 cardinality. Any updates to a membership record will be 
reflected in the passes themselves. These updates will be pushed to a registered user's device, allowing users to see the appropriate updates for their passes in real time.

  * Simple GUI Interface

The current interface provides two main views (excluding the main dashboard): One to upload the latest membership records, and another
used to send initial passes to members (via provided e-mails). Appropriate responsive flash messages and pop-ups are provided to help guide the user's interaction with the service.

 * Easy Customization

Many aspects of this project can be customized. At the project's current state, customization cannot be done via the GUI interface; however many aspects of the project
can be easily changed within the code base (further details below). Examples of this include: changing the e-mail body, changing look of passes, adding new types of *passes* (such as gift card or event *passes*).


## How does it work
### Overview
A digital card for mobile devices is referred to as a *pass*. A *pass* itself is nothing more but a compressed zip folder of digital assets (such as image icons) and a .json file (which contains the 'data' for the *pass*). Thus, this project is primarily a REST server implementation for *passes* written in Python (using the Flask framework). For more information regarding how a *pass* is created, it's limitations and more,
 refer to [here](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Creating.html#//apple_ref/doc/uid/TP40012195-CH4-SW1).

This REST api service allows for the **C**reaating, **R**etrieving, **U**pdating of membership records, and their associated pass records (in this current developmental phase, old membership records are simply kept). Data in the database relies on regular intervals of membership data uploaded (as a .csv file). The expected workflow would be:
1. A Phipps Conservatory employee logs onto the site
2. They attach a scanner to their work computer, and place the cursor focus into the Altru System
3. The employee can send a pass to a user via the site. This email will contain the pass itself, as well as instructions on how to add to add to their device.
4. A member can install the pass onto their device if they haven't already. If there has been an update to their membership record, their details will be reflected in real time.
5. When arriving at Phipps, the member can open their digital *pass*, and the employee can scan the barcode on the *pass*.
members.
6. The scanned data will auto-populate their existing registering system. 
7. At some regular interval, an employee will download need to download the latest membership data, and upload this to the website to update
the membership records within the server (which automatically starts the process of creating new *passes* for new members, and updating existing existing ones).

### Front-End
TODO: Add pictures for two main functions here

Currently, the front-end component consists of two main features: Sending initial passes to users, and
uploading a csv file containing membership data (to create/update membership and pass records). Because this is still in developmental phase, additional views are available on the left hand side (such as tables showing the data for members, *pass* data and device data). These additional views should be removed if deployed in production for obvious privacy reasons. They are currently kept for convenience sake in development. Additionally, there is another feature that allows for data to be cleared. Again, this is for development testing purposes and should be removed in end production. At it's current state, this project does not have a login page, and should be one of the higher priorities for future development.
### Back-End
TODO: Add images from /docs here

There are various components that are in play in the backend, and this section will try to cover in detail each major section:
1. Data Upload
    * Stale data will be a recurrence until new data is uploaded. Any files uploaded will first be checked to see if it is of csv file type, and will be automatically reject if not.
    * When a new csv data containing membership records is uploaded, it will first check to see if any prior data exists. If not, this first membership data will act as our initial dataset, and will populate the database accordingly.
    * If there has been an upload prior to this, a comparison of the data will trigger. It will iterate the new data, line by line, checking to see if that record exists in the old (using set comparison for faster processing). After collecting all membership record differences, each record is then checked to see if there is an existing membership record based on the primary key (member_id).
        * For each existing member, the rest of their details are updated. A new *pass* record is created. Based on the member's *pass* primary key (card_id), we check to see if there are any registered devices for this pass. Any registered devices are then sent a push notification of a change. The user's device will then retrieve a list of changed *passes* (a device can have multiple *passes*). It will then send a request for each change *pass*, and replace the old *pass* with the new.
        * For each new member, a new membership record and *pass* record is simply created.
        * Each member's pass is stored on the local machine. In terms of space complexity, each .pkpass file is only a few megabytes total, and will take up at most a few gigabytes. Local storage is the current means of the server being able to find and send the correct *pass*. Future storage is discussed further below.
    
2. Sending a Pass
    * Passes are sent to a member based on their associated e-mail address with that membership record.
    * After clicking the 'Send Pass' button, that card record's last_sent field will be updated.
    * The message is currently hard-coded in, as the contents of the body contain static instructions on opening the passes across a variety of devices (for which it does not appear to change often).
    * Passes are attached to the e-mail as a .pkpass file.
        * Adding to a smartphone will also register the device, with the server receiving a unique push_token that, alongside other authentication metrics, will be used to send updates in real-time
    * After a member has added the *pass* to their phone, it will update the associated card record's last_update field, to help indicate for the user that this *pass* has been added by the end-client.
    
Fig 1.1: Interaction between client and server

<img src="https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Art/client_server_interaction_2x.png" width="500" />
    
*More specific details regarding interactions from client to server can
    be found [here](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/Updating.html#//apple_ref/doc/uid/TP40012195-CH5-SW1), and AppleKit REST protocols can be found [here].(https://developer.apple.com/library/archive/documentation/PassKit/Reference/PassKit_WebService/WebService.html)
## Getting Started

### Prerequisites
* Apple Developer Account
* PEM files in /app/certificate
* Python 3.6.4
* Pip
* Docker
* AWS Account (used in following examples, depends on deployment)


### Setup and Installation

#### Environmental Variables
There are several environmental variables that are needed for this project to successfully
work:

| Variable Name | Expected or < Example Value >  | Description |
| ----------- | ----------- | ----------- |
| LANG      | en_US.utf-8       | Set locales to US English       |
| LC_ALL   | en_US.utf-8        | Set locales to US English       |
| SECRET_KEY   | < CnyShkdGFkgM+kbb >        | Needed to start user sessions. This can be done in Terminal via command: $ openssl rand -base64 12        |
| PASS_FOLDER   | pkpass files        |        Location of member's pass files.        |
| FLASK_APP   | app.py        | Allows for flask to be run via command $ flask run       |
| PEM_PASSWORD  | < qaplaqaplaqaplqa >        | Passwords for the PEM certificate files, needed for the signing of digital *passes*, as well as sending to APN (Apple Push Notification) service        |
| SERVER_EMAIL   | <abc@gmail.com>       | The e-mail address that sends e-mails to members       |
| SERVER_EMAIL_PASSWORD   | < 123456 >       | The e-mail password for the above mentioned address      |
| APP_SETTINGS   | config.DevelopmentConfig OR config.ProductionConfig        | Sets the current configurations for the app       |
| DATABASE_URL   | <postgresql://localhost/phipps_passes>        | The URL of the remote database. NOTE: This assumes password for a user of this database is in the URL.      |

Please keep in mind that for local testing, this needs to be set up for each Terminal session. The Dockerfile template will need to be set in order for the Image to run successfully locally.

#### Certificates
Each type of *pass* (ie. general, gift) will need to have a unique type identifier. The below steps are for creating a valid Pass Type ID To proceed further, you **will** need to have an Apple Developer Account (not the free version, but the annual subscription service). 
1. Log into https://developer.apple.com
2. Click the 'Certificates, IDs, & Profiles' tab
3. Under 'Identifiers', click 'Pass Type ID'
4. Add a new identifier with the + symbol
5. Provide the identifier with a description, and the identifier name
    5a. An example of the identifier would be: pass.org.conservatory.phipps
    
Every Apple project typically has an associated App ID. It is likely that you already have a default one associated with your Apple account, but if not:
1. Log into https://developer.apple.com
2. Click the 'Certificates, IDs, & Profiles' tab
3. Under 'Identifiers', click 'App ID's'
4. Add a new App ID with the + symbol
5. Provide the ID with a description, and an explicit App ID name
    5a. An example of the identifier would be: *com.phipps* (it will be appended with your Apple Account's App ID Prefix).

Another important facet for this service to run successfully is to provide valid PEM certificates in the /app/certificate directory. The below steps are for creating the 'Pass Type ID', and 'Apple Push Services' certificates:
1. Log into https://developer.apple.com
2. Click the 'Certificates, IDs, & Profiles' tab
3. Add a new certificate with the + symbol
4. Click on either 'Pass Type ID' or 'Apple Push Notification service SSL (Sandbox & Production)' options
5. If you selected 'Pass Type ID', choose the previous Pass Type ID. If you selected 'Apple Push Notification service SSL (Sandbox & Production)', choose an existing App ID
6. After clicking 'Continue', you will be brought to a page that asks you to provide a Certificate Signing Request (CSR) from your Mac. Follow the screen instructions before clicking on 'Continue'
6a.

#### Running locally without Docker
TODO
#### Running locally with Docker
TODO
#### Deployment via AWS Beanstalk
With the provided DockerFile template, we can easily create a Docker image of the entire project to be deploy onto any virtual machine. For demonstration purposes, one such example can be done via Amazon Web Service's Beanstalk. The following instructions explain a thorough process of deployment. Note: the domain phippsconservatory.xyz is used in the following examples, and is necesssary for later SSL certificate to achieve https. If you are a CMU IS student, please contact georgeY852@gmail.com to have access to this domain for future testing. 
TODO


#### Miscellaneous Commands
Below are several miscellaneous commands that you may need to use:

Add Environmental Variable:
Below is an example of adding an environmental variable to a current sessions:
```bash
$ export FLASK_APP=app.py
```

Run Flask Application locally:
For development and testing, you can run the flask application locally simply as follows:
```bash
$ flask run
```

Database Reset/Initialization:
The sample provided Docker template calls these commands already, but if you would like to test locally without using docker a database reset and initialization may be needed. Prior to reseting, make sure the database has no prior existing 'Alembic_version' table
```bash
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

Run Docker Image locally:

This requires Docker installed on the local machine, as well as being in the main outside directory (not in /apps) to work:
```bash
$ docker build -t phipps-passes .
$ docker run -p 80:80 -v /<path>/<to>/<repo>/Phipps API server/app/:/app/ --name flask1
 phipps-passes
```

Stop Docker Image locally:

In some cases, the docker image cannot be stopped via control + c. In those cases, run the following commands to stop the Docker processes. 

```bash
$ docker stop $(docker ps -a -q)
$ docker rm $(docker ps -a -q)
```

Drop Postgres Tables and Schema:

This assumes the backend database is a remote Postgres table:
```bash
$ DROP SCHEMA public CASCADE;
$ CREATE SCHEMA public;
```

## Future work
There is still a wide list of items that this project would need to get closer towards final deployment. While most of the grunt work has been done, primarily the backend interaction with the frontend and client, there are still components that need to be implemented for both the front and backend. These are listed in order of importance:
1. A proper login service - Because this project is currently used as a proof of concept, there is no security measure in place for it's usage. A new User model will need to be added in the backend database, and flask session/reroutes would be needed
2. Asynchronous task for data processing - This can be achieved either by using Threading, or by using something like Redis to have a queue of tasks to operate on
3. Reworked front-end design - I currently am using an open-source front end dashboard. It would be ideal if this was entirely recreated from scratch (primarily just html/css as the javascript logic can be used anywhere)
4. Handling errors gracefully - As of now, there are only a few error handles that I created (ex. if no .csv file is selected when uploading). Ideally, there should be more to cover all cases. 
5. If you are using nginx as the reverse proxy, make sure to edit the *nginx.conf* file to increase the size of the default limit to at least 10 megabytes with the line:
    ```bash
    client_max_body_size 100m;
    ```

## Built With
* [Docker](https://www.docker.com/) - Used to easily create a containerized image of entire project, to be deployed onto any virtual machine or locally

* [Flask](http://flask.pocoo.org/) - Used to build the entire server, both backend and frontend

* [Git](https://git-scm.com/) - Used for version control


## Acknowledgments
TODO

## License

This project is licensed under the MIT License.
