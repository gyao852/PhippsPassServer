<h1 align="center"> Phipps Conservatory Pass Generator and Server </h1> <br>

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
Mellon University Information Systems department, as well as Mike Casidy from Phipps Conservatory in Pittsburgh. 
Phipps Conservatory and Botanical Gardens has already won numerous awards and honors regarding
[green sustainability](https://www.phipps.conservatory.org/green-innovation/at-phipps/center-for-sustainable-landscapes-greenest-building-museum-garden-in-the-world).
Their mission is to to "*advance sustainability and promote human and environmental well-being through action and research*"; 
to help continue their mission, this project's goal to create a relatively automated way of generating and updating 'passes'; which
can be opened on digital devices for both Apple and Android (albeit Apple comes with a pre-installed wallet that can automatically
add and open passes, the Google Play Market has an comparable [app](https://play.google.com/store/apps/details?id=io.walletpasses.android&hl=en).
For this particular project, at its current state all passes are created specifically as a subsitute for paper membership cards
at Phipps.

## Features
  * Automated creation/update of membership passes


Passes are generated and created for membership records on a 1-1 cardinality. Any updates to a membership record will be 
reflected in the passes themselves. Further, these updates are then reciprocated across to prior registered devices, allowing the
end users to see the appropriate updates for their passes as soon as it's been entered into the backend database.

  * Simple GUI interface


While the grunt work is all done automatically in the back, there is a simple frontend component that allows a user to send
the initial e-mails containing instructions and the passes themselves (as .pkpass files) to Phipps Conservatory members. 
The service keeps track of users who have already opened their passes, as well as when the last e-mail was sent for those
who have NOT yet registered their smartphone with their digital pass. To prevent stale data, a new .csv file of the membership 
records is uploaded daily via a simple interface.

 * Easy customization


Many aspects of this project can be customized. From the e-mail body containing instructions, to the overall look and feel
of the current membership passes, to creating new 'types' of passes for special events. These changes are very simply and easy to 
do; albeit changeable in the source code itself.


## How does it work
Much of this is a rehash of Apple Developer guide for their Wallet application (found [here](https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/PassKit_PG/index.html#//apple_ref/doc/uid/TP40012195-CH1-SW1))
TODO
### Overview

### User-End

### Back-End


## Getting Started

### Prerequisites
* Apple Developer Account
* Python 3.6.4
* Pip
* Docker
* AWS Account (used in following examples, depends on deployment)

### Setup and Installation
TODO

## Future work
TODO

## Built With
* [Docker](https://www.docker.com/) - Used to easily create a docker image of entire project, to be deployed on any vm

* [Flask](http://flask.pocoo.org/) - Used to build the entire server, both backend and frontend

* [Git](https://git-scm.com/) - Used for version control


## Acknowledgments
TODO
## License

This project is licensed under the MIT License.
