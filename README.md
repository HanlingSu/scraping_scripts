## Introduction
This repository contains all the scraping scripts developed for the MLP Project and environmental project. 
The scripts are organized by country and environmental sources are stored in env_project folder.

## The primary goal of this repository is to:

1. Store and manage all scraping scripts for collecting data from sources worldwide.
2. Ensure scripts are properly grouped by country for ease of access and collaboration.
3. Maintain an organized and scalable repository for future development and updates.

## Scraping process
#### Scraping:
1. Direct Scrape:
  - Collect URLs from sitemap 
  - Date archived website structure
  - Empty search results that can be sorted by date
  - Category sections, allowing blacklisting while scraping
  - Selenium dynamic scraping
2.	Old ways:
  - Wayback
  - Gdelt

#### Before batch scraping, check for individual article’s date, title and main text content, if any mismatch from website, a custom parser is required. 

3.	Custom scraping 
  - Inspect the website, locate the html tag of wanted information
  - Load the source page, search for tag like “published”, “title”, “h1”, etc
  - Custom parsing also required in selenium scraping to collect all direct URLs

5.	Patch tools
  - Remove blacklisted articles
  - Duplicates 

6.	Checking scraped sources
  - Look at the monthly counts plot
  - Check the after TCG counts plot

## Problems that might be identified:
1.	Articles are in the wrong ‘articles-year-month’ collection
  - custom parser, rescrape all articles 
3.	Articles have the wrong title or text
  - custom parser, rescrape all articles 
4.	Mismatch count of TCG plot and DB plot
  - rerun patchtools, langauge code issue, TCG process problem
5.	Not enough monthly articles
  - Collect more URLs, selenium scraping, find new sources
