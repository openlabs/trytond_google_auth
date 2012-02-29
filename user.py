#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import logging

import gdata.service
import gdata.calendar.service

from trytond.model import ModelView, ModelSQL


logger = logging.getLogger('google_auth')

class User(ModelSQL, ModelView):
    '''
    Google Authentication for users
    '''

    _name = "res.user"

    def get_login(self, login, password):
        '''
        Return the user id if the google auth is sucessful

        :param login: the login name or email
        :param password: the password
        :return: integer
        '''
        if login == 'admin':
            return super(User, self).get_login(login, password)

        user_id, _x, _x = self._get_login(login)
        if not user_id:
            return 0
        user = self.browse(user_id)

        if user.email:
            # use google authentication
            logger.info("Use email for Google Auth Login: %s" % login)
            client = gdata.calendar.service.CalendarService()
            try:
                client.ClientLogin(user.email, password, source='Tryton')
                logger.info("Google auth was successful for %s" % login)
                return user_id
            except gdata.service.CaptchaRequired, exc:
                logging.error("%s for %s" % (exc, login))
                logging.info("Falling back to STD auth for %s" % login)
                return super(User, self).get_login(login, password)
            except gdata.service.BadAuthentication, exc:
                logger.error("%s for %s" % (exc, login))
                return 0

        # Fall back to standard login
        return super(User, self).get_login(login, password)

User()
