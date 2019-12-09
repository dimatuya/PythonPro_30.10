from django.http import HttpResponse


def home_view(request):
    html = ''' <!DOCTYPE html>
        <html>
        <head>
        <title>Title of the document</title>
        </head>
        
        <body>
        <h1> Hello World!</h1>
        </body>

        </html> '''
    return HttpResponse(html)
