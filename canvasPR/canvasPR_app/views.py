"""
This Photo Roster LTI tool was build using the HUIT TLT bootstrap_lit_django
basic lti app from 
https://github.com/penzance/bootstrap_lit_django

This tool was adaped for use by:
Matthew Coser
IT Systems Coordinator
Harvard Kennedy School
Executive Education
matthew_coser@hks.harvard.edu
617-496-0319

This Canvas Photo Roster Tool can be re-worked and re-distributed as you wish
please credit the above parties.


"""


from django.shortcuts import (render, redirect)
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from ims_lti_py.tool_config import ToolConfig
from django.http import HttpResponse
from canvas_sdk.methods import enrollments
from canvas_sdk.methods import courses
from canvas_sdk.methods import users
from canvas_sdk.utils import get_all_list_data
from canvas_sdk.exceptions import CanvasAPIError
from canvas_sdk import RequestContext
import logging

logger = logging.getLogger(__name__)




SDK_CONTEXT = request_context = RequestContext(**settings.CANVAS_SDK_SETTINGS)

TOOL_NAME = "canvasPR_app"

@require_http_methods(['GET'])
def index(request):
    """
    Show the index file
    """
    return render(request, 'canvasPR_app/index.html')

@login_required()
@require_http_methods(['POST'])
def lti_launch(request):
    """
    This method is here to build the LTI_LAUNCH dictionary containing all
    the LTI parameters and place it into the session. This is nessesary as we 
    need to access these parameters throughout the application and they are only 
    available the first time the application loads.
    """
    if request.user.is_authenticated():
        return redirect('canvasPR_app:main')
    else:
        return render(request, 'canvasPR_app/error.html', {'message': 'Error: user is not authenticated!'})

@login_required()
@require_http_methods(['GET'])
def main(request):



    #get the course ID of current course
    canvas_course_id = request.session['LTI_LAUNCH'].get('custom_canvas_course_id')
    logger.debug('////////////////////////////////////>')
    logger.debug('canvas_course_id=%s' % canvas_course_id)
    logger.debug('////////////////////////////////////>')
    

    #call to get course name for roster header
    canvas_course_name = get_all_list_data(SDK_CONTEXT, courses.get_single_course_courses, canvas_course_id, "all_courses")
    logger.debug('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>')
    logger.debug(canvas_course_name)
    logger.debug('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>')

    #get a list of STUDENTS in the current course, we will use only the user_id from the list
    #the 'avatar_url' is just a required option, and we will actually use the avatar_url from the profile list below
    enrollmentGet = {}
    try:
        enrollmentGet = get_all_list_data(SDK_CONTEXT, courses.list_users_in_course_users, canvas_course_id, 'avatar_url', enrollment_type='student')
    except CanvasAPIError as api_error:
        logger.debug((canvas_course_id, api_error))
    
    #get a list of TEACHERS in the current course.  Should be automatically hidden with js in lti_view.thml, and can be toggled with a switch
    faculty = {}
    try:
        faculty = get_all_list_data(SDK_CONTEXT, courses.list_users_in_course_users, canvas_course_id, 'avatar_url', enrollment_type='teacher')
    except CanvasAPIError as api_error:
        logger.debug((canvas_course_id, api_error))
    
    #for each student user in the course, get their user_id
    userID = []
    for d in enrollmentGet:
        userIdSingle = d['id']
        userID.append(userIdSingle)
    logger.debug('*********************************************>')
    logger.debug('userID=%s' %userID)
    logger.debug('*********************************************>')

    facultyID = []
    for d in faculty:
        facultyIdSingle = d['id']
        facultyID.append(facultyIdSingle)
    logger.debug('++++++++++++++++++++++++++++++++++++++++++++++++>')
    logger.debug('facultyID=%s' %facultyID)
    logger.debug('++++++++++++++++++++++++++++++++++++++++++++++++>')


    #Run the user profile call for each student user_id we just got, 
    #and use what we need in the html
    userGet = []
    for l in userID:  
        try:
            studentFull = get_all_list_data(SDK_CONTEXT, users.get_user_profile, l)
            userGet.append(studentFull)
        except CanvasAPIError as api_error:
            logger.debug('CanvasAPIError in get_all_list_data enrollments.list_enrollments_courses call for canvas_course_id=%s. Exception=%s:' % (canvas_course_id, api_error))
   
    facultyGet = []
    for l in facultyID:  
        try:
            facultyFull = get_all_list_data(SDK_CONTEXT, users.get_user_profile, l)
            facultyGet.append(facultyFull)         
        except CanvasAPIError as api_error:
            logger.debug('CanvasAPIError in get_all_list_data enrollments.list_enrollments_courses call for canvas_course_id=%s. Exception=%s:' % (canvas_course_id, api_error))



    #dictionary definitions for the lti_view html
    return render(request, 'canvasPR_app/lti_view.html', {'request': request, 'pages': enrollmentGet, 'userGet': userGet, 'facultyGet': facultyGet, 'courseName': canvas_course_name})








@require_http_methods(['GET'])
def tool_config(request):
    """
    This produces a Canvas specific XML config that can be used to
    add this tool to the Canvas LMS
    """
    if request.is_secure():
        host = 'https://' + request.get_host()
    else:
        host = 'http://' + request.get_host()

    url = host + reverse('canvasPR_app:lti_launch')

    lti_tool_config = ToolConfig(
        title='Photo Roster - Test',
        launch_url=url,
        secure_launch_url=url,
    )
    account_nav_params = {
        'enabled': 'true',
        'visibility': 'admins',
        # optionally, supply a different URL for the link:
        # 'url': 'http://library.harvard.edu',
        'text': 'Photo Roster - Test',
    }
    lti_tool_config.set_ext_param('canvas.instructure.com', 'privacy_level', 'public')
    lti_tool_config.set_ext_param('canvas.instructure.com', 'course_navigation', account_nav_params)
    lti_tool_config.description = 'This LTI app shows all the LTI parameters'

    resp = HttpResponse(lti_tool_config.to_xml(), content_type='text/xml', status=200)
    return resp