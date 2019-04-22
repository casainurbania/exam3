from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.apis.views',
    (r'^get_all_biz$', 'get_all_biz'),
    (r'^add_template$', 'add_template'),
    (r'^search_template_list', 'search_template_list'),
    (r'^get_all_user$', 'get_all_user')

    # (r'^queue_push', 'queue_push'),
    # (r'^queue_remove', 'queue_remove'),
    # (r'^chart_api/(?P<ip>[0-9.]{8,16})/', 'chart_api')

)
