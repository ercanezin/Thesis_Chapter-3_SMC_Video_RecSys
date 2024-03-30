# # YouTube Video Recommender Code for Chapter 3
</div>

This repository is created for Chapter 3 of the thesis titled 'Towards Context-Aware Recommender Systems for Tourists'.


# Abstract 


This chapter expands on Recommendation Systems (RS) and introduces a novel Group Decision Making (GDM) approach. Leveraging data from the YouTube API, we gather comprehensive video information related to various options, like trip locations. Unlike traditional methods relying on explicit user preferences, our approach infers preferences from user interactions with videos using Collaborative Filtering (CF). Additionally, we integrate trust dynamics within the group by recommending videos from different members. By analyzing user interactions, we infer trust relationships within the group to aggregate preferences and select optimal destinations. Finally, we showcase the application through a YouTube API-based platform, emphasizing user engagement in enhancing the trust network for informed decision-making.
 

# Getting Started
  
  You need Python 3.7 and higher to run the codes and you need the latest version of the following packages to run both codes and jupyter notebook. The list of this package is in the requirements.txt file. Please use pip to install it.

ATTENTION: If you intend to implement the project, we strongly advise you to undergo Django training beforehand. We also recommend creating a Google Developer Account and obtaining a secret key to access videos and map data hosted on Google servers. Additionally, MySQL needs to be installed separately to allow the application to interact with a database. However, once the necessary modifications are made to the system, you can choose any database you prefer.

	Here are few files that you need to update once you gain Google APIs secret key. 
	File name: settings.py, Change this line: YOUTUBE_DEVELOPER_KEY = '' # Please add your unique Youtube developer Key here.
	File name: settings.py, Change line 82. Update the MySQL connection settings to your desired connection settings.
	File names: add_pois.html and edit_pois.html. Update with your key: <script src="https://maps.googleapis.com/maps/api/js?key=###your_maps_key###&v=3.exp&libraries=places"></script> 
	We have also included Jupyter notebooks for the analysis in the notebook folder. Therefore the requirements includes libraries for them. Deduct them if needed.

# List of Libraries in the requirement file
  
    Django
    django-embed-video
    django-mathfilters
    mysqlclient
    google-api-python-client
    numpy
    youtube-dl
    pandas
    jupyter
    seaborn
    scikit-learn

 

# Files and their usage
	
	TravelMadeEasy -- Contains Django Related Module files
	css -- Contains css static code for front-end of the application
	fonts -- Contains fonts used by Django for front-end of the application
	recommender -- Contains code that works in the back-end of the application and also handles requests.
	manage.py -- Main Django management file to control Django operations.
	requirements.txt -- The file to install required libraries easily. 
	notebooks  -- This directory contains analysis files along with data collected from experiments. 


If you have any questions, please get in touch with ezinercan@gmail.com

# Bibtex
If this work is helpful for your research, please consider citing  

# Acknowledgement
 
Many thanks to my former supervisor Dr Ivan Palomares and colleague Dr James O. Neve for their invaluable input during this research.
 
