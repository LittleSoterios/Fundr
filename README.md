# Fundr

Fundr is a Tinder style fundraising app deisgned to help people find fundraisers local to them. Users see cards with fundraiser information within a catchment range and can choose to see the next one or save them. Once a user has saved a fundr it will be in their following page and any update posts from the Fundrs they follow in their home feed. Users can also create fundrs and add posts for their fundrs.

## Usage

Fundr is deployed at: https://fundr-app.fly.dev/

## Timefrme

Fundr was created over the course of a week by a team of three. 

## Brief

The goal was to create a full-stack Django application that fulfills the the following requirements:

Connect to and perform data operations on a PostgreSQL database (the default SQLLite3 database is not acceptable).
If consuming an API (OPTIONAL), have at least one data entity (Model) in addition to the built-in User model. The related entity can be either a one-to-many (1:M) or a many-to-many (M:M) relationship.
If not consuming an API, have at least two data entities (Models) in addition to the built-in User model. It is preferable to have at least one one-to-many (1:M) and one many-to-many (M:M) relationship between entities/models.
Have full-CRUD data operations across any combination of the app's models (excluding the User model). For example, creating/reading/updating posts and creating/deleting comments qualifies as full-CRUD data operations.
Authenticate users using Django's built-in authentication.
Implement authorization by restricting access to the Creation, Updating & Deletion of data resources using the login_required decorator in the case of view functions; or, in the case of class-based views, inheriting from the LoginRequiredMixin class.


## Planning

A trello board was set up for planning and development and as a group we came up with all user stories for the minimum viable product.

We created wireframes for the mobile version and desktop version. These wireframes were created with figma and can be found here: 

ERDs were developed and can be found here: 

## Build process

To start we group coded the base templates for both desktop and mobile based on the HTTP USER AGENT key on the request. By doing this we could display the content within this base depending the size of the viewport without having to have lots of css.

At the beginning of each day as a team we would have a stand up and assign user stories to work on throughout the day to ensure we would not be overlapping on features. We started from the most simple tasks, like setting up routing for each page and setting up the models before moving onto the more complex tasks.

I was responsible for creating the models one of which was a profile model as an extension of the user model built in with Django authentication:
 
`
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=200)
    location = models.CharField(max_length=7, default="")
    latitude = models.FloatField(default=0.0, null=True)
    longitude = models.FloatField(default=0.0, null=True)
    catchment = models.FloatField(default=100)

    def __str__(self):
        return self.user.username
`

The other models included the fundraiser model and the post model. Once I had created the models I could seed them with dummy data which would allow us to see future features working as we developed them. The seed.py creates dummy data and dummy locations for users, fundrs and posts.


I was also responsible for the create, delete and update functionality of fundrs. When a fundr is created the user puts in a postcode for the location of the fundr, this is then validated to be a legitimate UK postcode using ukpostcodeutils validation function and then converted into latitude and longitude using pgeocode. This is then stored on the fundr model which can then later be used to calculate the distance of the user from the fundraiser.

We take advantage of the browser inbuilt location service which is available on most modern browsers to send the user's current latitude and longitude to our server so that it can be stored on their profile: 
`
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
`

We can then find the distance between the user and a fundraiser by calculating the haversine distance. Luckily pgeocode has a built in haversine distance function:
` 
fundr_location = np.array([[fundr.lat, fundr.long]])
distance = np.round(pgeocode.haversine_distance(fundr_location, user_location),1)
`

On the explore page distance from user is calculated on all fundrs and then fitered based on the users catchment preference. These fundrs are then handed to the frontend as a list and displayed as a stack of cards. A user can press next to go to the next card or save to save that fundr. When the user presses save a post request is sent to the server and the current fundr is added to their *following* field.

I was solely responsible for building the home feed and implementing lazy loading. The home feed is a posts from fundrs that the current user is following in reverse chronological order of when they were posted (most recent first). I used pagification to seperate the posts into pages of three and based on the current page which was a parameter in the HTTP request it would send only the current page: 
`
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
`
On the frontend 





