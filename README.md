"# Amazon-Warehouse-Web-Scraper" 

Pretty simple python script that is used to monitor and report when amazon posts new uk warehouse jobs.

Why? 
The amazon warehouse website says it sends notifications but it doesn't, the feature simply does not work. This script monitors the website and gathers data using a lot of hard-coded and pretty poorly coded methods.

How?
Loads the webpage 
Accepts the cookies
Clears the default location filter to list all jobs
Feedbacks 
Saves jobs to file and if the job isn't already in file then it emails

Why release?
Because I have created a more advanced version which runs off of the amazon jobs api and is now setup on a web server to monitor the page 24/7

I am fairly certain other scripts like this already exist but this one was fun to make for myself.