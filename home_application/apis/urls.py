from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.apis.views',
    (r'^get_hosts$', 'get_hosts'),
    (r'^get_all_biz$', 'get_all_biz'),
    (r'^get_opt_list$', 'get_opt_list'),
    (r'^add_template$', 'add_template'),
    # (r'^exec_script$', 'exec_script'),
    # (r'^queue_push', 'queue_push'),
    # (r'^queue_remove', 'queue_remove'),
    # (r'^chart_api/(?P<ip>[0-9.]{8,16})/', 'chart_api')

)
