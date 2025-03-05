# Imports of the required python modules and libraries
######################################################
from django.urls import path
from . import views

urlpatterns = [
    # Main URL Route for Index
    path('', views.index, name='index'),

    # Complete URL Route for Manage-Sections
    path('manage/sections/', views.core_models_view, name='manage_sections'),

    # Main Table URL Route for Decree model
    path('decrees/', views.decree_list, name='decree_list'),
    
    # CRUD routes for Decree model
    path('decrees/add/', views.add_decree, name='add_decree'),
    path('decrees/edit/<int:document_id>/', views.edit_decree, name='edit_decree'),
    path('decrees/detail/<int:document_id>/', views.decree_detail, name='view_decree'),
    path('decrees/download/<int:document_id>/', views.download_decree, name='download_decree'),
    path('decrees/delete/<int:document_id>/', views.soft_delete_decree, name='delete_decree'),
    
    # Report route for Decree model
    path('reports/decree/', views.decree_report, name='decree_report'),

    # Main Table URL Route for Publication model
    path('publications/', views.publication_list, name='publication_list'),
    
    # CRUD routes for Publication model
    path('publications/add/', views.add_publication, name='add_publication'),
    path('publications/edit/<int:document_id>/', views.edit_publication, name='edit_publication'),
    path('publications/detail/<int:document_id>/', views.publication_detail, name='view_publication'),
    path('publications/download/<int:document_id>/', views.download_publication, name='download_publication'),
    path('publications/delete/<int:document_id>/', views.soft_delete_publication, name='delete_publication'),
    
    # Report route for Publication model
    path('reports/publication/', views.publication_report, name='publication_report'),
    
    # PDF generation routes for Publication model
    path('publications/pdf/<int:pub_id>/', views.gen_pub_pdf, name='gen_pub_pdf'),
    path('publications/pdf_f/<int:pub_id>/', views.gen_final_pub_pdf, name='gen_final_pub_pdf'),

    # Main Table URL Route for Objection model
    path('objections/', views.objection_list, name='objection_list'),
    
    # Secondary Table URL Route for picking a Publication to Object on
    path('objection-pub-pick/', views.objection_pub_pick, name='objection_pub_pick'),
    path('add_objection/<int:document_id>/', views.add_pub_objection, name='add_pub_objection'),
    path('objections/pdf/<int:obj_id>/', views.gen_obj_pdf, name='gen_obj_pdf'),
    path("check-status/", views.check_objection_status, name="check_objection_status"),
    
    # CRUD routes for Objection model
    path('objections/add//', views.add_objection, name='add_objection'),
    path('objections/edit/<int:document_id>/', views.edit_objection, name='edit_objection'),
    path('objections/detail/<int:document_id>/', views.objection_detail, name='view_objection'),
    path('objections/download/<int:document_id>/', views.download_objection, name='download_objection'),
    path('objections/download_r/<int:document_id>/', views.download_objection_receipt, name='download_objection_receipt'),
    path('objections/delete/<int:document_id>/', views.soft_delete_objection, name='delete_objection'),
    path('reports/objection/', views.objection_report, name='objection_report'),
    
    # PDF generation route for Objection model
    path('objections/pdf/<int:obj_id>/', views.gen_obj_pdf, name='gen_obj_pdf'),

    # Main Table URL Route for FormPlus model
    path('formplus/', views.formplus_list, name='formplus_list'),
    
    # CRUD routes for FormPlus model
    path('formplus/add/', views.add_edit_formplus, name='add_formplus'),
    path('formplus/edit/<int:document_id>/', views.add_edit_formplus, name='edit_formplus'),
    path('formplus/detail/<int:document_id>/', views.formplus_detail, name='view_formplus'),
    path('formplus/download_p/<int:document_id>/', views.download_formplus_pdf, name='download_formplus_pdf'),
    path('formplus/download_w/<int:document_id>/', views.download_formplus_word, name='download_formplus_word'),
    path('formplus/delete/<int:document_id>/', views.soft_delete_formplus, name='delete_formplus'),

    # AJAX autocomplete function for Publication model
    path('decree-autocomplete/', views.DecreeAutocompleteView.as_view(), name='decree-autocomplete'),
    
    # AJAX autocomplete function for Objection model
    path('publication-autocomplete/', views.PublicationAutocompleteView.as_view(), name='pub-autocomplete'),
    
    # AJAX Mark Complete functions
    path('update-status/<int:document_id>/', views.update_status, name='update_status'),
    path('confirm-objection-fee/<int:document_id>/', views.confirm_objection_fee, name='confirm_objection_fee'),
    path('decline-objection-fee/<int:document_id>/', views.decline_objection_fee, name='decline_objection_fee'),
    path('confirm-objection-status/<int:document_id>/', views.confirm_objection_status, name='confirm_objection_status'),
    path('decline-objection-status/<int:document_id>/', views.decline_objection_status, name='decline_objection_status'),
]