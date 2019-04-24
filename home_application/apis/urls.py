from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.apis.views',
    (r'^get_all_biz$', 'get_all_biz'),
    (r'^add_template$', 'add_template'),
    (r'^search_task$','search_task'),
    (r'^search_template_list', 'search_template_list'),
    (r'^get_all_user$', 'get_all_user'),
    (r'^download_sample_template$', 'download_sample_template'),
    (r'^download_template/(\w+)', 'download_template'),
    (r'^create_task$', 'create_task'),
    (r'^get_task_content', 'get_task_content'),
    (r'^confirm', 'confirm'),
    (r'^delete_template', 'delete_template')
    # (r'^chart_api/(?P<ip>[0-9.]{8,16})/', 'chart_api')

)
