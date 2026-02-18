from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Asosiy sahifalar
    path('', views.index_view, name='home'),
    path('courses/', views.CoursesView.as_view(), name='courses'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:course_id>/test/', views.course_test_view, name='course_test'),
    path('courses/<int:course_id>/test/submit/', views.submit_test, name='submit_test'),
    path('module/<int:module_id>/complete/', views.complete_module, name='complete_module'),
    path('module/<int:module_id>/track-presentation/', views.track_presentation, name='track_presentation'),
    path('module/<int:module_id>/track-video/', views.track_video, name='track_video'),
    
    # E'lonlar
    path('announcement/<int:pk>/', views.announcement_detail_view, name='announcement_detail'),
    
    # Iqtidorli talabalar
    path('iqtidorli-sorovnoma/', views.IqtidorliSorovnomaView.as_view(), name='iqtidorli_sorovnoma'),
    path('iqtidorli-baza/', views.IqtidorliBazaView.as_view(), name='iqtidorli_baza'),
    
    # Stipendiyalar
    path('davlat-stipendiyalari/', views.DavlatStipendiyalariView.as_view(), name='davlat_stipendiyalari'),
    path('buxdu-stipendiyalari/', views.BuxDUStipendiyalariView.as_view(), name='buxdu_stipendiyalari'),
    path('buxdu-stipendiya-bazasi/', views.BuxDUStipendiyaBazasiView.as_view(), name='buxdu_stipendiya_bazasi'),
    
    # Olimpiadalar
    path('olimpiadalar/', views.OlimpiadalarView.as_view(), name='olimpiadalar'),
    path('xalqaro-olimpiadalar/', views.XalqaroOlimpiadalarView.as_view(), name='xalqaro_olimpiadalar'),
    path('respublika-olimpiadalar/', views.RespublikaOlimpiadalarView.as_view(), name='respublika_olimpiadalar'),
    path('onlayn-olimpiadalar/', views.OnlaynOlimpiadalarView.as_view(), name='onlayn_olimpiadalar'),
    path('buxdu-olimpiada-goliblari/', views.BuxDUOlimpiadaGoliblarView.as_view(), name='buxdu_olimpiada_goliblari'),
    path('buxdu-olimpiadalari/', views.BuxDUOlimpiadalarView.as_view(), name='buxdu_olimpiadalari'),
    path('buxdu-olimpiadalari/<int:pk>/', views.BuxDUOlimpiadaDetailView.as_view(), name='buxdu_olimpiada_detail'),
    
    # Ilmiy nashrlar
    path('mahalliy-oak-jurnallari/', views.MahalliyOAKJurnallariView.as_view(), name='mahalliy_oak_jurnallari'),
    path('xalqaro-oak-jurnallari/', views.XalqaroOAKJurnallariView.as_view(), name='xalqaro_oak_jurnallari'),
    path('xalqaro-konferensiyalar/', views.XalqaroKonferensiyalarView.as_view(), name='xalqaro_konferensiyalar'),
    path('respublika-konferensiyalar/', views.RespublikaKonferensiyalarView.as_view(), name='respublika_konferensiyalar'),
    path('dissertatsiyalar-banki/', views.DissertatsiyalarBankiView.as_view(), name='dissertatsiyalar_banki'),
    path('maqolalar-banki/', views.MaqolalarBankiView.as_view(), name='maqolalar_banki'),
    
    # Xizmatlar
    path('service/', views.ServiceView.as_view(), name='service'),
    path('maqola-jurnal-tavsiyasi/', views.MaqolaJurnalTavsiyasiView.as_view(), name='maqola_jurnal_tavsiyasi'),
    path('ilmiy-nizomlar/', views.IlmiyNizomlarView.as_view(), name='ilmiy_nizomlar'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Certificates
    path('certificate/<int:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    
    # Saralash testi (Assessment Test)
    path('assessment-test/', views.assessment_test_view, name='assessment_test'),
    path('assessment-test/start/', views.start_assessment_test, name='start_assessment_test'),
    path('assessment-test/submit/', views.submit_assessment_test, name='submit_assessment_test'),
]
