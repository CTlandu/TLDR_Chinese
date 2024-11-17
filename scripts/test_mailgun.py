import requests
import os

def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox918d0ad832384ac98c085c3512896938.mailgun.org/messages",
  		auth=("api", os.environ.get('MAILGUN_API_KEY')),
  		data={"from": "Excited User <mailgun@sandbox918d0ad832384ac98c085c3512896938.mailgun.org>",
  			"to": ["bar@example.com", "YOU@sandbox918d0ad832384ac98c085c3512896938.mailgun.org"],
  			"subject": "Hello",
  			"text": "Testing some Mailgun awesomeness!"})
   

if __name__ == '__main__':
  
    send_simple_message()
    print("Message sent")