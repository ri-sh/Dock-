from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TheBlock.views.home', name='home'),
    # url(r'^TheBlock/', include('TheBlock.foo.urls')),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    #TODO clean all of this up (there's a lot of repeated info)
    (r'^desktop/alexpaino/$', 'userInfo.views.alex_paino'),
    (r'^tos/$', 'userInfo.views.tos'),
    (r'^mobile/$', 'userInfo.views.mobile'),

    #Beginning of userInfo views
    (r'^(rest|mobile|desktop)/users/login/$', 'userInfo.views.login'),
    (r'^(rest|mobile|desktop)/users/forgot_password/$', 'userInfo.views.forgotPassword'),
    (r'^(rest|mobile|desktop)/users/reset_password/$', 'userInfo.views.resetPassword'),
    (r'^(rest|mobile|desktop)/users/logout/$', 'userInfo.views.logout'),
    (r'^(rest|mobile|desktop)/users/(\d+)/friends/$', 'userInfo.views.getFriends'),
    (r'^(rest|mobile|desktop)/users/friend_requests/$', 'userInfo.views.getFriendRequests'),
    (r'^(rest|mobile|desktop)/users/request_friend/$', 'userInfo.views.requestFriend'),
    (r'^(rest|mobile|desktop)/users/confirm_friend/$', 'userInfo.views.confirmFriend'),
    (r'^(rest|mobile|desktop)/users/reject_friend_request/$', 'userInfo.views.rejectFriendRequest'),
    (r'^(rest|mobile|desktop)/users/remove_friend/$', 'userInfo.views.removeFriend'),
    (r'^(rest|mobile|desktop)/users/signup/$', 'userInfo.views.signup'),
    (r'^(rest|mobile|desktop)/users/edit_profile/$', 'userInfo.views.editProfile'),
    (r'^(rest|mobile|desktop)/users/(\d+)/profile/$', 'userInfo.views.getProfile'),
    (r'^(rest|mobile|desktop)/users/(\d+)/activity/(?:offset=)?(\d*)$', 'userInfo.views.getActivity'),
    (r'^(rest|mobile|desktop)/users/friend_feed/(?:offset=)?(\d*)$', 'userInfo.views.getFriendFeed'),
    (r'^(rest|mobile|desktop)/users/search/(.+)$', 'userInfo.views.search'),
    (r'^(rest|mobile|desktop)/users/set_profile_pic/$', 'userInfo.views.setProfilePic'),
    (r'^users/account/$', 'userInfo.views.viewAccount'),
    (r'^users/(\d+)/register/(.+)$', 'userInfo.views.confirmRegistration'),
    #Beginning of MessagesApp views
    (r'^(rest|mobile|desktop)/messaging/send_new_message/$', 'MessagesApp.views.sendNewMessage'),
    (r'^(rest|mobile|desktop)/messaging/send_reply/$', 'MessagesApp.views.sendReply'),
    (r'^(rest|mobile|desktop)/messaging/threads/$', 'MessagesApp.views.getThreads'),
    (r'^(rest|mobile|desktop)/messaging/num_unread_messages/$', 'MessagesApp.views.getNumUnreadMessages'),
    (r'^(rest|mobile|desktop)/messaging/threads/(\d+)$', 'MessagesApp.views.getThread'),
    #Beginning of PostsApp views
    (r'^(rest|mobile|desktop)/posts/create_post/$', 'PostsApp.views.createPost'),
    (r'^(rest|mobile|desktop)/(posts|events)/create_comment/$', 'PostsApp.views.createComment'),
    (r'^(rest|mobile|desktop)/posts/(\d+)/comments/(?:offset=)?(\d*)$', 'PostsApp.views.getComments'),
    #Beginning of ExtraInfo views
    (r'^(rest|mobile|desktop)/users/add_interest/$', 'SpecialInfoApp.views.addInterest'),
    (r'^(rest|mobile|desktop)/users/add_living_loc/$', 'SpecialInfoApp.views.addLivingLoc'),
    (r'^(rest|mobile|desktop)/users/add_school/$', 'SpecialInfoApp.views.addSchool'),
    (r'^(rest|mobile|desktop)/users/add_workplace/$', 'SpecialInfoApp.views.addWorkplace'),
    (r'^(rest|mobile|desktop)/users/remove_interest/$', 'SpecialInfoApp.views.removeInterest'),
    (r'^(rest|mobile|desktop)/users/remove_living_loc/$', 'SpecialInfoApp.views.removeLivingLoc'),
    (r'^(rest|mobile|desktop)/users/remove_school/$', 'SpecialInfoApp.views.removeSchool'),
    (r'^(rest|mobile|desktop)/users/remove_workplace/$', 'SpecialInfoApp.views.removeWorkplace'),
    (r'^(rest|mobile|desktop)/users/(\d+)/extra/$', 'SpecialInfoApp.views.getExtraInfo'),
    (r'^(rest|mobile|desktop)/users/(interests|living_locs|schools|workplaces)/(.+)$', 'SpecialInfoApp.views.searchExtraInfo'),
    #Beginning of BlockPages views
    (r'^(rest|mobile|desktop)/block/(?:offset=)?(\d*)$', 'BlockPages.views.myBlock'), #Block page of block current user is in
    (r'^(rest|mobile|desktop)/block/update/$', 'BlockPages.views.updateBlock'), #Updates block of current user
    (r'^(rest|mobile|desktop)/block/create_event/$', 'BlockPages.views.createEvent'),
    (r'^(rest|mobile|desktop)/block/attending/$', 'BlockPages.views.attending'),
    (r'^(rest|mobile|desktop)/block/events/(\d+)/(?:offset=)?(\d*)$', 'BlockPages.views.eventPage'),
    (r'^$', 'BlockPages.views.myBlock'),
    (r'^(rest|mobile|desktop)/block/current/(?:offset=)?(\d*)$', 'BlockPages.views.currentBlock'), #Preview of block page for viewer's current location
)
