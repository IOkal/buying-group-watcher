# New Deals watcher

Welcome to the Deal Watcher tool! This nifty tool is a companion for staying updated with the latest deals, so you never miss out on a bargain. 💸 Here's a dive into what makes this code tick and how you can get it up and running on your AWS EC2 instance.

## What This Code Does 🎯

- **Automated Deal Monitoring**: This script periodically checks a website for new deals and sends you a notification via AWS SNS whenever a new deal pops up.
- **Detailed Alerts**: Each notification includes the deal title, price, retailer, and a direct link to the deal. 
- **Persistent Tracking**: It keeps track of seen deals locally to ensure you only get notified about new deals, even after a restart.

## The Nitty-Gritty Details 🛠️

1. **Logging In**: The script logs into the website using your credentials to access the dashboard with the deals.
2. **Fetching Deals**: It scrapes the page to extract the latest deals, including the title, price, retailer, and URL.
3. **Sending Notifications**: New deals trigger an AWS SNS notification to keep you in the loop.
4. **Local Storage**: Seen deals are stored in a JSON file to prevent duplicate alerts across restarts.
5. **Logging**: Detailed logs are maintained to help you keep an eye on what's happening behind the scenes.

## How to Deploy 📦

1. **Set Up Your EC2 Instance**: Make sure you have Python 3 and the necessary permissions to run the service.
2. **Install Dependencies**:
   ```
   sudo yum update -y
   sudo yum install python3 -y
   pip3 install requests beautifulsoup4 boto3
   ```

3. Configure AWS CLI:
    ```aws configure```

4. **Copy the Script** (or clone this repo): Save the provided Python script on your EC2 instance (e.g., /home/ec2-user/deal_watcher.py).

5. Create a systemd Service:
   * Run `sudo nano /etc/systemd/system/deal-watcher.service`
   * Paste the code below into the text editor
```
   [Unit]
    Description=Deal Watcher Service
    After=network.target
    
    [Service]
    User=ec2-user
    ExecStart=/usr/bin/python3 /home/ec2-user/deal_watcher.py
    Restart=always
    StandardOutput=journal
    StandardError=journal
    
    [Install]
    WantedBy=multi-user.target
```
  * Save the file

6. Enable and Start the Service:
```
sudo systemctl daemon-reload
sudo systemctl start deal-watcher
sudo systemctl enable deal-watcher
sudo systemctl status deal-watcher
```

7. View Logs:
   `sudo journalctl -u deal-watcher.service -f`

## Keeping It Secure 🔒
* **AWS Credentials**: Ensure your EC2 instance has the necessary IAM role with permissions to publish to SNS.
* **Sensitive Info**: Keep your login credentials secure and consider using environment variables or AWS Secrets Manager for added security.

## Ready to Rock? 🤘
With this setup, you're all set to automate deal tracking and never miss out on a great bargain again! Have fun, and happy deal hunting! 🛍️✨

