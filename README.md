Name: Rohan Rabbi(mr4280) & Yi Quan (yq2311)

# Chatbot Concierge #

## About ##

Frontend starter repository for HW 1 of the Cloud Computing & Big Data
class at Columbia University and New York University.

## Usage ##

1. Clone the repository.
2. Replace `/assets/js/sdk/apigClient.js` with your own SDK file from API
   Gateway.
3. Open `chat.html` in any browser.
4. Start sending messages to test the chatbot interaction.

## Outline:

This assignment has the following requirements:

Build and deploy the frontend of the application
Repurpose the following frontend starter application to interface with your chatbot
https://github.com/ndrppnc/cloud-hw1-starter Links to an external site. 
Host your frontend in an AWS S3 bucket
Set the bucket up for website hosting
https://docs.aws.amazon.com/AmazonS3/latest/dev/HostingWebsiteOnS3Setup.htmlLinks to an external site.
Build the API for the application
Use API Gateway to setup your API
use the following API/Swagger specification for your API
https://github.com/001000001/aics-columbia-s2018/blob/master/aics-swagger.yamlLinks to an external site.
Use http://editor.swagger.io/ Links to an external site.to visualize this file
You can import the Swagger file into API Gateway
https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-import-api.html Links to an external site. 
Create a Lambda function (LF0) that performs the chat operation
Use the request/response model (interfaces) specified in the API specification above
For now, just implement a boilerplate response to all messages:
ex. User says anything, Bot responds: "I’m still under development. Please come back later."
Notes
You will need to enable CORS on your API methods
https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html Links to an external site. 
API Gateway can generate an SDK for your API, which you can use in your frontend. It will take care of calling your API, as well as session signing the API calls -- an important security feature
https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-generate-sdk-javascript.html

Links to an external site.
Build a Dining Concierge chatbot using Amazon Lex.
Create a new bot using the Amazon Lex service. Read up the documentation on all things Lex, for more information: https://docs.aws.amazon.com/lex/latest/dg/getting-started.html Links to an external site.  
Create a Lambda function (LF1) and use it as a code hook for Lex, which essentially entails the invocation of your Lambda before Lex responds to any of your requests -- this gives you the chance to manipulate and validate parameters as well as format the bot’s responses. More documentation on Lambda code hooks at the following link: https://docs.aws.amazon.com/lex/latest/dg/using-lambda.html Links to an external site. 
Bot Requirements:
Implement at least the following three intents:
GreetingIntent
ThankYouIntent
DiningSuggestionsIntent
The implementation of an intent entails its setup in Amazon Lex as well as handling its response in the Lambda function code hook.
Example: for the GreetingIntent you need to 1. create the intent in Lex, 2. train and test the intent in the Lex console, 3. implement the handler for the GreetingIntent in the Lambda code hook, such that when you receive a request for the GreetingIntent you compose a response such as “Hi there, how can I help?”
For the DiningSuggestionsIntent, you need to collect at least the following pieces of information from the user, through conversation:
Location
Cuisine
Dining Time
Number of people
Phone number or email (if using SES instead of SNS)
Based on the parameters collected from the user, push the information collected from the user (location, cuisine, etc.) to an SQS queue (Q1). More on SQS queues here: https://aws.amazon.com/sqs/Links to an external site.
Also confirm to the user that you received their request and that you will notify them over SMS once you have the list of restaurant suggestions.

Integrate the Lex chatbot into your chat API
Use the AWS SDK to call your Lex chatbot from the API Lambda (LF0).
When the API receives a request, you should 1. extract the message from the API request, 2. send it to your Lex chatbot, 3. wait for the response, 4. send back the response from Lex as the API response.

Use the Yelp API to collect 5,000+ random restaurants from Manhattan.
Use the following tools:
Yelp API
Get restaurants by your self-defined cuisine types 
You can do this by adding cuisine type in the search term ( ex. Term: chinese restaurants)
Each cuisine type should have 1,000 restaurants or so.
Make sure your restaurants don’t duplicate.
DynamoDB Links to an external site.(a noSQL database)
Create a DynamoDB table and named “yelp-restaurants”
Store the restaurants you scrape, in DynamoDB (one thing you will notice is that some restaurants might have more or less fields than others, which makes DynamoDB ideal for storing this data)
With each item you store, make sure to attach a key to the object named “insertedAtTimestamp” with the value of the time and date of when you inserted the particular record
Store those that are necessary for your recommendation. (Requirements: Business ID, Name, Address, Coordinates, Number of Reviews, Rating, Zip Code)
Note: you can perform this scraping from your computer or from your AWS account -- your pick.


Create an ElasticSearch instance using the AWS ElasticSearch Service.
Create an ElasticSearch index called “restaurants”
Create an ElasticSearch type under the index “restaurants” called “Restaurant”
Store partial information for each restaurant scraped in ElasticSearch under the “restaurants” index, where each entry has a “Restaurant” data type.
You only need to store RestaurantID and Cuisine for each restaurant
NOTE: Make sure you correct set up ElasticSearch, meaning give permission to ElasticSearch that it can be invoked by Lambda function as well as giving Lambda function permission to invoke ElasticSearch. Please follow the ElasticSearch Demo Video shared under Files/Demos.


Build a suggestions module, that is decoupled from the Lex chatbot.
Create a new Lambda function (LF2) that acts as a queue worker. Whenever it is invoked it 1. pulls a message from the SQS queue (Q1), 2. gets a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB, 3. formats them and 4. sends them over text message to the phone number included in the SQS message using SNS (or you can send via email using SES; prompt the user to enter email in the Lex bot instead of phone number) (https://docs.aws.amazon.com/sns/latest/dg/SMSMessages.html Links to an external site.).
Use the DynamoDB table “yelp-restaurants”  (which you created from Step 1) to fetch more information about the restaurants (restaurant name, address, etc.), since the restaurants stored in ElasticSearch will have only a small subset of fields from each restaurant.
Modify the rest of the LF2 function if necessary to send the user text/email.
Set up a CloudWatch event trigger that runs every minute and invokes the Lambda function as a result: https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/RunLambdaSchedule.html Links to an external site.. This automates the queue worker Lambda to poll and process suggestion requests on its own.
 

In summary, based on a conversation with the customer, your LEX chatbot will identify the customer’s preferred ‘cuisine’. You will search through ElasticSearch to get random suggestions of restaurant IDs with this cuisine. At this point, you would also need to query the DynamoDB table with these restaurant IDs to find more information about the restaurants you want to suggest to your customers like name and address of the restaurant. Please note that you do not need to worry about filtering restaurants based on neighborhood in this assignment. Filter only using the cuisine.

 

Extra Credit: 10 pts

Implement state for your concierge application, such that it remembers your last search for both location and category. When a user returns to the chat, they should automatically receive a recommendation based on their previous search. You can use DynamoDB to store intermediary state information and a separate Lambda function to handle the recommendation based on the last search.

 

Example Interaction

 

User: Hello

Bot: Hi there, how can I help?

User: I need some restaurant suggestions.

Bot: Great. I can help you with that. What city or city area are you looking to dine in?

User: Manhattan

Bot: Got it, Manhattan. What cuisine would you like to try?

User: Japanese

Bot: Ok, how many people are in your party?

User: Two

Bot: A few more to go. What date?

User: Today

Bot: What time?

User: 7 pm, please

Bot: Great. Lastly, I need your phone number so I can send you my findings. (NOTE: you can use email and SES instead of text messaging)

User: 123-456-7890

Bot: You’re all set. Expect my suggestions shortly! Have a good day.

User: Thank you!

Bot: You’re welcome.

 

(a few minutes later)

 

User gets the following text message or email:

 

“Hello! Here are my Japanese restaurant suggestions for 2 people, for today at 7 pm: 1. Sushi Nakazawa, located at 23 Commerce St, 2. Jin Ramen, located at 3183 Broadway, 3. Nikko, located at 1280 Amsterdam Ave. Enjoy your meal!”

 

Error Handling / Edge Cases:

Make sure to handle wide range of inputs from the user. Instead of saying 'Japanese', we can input 'I like to eat Japanese food' during the demo. More examples below:

How many people: 2 or two; 0 or negative number should show error and Lex should ask user to input again.
Make sure entered time or date is the future. We can enter time and date as numbers or in words (Oct 5, 5pm or next Monday, at noon).
Validate email address or phone number.
City: I can say 'Manhattan' or "I would like to eat around Manhattan'.
These are just few example cases, make sure to handle all possible edge cases and in case of error, ask the user to answer the prompt again (please don't start over the entire conversation, just ask the prompt again where error occurs).
