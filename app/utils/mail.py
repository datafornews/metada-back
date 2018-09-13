import sendgrid
import os
from sendgrid.helpers.mail import *


def send_register_email(new_user):
    try:
        sg = sendgrid.SendGridAPIClient(
            apikey=os.getenv('SENDGRID_API_KEY'))
        from_email = Email("no-repy@metada.org", name='Metada No Reply')
        subject = "Verify your Metada account"
        to_email = Email("vsch@protonmail.com")
        # to_email = Email(new_user.email)
        content = Content(
            "text/html",
            """
            Hello, {}!<br/>
            To verify your OOP account, go to this address:
            <strong>
                localhost:5000/verify/{}
            </strong>
            """.format(new_user.username, new_user.verified_email.link))
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        return response
    except Exception as e:
        print(e)
        return ''
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)
