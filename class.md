### class 1 : setup joser and simple jwt
### class 2 : overwriting BaseUserCreateSerializer from Djoser to register email, password, firstname, last name, address
### class 3 : login user with jwt using modheader chrome extention
### class 4 : over write BaseUserSerializer from djoser for id, email, password, firstname, last name, address field
### class 5 : Django Rest Framework Permission classes 
- by using permission class parameter in the `ModelViewSet` class
- by implementing `get_permission` method
- defining custom permission class inheriting rest-framework `BasePermission`
### class 6 : DRF model permission creating custom model permission overwritting `perms_map`
### class 7 : update and delete operation
- created a user review api 
- let user update past review post
- secquire the api so that one can only edit his review with custom permission class

## SEction: oder api
task
- add item to cart 
- delete items from cart when oder finished
- models -> serializer -> viewset -> router 
- model used:4

### Create order
- get list of items in the cart
- place the order 
- delete items from cart as order is placed

### services
- in create order class we are doing a lot of task: getting the items in cart, then calculation of price
- in business we might have many comples logics when a order is placed.
- we seperate all these calculation or task from create order serialized and put them in a file or folder called services

### update order
- we often need to change oder details. specially the order stat of the order. 
- also the oder should only be deleted by the admin. normal user should not be able to delete 
- but normal user may cancle an order. also we will not always allow to cancle. if the order is delivered the order should not be cancled

### Model viewset: action
- action decorator 
- custom action for canceling order
- action for `update order`


## Section: product image and documentation
- i product may have multiple images. so instade of single souce created a seperated model for image 
- file extention validator: other than image upload from user should not be accepted
- setup swagger for api documentation: `drf-yasg`
- adding doc string for swagger
- Customize API Documentation Using swagger_auto_schema
- fixing errors throwed by swagger. by short circuit

## Section: deployment
- previously we learned to deploy on render but render is a bit slow.
- setup superbase for postgrerss server
- setup cloudinary for serving media files
- setup whitenoise for serving static files
- deploy on vercel
- send activation email using djoser


