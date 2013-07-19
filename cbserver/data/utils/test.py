from pymongo import MongoClient

client = MongoClient()
db = client.data

answer_queue = db.answer_queue
product_attributes = db.product_attributes

answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "diner", "wrongProduct": "5_star"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "diner", "wrongProduct": "5_star"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "5_star", "wrongProduct": "diner"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "hipster", "wrongProduct": "lil_wayne"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "red_hot", "wrongProduct": "hipster"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "red_hot", "wrongProduct": "lil_wayne"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "lil_wayne", "wrongProduct": "hipster"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "clean_pool", "wrongProduct": "mow_lawn"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "mow_lawn", "wrongProduct": "clean_pool"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "new_york", "wrongProduct": "port_huron"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "port_huron", "wrongProduct": "san_fran"})

answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "san_fran", "wrongProduct": "arkansas"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "san_fran", "wrongProduct": "new_york"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "new_york", "wrongProduct": "san_fran"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "port_huron", "wrongProduct": "arkansas"})


answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "salad", "wrongProduct": "chocolate"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "salad", "wrongProduct": "potatoes"})
answer_queue.insert({"fromUser":"123", "forFacebookId": "123", "chosenProduct": "potatoes", "wrongProduct": "chocolate"})

product_attributes.insert({"product": "diner", "attributes": {"spending_habits": 15}} )
product_attributes.insert({"product": "5_star", "attributes": {"spending_habits": 85}} )
product_attributes.insert({"product": "hipster", "attributes": {"mainstream": 10}} )
product_attributes.insert({"product": "red_hot", "attributes": {"mainstream": 65}} )

product_attributes.insert({"product": "clean_pool", "attributes": {"diy": 85}} )
product_attributes.insert({"product": "mow_lawn", "attributes": {"diy": 65}} )
product_attributes.insert({"product": "new_york", "attributes": {"urban": 95}} )
product_attributes.insert({"product": "san_fran", "attributes": {"urban": 75}} )
product_attributes.insert({"product": "port_huron", "attributes": {"urban": 25}} )
product_attributes.insert({"product": "arkansas", "attributes": {"urban": 10}} )

product_attributes.insert({"product": "salad", "attributes": {"healthy": 95}} )
product_attributes.insert({"product": "chocolate", "attributes": {"healthy": 25}} )
product_attributes.insert({"product": "potatoes", "attributes": {"healthy": 55}} )


