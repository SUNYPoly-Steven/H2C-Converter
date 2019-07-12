# H2C-Converter
A converter from Harvest to Clockify, It will take the current weeks time entries from a configured Harvest account and create time entries in Clockify

## How to use
After cloning the repository, fill in the environment variables in ```h2c.sh``` as described below.

Make sure you have the required packages installed:
  ```
  pip install "python-harvest-redux>=3.0"
  pip install requests
  ```

Then run the script with ```sh h2c.sh``` 

## Environment Variables
Below is the list of environment variables the H2C uses to configure itself for your harvest and clockify accounts:

---
```
H2C_HARVEST_COMPANY_NAME
```

This is the company you are under in harvest, it shows up in the URL for the harvest website and is used to fill that in.

Harvest URL example: [https://COMPANY_NAME.harvestapp.com](https://harvest.harvestapp.com)

---
```
H2C_HARVEST_EMAIL
```

This is the email address used to sign into harvest

---
```
H2C_HARVEST_PASSWORD
```

This is the password used to sign into harvest

*Note: This will be updated to use a more secure authentication method 
in the future*

---
```
H2C_CLOCKIFY_START_TIME
```

This is the time you begin your work day and will be the start time
used in the clockify timer

*(24 hour clock, formatted as: HH:MM:SS)*

---
```
H2C_CLOCKIFY_API_KEY
```

This is the API key that can be generated on the clockify website
found at the bottom of the [profile page](https://clockify.me/user/settings)

---
```
H2C_CLOCKIFY_PROJECT_NAME
```

This is the name of the clockify project to put the time under


# Limitations

Currently H2C is just a tool I use for my own very limited use case, so it is not very flexible. However I plan to expand it's capabilities when I have the time.

Right now there is very little error checking functionality. As the project grows I will become more featureful and most likely more useful to many people.

# Contributions
I am always open to contributions, if you want post an issue and I will try to work on it as soon as I can. However if there is an issue that you want to implement yourself, as I can get very busy and might not have time to do it myself. I will gladly merge in a helpful pull request.
