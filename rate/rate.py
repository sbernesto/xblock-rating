# coding: utf-8
"""
Providing feedback and rating.
This can be put anywhere inside a course. Multiple rating at same page is also allowed.
"""
import random
import emot
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Float
from xblock.fragment import Fragment
from eventtracking import tracker as tk
from .utils import *

from django.utils import translation


@XBlock.needs('i18n')
class RatingXBlock(XBlock):
    """
    An XBlock for collecting rating and feedback from students
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # This is a list of prompts. If we have multiple elements in the
    # list, one will be chosen at random. This is currently not
    # exposed in the UX. If the prompt is missing any portions, we
    # will default to the ones in default_prompt.
    prompts = List(
        default=[{
            'text': "Por favor envianos tus comentarios sobre esta sección",
            'rating': "Califique su experiencia general",
            'error': "¡Por favor, llene los comentarios antes de enviar!"
        }],
        scope=Scope.settings,
        help="Input text feedback here",
        xml_node=True
    )

    prompt_choice = Integer(
        default=-1,
        scope=Scope.user_info,
        help="Random number generated for p. -1 if uninitialized"
    )

    show_textarea = Integer(
        default=1,
        scope=Scope.settings,
        help="Option for whether to show text feedback. 1=Yes / 0=No"
    )

    user_vote = Integer(
        default=-1,
        scope=Scope.user_state,
        help="How user voted. -1 if didn't vote"
    )

    p = Float(
        default=100,
        scope=Scope.settings,
        help="What percent of the time should this show?"
    )

    p_user = Float(
        default=-1,
        scope=Scope.user_info,
        help="Random number generated for p. -1 if uninitialized"
    )

    rating_aggregate = List(
        default=None,
        scope=Scope.user_state_summary,
        help="A list of user votes"
    )

    user_freeform = String(
        default="",
        scope=Scope.user_state,
        help="Feedback")

    display_name = String(
        display_name="Display Name",
        default="Rating With Text Feedback",
        scope=Scope.settings
    )

    def get_prompt(self, index):
        """ 
        Return the current prompt dictionary, doing appropriate
        randomization if necessary, and falling back to defaults when
        necessary.
        """
        # _ = self.runtime.service(self, 'i18n').ugettext
        language = translation.get_language()

        if language.split('-')[0] == 'fr':

            prompt = {'text': "S'il vous plaît nous fournir des commentaires sur cette section",
                      'rating': "S'il vous plaît noter que votre expérience avec cette section",
                      'error': "S'il vous plaît remplir quelques commentaires avant de soumettre!",
                      'mouseovers': ["Excellent", "Bon", "Moyen", "Passable", "Mauvais"]}

        else:
            prompt = {'text': "Please provide us feedback on this section.",
                      'rating': "Please rate your overall experience with this section.",
                      'error': "Please fill in some feedback before submitting!",
                      'mouseovers': ["Excellent", "Good", "Average", "Fair", "Poor"]}

        icons = [u"😁", u"😊", u"😐", u"😞", u"😭"]

        prompt.update(self.prompts[index])
        prompt.update({'icons': icons})
        return prompt

    def student_view(self, context=None):
        """
        The primary view of the RatingXBlock, shown to students
        when viewing courses.
        """
        # _ = self.runtime.service(self, 'i18n').ugettext
        language = translation.get_language().split('-')[0]

        # Figure out which prompt we show. We set self.prompt_choice to
        # the index of the prompt. We set it if it is out of range (either
        # uninitiailized, or incorrect due to changing list length). Then,
        # we grab the prompt, prepopulated with defaults.
        if self.prompt_choice < 0 or self.prompt_choice >= len(self.prompts):
            self.prompt_choice = random.randint(0, len(self.prompts) - 1)
        prompt = self.get_prompt(self.prompt_choice)

        indexes = range(len(prompt['icons']))
        active_vote = ["checked" if i == self.user_vote else "" for i in indexes]

        scale_items = zip(prompt['mouseovers'], prompt['icons'], indexes, active_vote)
        rated = False
        if self.user_vote > -1 or self.user_freeform:
            rated = True

        context = {
            'user_freeform': self.user_freeform,
            'text_prompt': prompt['text'],
            'rating_prompt': prompt['rating'],
            'rated': rated,
            'rating': self.user_vote,
            'show_textarea': self.show_textarea,
            'scale_items': scale_items,
            'language': language
        }

        # We initialize self.p_user if not initialized -- this sets whether
        # or not we show it. From there, if it is less than odds of showing,
        # we set the fragment to the rendered XBlock. Otherwise, we return
        # empty HTML. There ought to be a way to return None, but XBlocks
        # doesn't support that.
        if self.p_user == -1:
            self.p_user = random.uniform(0, 100)
        frag = Fragment(u"")

        frag.add_content(render_template('static/html/rating.html', context))
        # Finally, we do the standard JS+CSS boilerplate. Honestly, XBlocks
        # ought to have a sane default here.
        frag.add_css(load_resource("static/css/rating.css"))
        frag.add_javascript(load_resource("static/js/src/rating.js"))
        frag.initialize_js('RatingXBlock')
        return frag

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        options = self.get_prompt(self.prompt_choice)
        options['title'] = self.display_name
        options['show_textarea'] = self.show_textarea
        frag = Fragment()
        frag.add_content(render_template("static/html/studio_view.html", options))
        frag.add_javascript(load_resource("static/js/src/studio.js"))
        frag.initialize_js('RatingXBlock')
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.prompts[self.prompt_choice]['text'] = data.get('text')
        self.prompts[self.prompt_choice]['rating'] = data.get('rating')
        self.display_name = data.get('title')
        self.prompts[self.prompt_choice]['error'] = data.get('error')
        self.show_textarea = data.get('show_textarea')
        return {'result': 'success'}

    def handle_rating(self, data):
        """
        Handle voting
        """
        # prompt_choice is initialized by student view.
        # Ideally, we'd break this out into a function.
        prompt = self.get_prompt(self.prompt_choice)

        # Make sure we're initialized
        if not self.rating_aggregate:
            self.rating_aggregate = [0] * len(prompt['mouseovers'])

        # Remove old vote if we voted before
        if self.user_vote != -1:
            self.rating_aggregate[self.user_vote] -= 1

        self.user_vote = data['rating']
        self.rating_aggregate[self.user_vote] += 1

    @XBlock.json_handler
    def feedback(self, data, suffix=''):
        valid = False
        if 'text' in data:
            # tracker.emit('edx.ratingxblock.text_feedback',{'old_text': self.user_freeform,'new_text': data['text']})
            self.user_freeform = data['text']
            valid = True
        if 'rating' in data:
            # tracker.emit('edx.ratexblock.rating',{'old_vote': self.user_vote,'new_vote': data['vote']})
            self.handle_rating(data)
            valid = True

        # _ = self.runtime.service(self, 'i18n').ugettext
        if valid:
            return {"success": True}
        else:
            return {"success": False, "response": self.get_prompt(self.prompt_choice)['error']}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("RatingXBlock",
             """<rate p="50"/>
             """),
            ("Multiple RatingXBlock",
             """<vertical_demo>
                <rate p="50"/>
                <rate p="50"/>
                <rate p="50"/>
                </vertical_demo>
             """),
        ]
