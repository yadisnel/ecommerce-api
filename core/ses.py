import boto3
from botocore.exceptions import ClientError
from core.aws import load_config


async def send_registry_email_to_customer(email: str, security_code: str, locale):
    sender = "Ecommerce Team <yadisnel@gmail.com>"
    region_name = "eu-central-1"
    charset = "UTF-8"
    config = load_config()
    subject = "Confirmación de registro"

    # The email body for recipients with non-HTML email clients.
    body_text = """
        E-COMMERCE
        
        Welcome to the E-Commerce platfom. Please confirm you email address by clicking on the button below:
        <<CONFIRM EMAIL>> [{{var:confirmation_link}}]

        If the button doesn't work, please copy paste the following link in your browser:
        
        {{var:confirmation_link}}
        Cheers, The E-Commerce Team.
    """
    # The HTML body of the email.
    body_html = """
                <!doctype html>
                <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml"
                      xmlns:o="urn:schemas-microsoft-com:office:office">
                <head><title>Confirmación de registro</title><!--[if !mso]><!-- -->
                    <meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]-->
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <meta name="viewport" content="width=device-width,initial-scale=1">
                    <style type="text/css">#outlook a { padding:0; }
                          body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; }
                          table, td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; }
                          img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; }
                          p { display:block;margin:13px 0; }
                    </style>
                    <!--[if mso]>
                    <xml>
                        <o:OfficeDocumentSettings>
                            <o:AllowPNG/>
                            <o:PixelsPerInch>96</o:PixelsPerInch>
                        </o:OfficeDocumentSettings>
                    </xml>
                    <![endif]--><!--[if lte mso 11]>
                    <style type="text/css">
                          .mj-outlook-group-fix { width:100% !important; }
                        
                    </style>
                    <![endif]-->
                    <style type="text/css">@media only screen and (min-width:480px) {
                        .mj-column-per-100 { width:100% !important; max-width: 100%; }
                      }
                    </style>
                    <style type="text/css">[owa] .mj-column-per-100 { width:100% !important; max-width: 100%; }</style>
                    <style type="text/css"></style>
                </head>
                <body style="background-color:#F4F4F4;">
                <div style="background-color:#F4F4F4;"><!--[if mso | IE]>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600">
                        <tr>
                            <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
                    <div style="background:transparent;background-color:transparent;margin:0px auto;max-width:600px;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                               style="background:transparent;background-color:transparent;width:100%;">
                            <tbody>
                            <tr>
                                <td style="border:0px solid #ffffff;direction:ltr;font-size:0px;padding:20px 0px 20px 0px;padding-left:0px;padding-right:0px;text-align:center;">
                                    <!--[if mso | IE]>
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="" style="vertical-align:top;width:600px;"><![endif]-->
                                    <div class="mj-column-per-100 mj-outlook-group-fix"
                                         style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                                        <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                               style="vertical-align:top;" width="100%">
                                            <tr>
                                                <td align="left"
                                                    style="font-size:0px;padding:10px 25px;padding-top:0px;padding-bottom:0px;word-break:break-word;">
                                                    <div style="font-family:Arial, sans-serif;font-size:21px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;"></div>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    <!--[if mso | IE]></td></tr></table><![endif]--></td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                    <!--[if mso | IE]></td></tr></table>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600">
                        <tr>
                            <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
                                <v:rect style="width:600px;" xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false">
                                    <v:fill origin="0.5, 0" position="0.5, 0" src="http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png"
                                            color="transparent" type="tile"/>
                                    <v:textbox style="mso-fit-shape-to-text:true" inset="0,0,0,0"><![endif]-->
                    <div style="background:transparent url(http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png) top center / auto repeat;margin:0px auto;max-width:600px;">
                        <div style="line-height:0;font-size:0;">
                            <table align="center" background="http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png" border="0"
                                   cellpadding="0" cellspacing="0" role="presentation"
                                   style="background:transparent url(http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png) top center / auto repeat;width:100%;">
                                <tbody>
                                <tr>
                                    <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;"><!--[if mso | IE]>
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td class="" style="vertical-align:top;width:600px;"><![endif]-->
                                        <div class="mj-column-per-100 mj-outlook-group-fix"
                                             style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                                   style="vertical-align:top;" width="100%">
                                                <tr>
                                                    <td align="left"
                                                        style="font-size:0px;padding:10px 25px;padding-top:0px;padding-bottom:0px;word-break:break-word;">
                                                        <div style="font-family:Arial, sans-serif;font-size:21px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;">
                                                            <p class="text-build-content"
                                                               style="text-align: center; margin: 10px 0; margin-top: 10px; margin-bottom: 10px;"
                                                               data-testid="5R_D_Tee2"><span
                                                                    style="color:#ffffff;"><b>E-COMMERCE</b></span></p></div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <!--[if mso | IE]></td></tr></table><![endif]--></td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <!--[if mso | IE]></v:textbox></v:rect></td></tr></table>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600">
                        <tr>
                            <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
                    <div style="background:#ffffff;background-color:#ffffff;margin:0px auto;max-width:600px;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                               style="background:#ffffff;background-color:#ffffff;width:100%;">
                            <tbody>
                            <tr>
                                <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;"><!--[if mso | IE]>
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="" style="vertical-align:top;width:600px;"><![endif]-->
                                    <div class="mj-column-per-100 mj-outlook-group-fix"
                                         style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                                        <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                               style="vertical-align:top;" width="100%">
                                            <tr>
                                                <td align="left" vertical-align="top"
                                                    style="font-size:0px;padding:10px 25px;padding-top:0px;padding-bottom:0px;word-break:break-word;">
                                                    <div style="font-family:Arial, sans-serif;font-size:15px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;">
                                                        <p class="text-build-content" data-testid="xv-0xtEB7if2"
                                                           style="margin: 10px 0; margin-top: 10px; margin-bottom: 10px;"><span
                                                                style="color:#5e6977;font-family:Arial;font-size:15px;line-height:20px;">Welcome to the E-Commerce platfom. Please confirm you email address by clicking on the button below:</span>
                                                        </p></div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td align="center" vertical-align="top"
                                                    style="font-size:0px;padding:15px 30px;word-break:break-word;">
                                                    <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                                           style="border-collapse:separate;line-height:100%;">
                                                        <tr>
                                                            <td align="center" bgcolor="#41B8FF" role="presentation"
                                                                style="border:none;border-radius:0px;cursor:auto;mso-padding-alt:10px 25px;background:#41B8FF;"
                                                                valign="top"><a href="{{var:confirmation_link}}"
                                                                                style="display:inline-block;background:#41B8FF;color:#ffffff;font-family:Arial, sans-serif;font-size:15px;font-weight:normal;line-height:120%;margin:0;text-decoration:none;text-transform:none;padding:10px 25px;mso-padding-alt:0px;border-radius:0px;"
                                                                                target="_blank"><span
                                                                    style="background-color:#41B8FF;color:#ffffff;font-family:Arial;font-size:15px;"><b>CONFIRM EMAIL</b></span></a>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    <!--[if mso | IE]></td></tr></table><![endif]--></td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                    <!--[if mso | IE]></td></tr></table>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600">
                        <tr>
                            <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
                    <div style="background:#ffffff;background-color:#ffffff;margin:0px auto;max-width:600px;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                               style="background:#ffffff;background-color:#ffffff;width:100%;">
                            <tbody>
                            <tr>
                                <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;"><!--[if mso | IE]>
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="" style="vertical-align:top;width:600px;"><![endif]-->
                                    <div class="mj-column-per-100 mj-outlook-group-fix"
                                         style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                                        <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                               style="vertical-align:top;" width="100%">
                                            <tr>
                                                <td align="left"
                                                    style="font-size:0px;padding:10px 25px;padding-top:0px;padding-bottom:0px;word-break:break-word;">
                                                    <div style="font-family:Arial, sans-serif;font-size:15px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;">
                                                        <p class="text-build-content" data-testid="xKr5r-GHTySy"
                                                           style="margin: 10px 0; margin-top: 10px;"><span
                                                                style="color:#5e6977;font-family:Arial;font-size:15px;line-height:13px;">If the button doesn't work, please copy paste the following link in your browser:</span>
                                                        </p>
                                                        <p class="text-build-content" data-testid="xKr5r-GHTySy"
                                                           style="margin: 10px 0; margin-bottom: 10px;"><span
                                                                style="color:#5e6977;font-family:Arial;font-size:15px;line-height:13px;">{{var:confirmation_link}}</span>
                                                        </p></div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td align="left"
                                                    style="font-size:0px;padding:10px 25px;padding-top:15px;padding-bottom:0px;word-break:break-word;">
                                                    <div style="font-family:Arial, sans-serif;font-size:15px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;">
                                                        <p class="text-build-content" data-testid="88XSVC-9jHtY"
                                                           style="margin: 10px 0; margin-top: 10px; margin-bottom: 10px;"><span
                                                                style="color:#5e6977;font-family:Arial;font-size:15px;line-height:22px;">Cheers, The &nbsp;E-Commerce Team.</span>
                                                        </p></div>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    <!--[if mso | IE]></td></tr></table><![endif]--></td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                    <!--[if mso | IE]></td></tr></table>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600">
                        <tr>
                            <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
                                <v:rect style="width:600px;" xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false">
                                    <v:fill origin="0.5, 0" position="0.5, 0" src="http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png"
                                            color="transparent" type="tile"/>
                                    <v:textbox style="mso-fit-shape-to-text:true" inset="0,0,0,0"><![endif]-->
                    <div style="background:transparent url(http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png) top center / auto repeat;margin:0px auto;max-width:600px;">
                        <div style="line-height:0;font-size:0;">
                            <table align="center" background="http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png" border="0"
                                   cellpadding="0" cellspacing="0" role="presentation"
                                   style="background:transparent url(http://go.mailjet.com/tplimg/mtrq/b/ox8s/mg1qn.png) top center / auto repeat;width:100%;">
                                <tbody>
                                <tr>
                                    <td style="border:0px solid #ffffff;direction:ltr;font-size:0px;padding:0px 0px 0px 0px;padding-bottom:0px;padding-left:0px;padding-right:0px;padding-top:0px;text-align:center;">
                                        <!--[if mso | IE]>
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td class="" style="vertical-align:top;width:600px;"><![endif]-->
                                        <div class="mj-column-per-100 mj-outlook-group-fix"
                                             style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                                            <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                                   style="vertical-align:top;" width="100%">
                                                <tr>
                                                    <td align="left"
                                                        style="font-size:0px;padding:0px 23px 0px 23px;padding-top:0px;padding-right:23px;padding-bottom:0px;padding-left:23px;word-break:break-word;">
                                                        <div style="font-family:Arial, sans-serif;font-size:21px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;"></div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <!--[if mso | IE]></td></tr></table><![endif]--></td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <!--[if mso | IE]></v:textbox></v:rect></td></tr></table>
                    <table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:600px;" width="600">
                        <tr>
                            <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
                    <div style="background:transparent;background-color:transparent;margin:0px auto;max-width:600px;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                               style="background:transparent;background-color:transparent;width:100%;">
                            <tbody>
                            <tr>
                                <td style="border:0px solid #ffffff;direction:ltr;font-size:0px;padding:20px 0px 20px 0px;padding-left:0px;padding-right:0px;text-align:center;">
                                    <!--[if mso | IE]>
                                    <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td class="" style="vertical-align:top;width:600px;"><![endif]-->
                                    <div class="mj-column-per-100 mj-outlook-group-fix"
                                         style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                                        <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                               style="vertical-align:top;" width="100%">
                                            <tr>
                                                <td align="left"
                                                    style="font-size:0px;padding:10px 25px;padding-top:0px;padding-bottom:0px;word-break:break-word;">
                                                    <div style="font-family:Arial, sans-serif;font-size:21px;letter-spacing:normal;line-height:1;text-align:left;color:#000000;"></div>
                                                </td>
                                            </tr>
                                        </table>
                                    </div>
                                    <!--[if mso | IE]></td></tr></table><![endif]--></td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                    <!--[if mso | IE]></td></tr></table><![endif]--></div>
                </body>
                </html>
                """

    body_html = body_html.replace("{{var:confirmation_link}}",
                                  "https://app.ecommerce.com/confirm-by-email?email=%s&code=%s" % (
                                  email, security_code))
    body_text = body_text.replace("{{var:confirmation_link}}",
                                  "https://app.ecommerce.com/confirm-by-email?email=%s&code=%s" % (
                                  email, security_code))

    boto3.setup_default_session(aws_access_key_id=config['aws_access_key_id'],
                                aws_secret_access_key=config['aws_secret_access_key'])
    client = boto3.client('ses', region_name=region_name, )
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    email,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
