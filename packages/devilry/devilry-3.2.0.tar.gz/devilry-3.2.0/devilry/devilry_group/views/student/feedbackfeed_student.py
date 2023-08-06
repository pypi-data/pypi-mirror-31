# Python imports
from __future__ import unicode_literals

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit

from devilry.devilry_email.comment_email import comment_email
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.utils import setting_utils


class StudentFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Student view.
    Handles what should be rendered for a student
    on the FeedbackFeed.
    """
    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/student_commentform_headingtext.django.html'

    def get_hard_deadline_info_text(self):
        return setting_utils.get_devilry_hard_deadline_info_text(
            setting_name='DEVILRY_HARD_DEADLINE_INFO_FOR_STUDENTS')

    def get_devilryrole(self):
        """
        Get the devilryrole for the view.

        Returns:
            str: ``student`` as devilryrole.
        """
        return 'student'

    def get_buttons(self):
        buttons = super(StudentFeedbackFeedView, self).get_buttons()
        buttons.extend([
            PrimarySubmit(
                'student_add_comment',
                _('Add delivery or question')
            )
        ])
        return buttons

    def set_automatic_attributes(self, obj):
        super(StudentFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'student'
        obj.published_datetime = timezone.now()

    def __send_comment_email(self, comment):
        comment_email.bulk_send_comment_email_to_students_and_examiners(
            group_id=self.request.cradmin_role.id,
            comment_user_id=comment.user.id,
            published_datetime=comment.published_datetime,
            domain_url_start=self.request.build_absolute_uri('/'))

    def save_object(self, form, commit=False):
        comment = super(StudentFeedbackFeedView, self).save_object(form=form, commit=commit)
        self.__send_comment_email(comment=comment)
        return super(StudentFeedbackFeedView, self).save_object(form, commit=True)


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ensure_csrf_cookie(StudentFeedbackFeedView.as_view()),
            name=crapp.INDEXVIEW_NAME),
    ]
