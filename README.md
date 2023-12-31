# Fundr

Fundr is a Tinder style fundraising app designed to help people find fundraisers local to them. Users see cards with fundraiser information within a catchment range and can choose to see the next one or save them. Once a user has saved a fundr it will be in their following page and any update posts from the Fundrs they follow in their home feed. Users can also create fundrs and add posts for their fundrs.

## Usage

Fundr is deployed at: https://fundr-app.fly.dev/

## Timeframe

Fundr was created over the course of a week by a team of three. 

## Brief

The goal was to create a full-stack Django application that fulfills the the following requirements:

- Connect to and perform data operations on a PostgreSQL database (the default SQLLite3 database is not acceptable).
- If consuming an API (OPTIONAL), have at least one data entity (Model) in addition to the built-in User model. The related entity can be either a one-to-many (1:M) or a many-to-many (M:M) relationship.
- If not consuming an API, have at least two data entities (Models) in addition to the built-in User model. It is preferable to have at least one one-to-many (1:M) and one many-to-many (M:M) relationship between entities/models.
- Have full-CRUD data operations across any combination of the app's models (excluding the User model). For example, creating/reading/updating posts and creating/deleting comments qualifies as full-CRUD data operations.
- Authenticate users using Django's built-in authentication.
- Implement authorization by restricting access to the Creation, Updating & Deletion of data resources using the login_required decorator in the case of view functions; or, in the case of class-based views, inheriting from the LoginRequiredMixin class.


## Planning

A trello board was set up for planning and development and as a group we came up with all user stories for the minimum viable product.

We created wireframes for the mobile version and desktop version. These wireframes were created with figma and are below: \
![Imgur](https://i.imgur.com/p6c8pHP.png) \

![Imgur](https://i.imgur.com/6uihgTp.png) \


ERDs were developed and can be seen here: \
![Imgur](https://i.imgur.com/W5yijEd.png)

## Build process

To start we group coded the base templates for both desktop and mobile based on the HTTP USER AGENT key on the request. By doing this we could display the content within this base depending the size of the viewport without having to have lots of css.

At the beginning of each day as a team we would have a stand up and assign user stories to work on throughout the day to ensure we would not be overlapping on features. We started from the most simple tasks, like setting up routing for each page and setting up the models before moving onto the more complex tasks.

I was responsible for creating the models one of which was a profile model as an extension of the user model built in with Django authentication:
 
```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=200)
    location = models.CharField(max_length=7, default="")
    latitude = models.FloatField(default=0.0, null=True)
    longitude = models.FloatField(default=0.0, null=True)
    catchment = models.FloatField(default=100)

    def __str__(self):
        return self.user.username
```

The other models included the fundraiser model and the post model. Once I had created the models I could seed them with dummy data which would allow us to see future features working as we developed them. The seed.py creates dummy data and dummy locations for users, fundrs and posts.


I was also responsible for the create, delete and update functionality of fundrs. When a fundr is created the user puts in a postcode for the location of the fundr, this is then validated to be a legitimate UK postcode using ukpostcodeutils validation function and then converted into latitude and longitude using pgeocode. This is then stored on the fundr model which can then later be used to calculate the distance of the user from the fundraiser.

We take advantage of the browser inbuilt location service which is available on most modern browsers to send the user's current latitude and longitude to our server so that it can be stored on their profile: 
```javascript
    async function constructURL(lat, lon) {
      let baseURL = 'https://fundr.fly.dev'
      let endpoint = '/userlocation/'
      let queryParameters = `?lat=${lat}&lon=${lon}/`;
      let url = baseURL + endpoint + queryParameters
      try {
        await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // Required by django:  CRSF token 
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            userlat: lat,
            userlon: lon,
          })
        })
      } catch {
        console.log('error');
      }
    }

    // Function to retrieve the CSRF token from the cookies
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Use inbuilt geolocation in modern browsers:
    navigator.geolocation.getCurrentPosition((position) => {
      constructURL(position.coords.latitude, position.coords.longitude);
    });
```

We can then find the distance between the user and a fundraiser by calculating the haversine distance. Luckily pgeocode has a built in haversine distance function:
```python 
fundr_location = np.array([[fundr.lat, fundr.long]])
distance = np.round(pgeocode.haversine_distance(fundr_location, user_location),1)
```

On the explore page distance from user is calculated on all fundrs and then filtered based on the users catchment preference. These fundrs are then handed to the frontend as a list and displayed as a stack of cards. A user can press next to go to the next card or save to save that fundr. When the user presses save a post request is sent to the server and the current fundr is added to their *following* field.

I was solely responsible for building the home feed and implementing lazy loading. The home feed is a posts from fundrs that the current user is following in reverse chronological order of when they were posted (most recent first). I used pagination to separate the posts into pages of three and based on the current page which was a parameter in the HTTP request it would send only the current page: 
```python
def home(request): 
  if (request.user.is_authenticated != True): return redirect('/accounts/login/')
  template = is_mobile(request)

  user = request.user
  
  posts = []
  fundrs = User.objects.get(id=request.user.id).fundraiser_set.all()

  for fundr in fundrs:
    post_list = list(Post.objects.filter(fundraiser=fundr.id))
    posts.extend(post_list)

  sorted_list = list(reversed(sorted(posts, key=lambda x: x.date_created)))
  page = request.GET.get('page', 1)
  paginator = Paginator(sorted_list, 3)

  try:
      posts = paginator.page(page)
  except PageNotAnInteger:
      posts  = paginator.page(1)
  except EmptyPage:
      posts = paginator.page(paginator.num_pages)

  return render(request, 'home.html', { 'template' : template, 'posts': posts, 'title': 'Home', 'user': user })
```
On the frontend I used jQuery Waypoints and infinite scroll (http://imakewebthings.com/waypoints/shortcuts/infinite-scroll/) so that when the bottom of the page was in view it sent off the request for the next page and added it to the bottom of the page:

```html
 {% if posts.has_next %}
  <a class="infinite-more-link" href="?page={{ posts.next_page_number }}">More</a>
  {% endif %}
  <div class="loading" style="display: none;">
    Loading...
  </div>
```
```javascript
<script>
  var infinite = new Waypoint.Infinite({
    element: $('.infinite-container')[0],
    offset: 'bottom-in-view',
    onBeforePageLoad: function () {
      $('.loading').show();
    },

    onAfterPageLoad: function ($items) {
      $('.loading').hide();
    }
  });
</script>
{% endblock %}

```

## Challenges

The key challenges in this project were styling and working together with other developers. We bootstrap as much as possible for the styling as a way to save time writing css, however this has resulted in some weird and not very appealing styling when switching from mobile to desktop view. This is in part due to the decision to create two different base templates as although it seemed like a good idea at the time, limited our ability to make the core content of the application different and suitable for all devices. In hindsight more thought should have been put into developing the individual content templates to be responsive however this would have resulted in writing a lot more HTML and with the time constraints of the project could have delayed us and resulted in an incomplete MVP.

Working together with different developers can be difficult especially when there is no 'lead'. With splitting up tasks between us when another developer became stuck with a certain section and I came into help, it was clear that the way they had implemented their functionality would work, but break with any kind of real world usage of the app. Specifically, at the moment, the distance from the user is held on the Fundraiser model and then sorted by that. This works when maybe one or two people are using the application at the same time, however would break as soon as there are several users accessing the same fundrs in their explore page. By this point the developer had been working on it for an extended period and therefore it was not changed - leaving myself a bit frustrated. Had we had more time, it would've made sense for us to do regular code reviews in order to catch bugs in each others code and make sure that it was as efficient and scalable as possible.

# Wins

This was the first time I had implemented lazy loading and I was quite pleased with the result and being able to do it in Django which isn't as responsive as say React. I was also very pleased with my implementation of the user settings page which allows a user to change their catchment range:

```html
<h2>Settings</h2>
<p class="lead">Tweak your distance settings</p>
<div class="slidecontainer">
  <form action="{% url 'update_settings' user.profile.id %}" method="POST">
    {% csrf_token %}
  <input  type="range" min="1" max="100" class="form-range " id="myRange" style="color: pink;">
  <input type="number" id="slider-value" name="catchment" value="{{user.profile.catchment}}" class="d-none form-number"></input>
  <h3 class="display-value" id="display-value">{{user.profile.catchment}}</h3>
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
</div>
{% if messages %}
  <ul class="messages mt-3">
    {% for message in messages %}
    <li{% if message.tags %} class="{{ message.tags }}" {% endif %}>{{ message }}</li>
      {% endfor %}
  </ul>
  {% endif %}

<script>
  document.addEventListener("DOMContentLoaded", function () {
    const sliderEl = document.getElementById('myRange')
    const valueEl = document.getElementById('slider-value')
    const displayValueEl = document.getElementById('display-value')
    valueEl.value = Math.round(valueEl.value)
    displayValueEl.innerHTML = valueEl.value + ' km' 
    valueEl.value = logslider(this.value)
    sliderEl.oninput = function(){
      valueEl.value = logslider(this.value)
      displayValueEl.innerHTML = valueEl.value + ' km'

    }
  function logslider(position) {
  var minp = 1;
  var maxp = 100;
  var minv = Math.log(1);
  var maxv = Math.log(2000);
  var scale = (maxv-minv) / (maxp-minp);
  return Math.round(Math.exp(minv + scale*(position-minp)));
}
  });

</script>
```

It uses a logarithmic scale to allow the user to be more specific at shorter distances and dynamically updates the value. In the backend once it is done it sends a message through to the user to confirm that their settings have been updated or let them know that their has been some error.

## Key learnings

While I was used to coding in Python through university, this was my first foray into application development with Python and it gave me a new perspective on how to use my programming skills in a more practical way with a tangible outcome. Working with a team was eye-opening and I think we did really well given the timeframe and the level of developers we were and the mistakes we made have been good learning experiences. Overall I am happy with outcome of the project and am keen to fix the bugs and add more features.

## Future improvements
Right now there is on way to pledge money towards a fundraiser however this should be an easy fix as the models are set up to hold a current and goal value. The real improvement in this sense would be to implement payment processes for users to actually be able to give money to fundraisers, which is a more complex issue not only due to implementing a payment API but also the legal ramification of handling money pledged to charitable causes.

The UI could do with some work - currently due to the setup of the base templates for mobile and desktop, lazy loading only works on mobile, this is due to issues the viewport for different devices. The style of posts leaves a lot to be desired as there is not much way to distinguish them from individual fundrs as some html and bootstrap was copied to save time when styling.





