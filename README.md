# ShopSearch-Django-React

This project is an backend of website built using React, Redux for frontend and Django for backend.
The purpose of the project is:
  -download detailed data of shop from shop website in the case of online mode 
  -show downloaded detailed info of every shop according to user's demand.


## Backend routes

* GET `/api/search-history/`
 users get all search history
        
* GET `/api/offline-items/`
 Users can look at downloaded product detailed info in offline mode  

* GET `/api/onine-items/`
 If users search keyword, backend engine download detailed data including json and image from shop website server, save data in local server.

* GET `/api/item-detail/`
 When users click the specific product, they can get detailed info of that product from local server


   
