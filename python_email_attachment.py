def send_assignments(date, url_template, target_vendor_id=None):
    subject_template = "SO1 lesson assignments for %(date_id)s"
    message_template = "Here is your lesson assignment file for %(full_date)s:\n\n%(url)s"

    date_id = date.strftime('%Y-%m-%d')

    for vendor in Vendor.with_assignments(date):
        if target_vendor_id is None or (target_vendor_id is not None and vendor.id == target_vendor_id):

            url = 'http://so1live.com/vendor/%s/so1_vendor_export-%s.csv' % (vendor.api_token, date_id)
            template_values = {
                'full_date': date.strftime('%a, %b %d, %Y'),
                'date_id': date_id,
                'url': url
            }

            subject = subject_template % template_values
            body = message_template % template_values

            print 'Emailing %s (%s)' % (vendor.name, ', '.join(vendor.contact_emails))

            send_mail(
                server_addr='smtp.gmail.com',
                server_port=587,
                username='vendor-export@so1live.com',
                password='sharingiscaring',
                from_name='SO1 Vendor Export',
                from_addr='vendor-export@so1live.com',
                to_addr=vendor.contact_emails,
                subject=subject,
                body=body
            )
