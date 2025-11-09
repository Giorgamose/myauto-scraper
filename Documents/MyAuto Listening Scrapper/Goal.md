Goal:
Create a Python backend application that periodically checks myauto.ge for new car listings matching one or more configurable search URLs (example below).
When a new listing is detected, the system should send me a WhatsApp message notification via Meta API.
The entire setup (hosting + database + automation) must operate at zero cost using free-tier services.

🎯 Example Car Listing URL:
https://www.myauto.ge/ka/s/iyideba-manqanebi-toyota-land-cruiser-land-cruiser-prado-1995-2008?vehicleType=0&bargainType=0&mansNModels=41.1109.1499&yearFrom=1995&yearTo=2008&priceFrom=11000&priceTo=18000&currId=1&mileageType=1&fuelTypes=3&locations=2.3.4.7.15.30.113.53.39.38.37.36.40.41.44.31.5.47.48.52.8.54.16.6.14.13.12.11.10.9.55.56.57.59.58.61.62.63.64.66.71.72.74.75.76.77.78.80.81.82.83.84.85.86.87.88.91.96.97.101.109.116.119.122.127.131.133.137.139.143&customs=1&page=1&layoutId=1

⚙️ Requirements

Multiple Search Configurations

Ability to monitor several URLs (e.g., different brands/models).

Each search is stored in configuration (e.g., config.json).

New Listing Detection

Script checks each configured URL using MyAuto public API (JSON data).

Compare listing IDs against stored IDs in database.

Identify newly posted listings only.

Notifications

Send a message to my WhatsApp using Meta Graph API.

My WhatsApp number: +995577072753

My Meta App info:

App ID: 850466404119710

App Secret: e588a6f27f463bdc59972f87c151d238

Use free-tier Meta for Developers Sandbox environment for WhatsApp messages.

Persistence / Database

Use a free-tier database or a lightweight file (e.g., SQLite, JSON on GitHub repo).

Should remember already-seen car IDs to avoid duplicate alerts.

Automation & Hosting

Entire project hosted for free (e.g., GitHub + GitHub Actions, Deta Space, or Render Free Tier).

GitHub Actions should run the check every X minutes (e.g., 10 or 15 mins).

On each run, it:

Fetches latest listings

Detects new items

Sends WhatsApp notifications

Updates stored IDs

GitHub Integration

Full working project must be pushed to a GitHub repo.

Include setup guide and .github/workflows/schedule.yml for automation.

Project should be easily extendable (add more URLs in config file).

Zero-Cost Constraint

Every part (hosting, database, messaging API) must be within free limits.

Use no paid libraries, services, or premium APIs.

🔒 Security

Do not hardcode secrets (App Secret or tokens) directly in code.

Store them using GitHub Secrets and reference them in workflow.

Implement .env configuration pattern for local runs.

🧩 Deliverables

Implementation Plan

Detailed explanation of architecture, libraries, and free hosting setup.

Working Python Project

Configurable URLs, new-listing detection, WhatsApp messaging.

GitHub Automation

Cron-based GitHub Actions workflow.

README

Step-by-step setup for others to replicate the project.

📋 Inputs for Claude


Preferred notification frequency:10 minutes, if nothing new is published this should be also sent to me.

Preferred database type SQLite



If anything is unclear, ask me for details 


Please start by producing a complete implementation plan (architecture + flow + free hosting setup + API usage), then wait for my review before generating the code.