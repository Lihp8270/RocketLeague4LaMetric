# RocketLeague4LaMetric
Python script to display your MMR, and notify you of changes to your MMR on the LaMetric Time clock

The server should run on an rPi or similar, and is configured so that the client can remotely start and stop the service to prevent spamming.

Server automatically stops after 20 loops with no MMR update.

Client can be used with the Start, Stop, or Status arguments.  Status simply gives you the current status of the scraper service.  Running the script with no argument will alternate the state of your rPi service.

Parts of the scraping code of been redacted, you are to find your own source, and method of fitering this information.  It should only be done with expression permission of the site owner.

It is recommended when using steam to use a scheduler to run the script when Rocket League starts and closes
