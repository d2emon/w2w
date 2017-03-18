CSRF_ENABLED = True
SECRET_KEY = 'ThereIsNoSpoon'
OPENID_PROVIDERS = [
                    {'name': "Google", 'url': "https://www.google.com/accounts/o8/id"},
                    {'name': "Yahoo", 'url': "https://me.yahoo.com"},
                    {'name': "AOL", 'url': "https://openid.aol.com/<username>"},
                    {'name': "Flickr", 'url': "https://www.flickr.com/<username>"},
                    {'name': "MyOpenID", 'url': "https://www.myopenid.com"},
                    ]