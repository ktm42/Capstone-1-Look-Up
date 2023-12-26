# Travel Your Way
Users can use this app to log their dream travel estinations and the top amount they want to pay for an airline ticket. Once a day the app will perform a search to see if there are any deals that meet the criteria and alert the user if any deals are found in a six-month period starting from the current date. This eliminates the need for the user to remember to search for deals and also allows a list of travel destinations to be created and stored to be easily built upon.
## Stack
Python, Flask, SQLAlchemy, CSS, HTML
## Third-party APIs
I used the Tequila API/Kiwi.com to get the appropriate IATA codes for destination cities and then search for flights that fall within your set parameters.

If this app were deployed into production, the Twilio API would be used to send the user SMS notifications after the search is run.