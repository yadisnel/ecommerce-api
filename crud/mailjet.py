from mailjet_rest import Client

MJ_APIKEY_PUBLIC = 'dfdd133019fca75b99f9c6d9dbf86731'
MJ_APIKEY_PRIVATE = 'ded78784c3bcf5aec273a4b99ddac3f7'
EMAIL_CONFIRMATION_TEMPLATE_ID = 1326212


async def send_registry_email_to_user(email: str, username: str, security_code: str):
    confirmation_link = "https://api.acheapp.com/confirm_by_email?email=%s&code=%s" % (email, security_code)
    mailjet = Client(auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "ache.app.official@gmail.com",
                    "Name": "Equipo Aché"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": username
                    }
                ],
                "TemplateID": EMAIL_CONFIRMATION_TEMPLATE_ID,
                "TemplateLanguage": True,
                "Subject": "Aché - Activa tu cuenta",
                "Variables": {"confirmation_link": confirmation_link, "username": username}
            }
        ]
    }
    result = mailjet.send.create(data=data)
    status = result.status_code
    return status