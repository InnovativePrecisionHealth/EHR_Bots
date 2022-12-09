import base64
import datetime

def decode_and_save(b64str, filename, mrn):
    date=datetime.datetime.today().strftime('%Y-%m-%d')
    filename_new = 'PROs for '+str(mrn)+' on '+str(date)+'.pdf'

    with open(filename_new, 'wb') as pdf:
        pdf.write(base64.b64decode(b64str))
    print (filename_new+" generated and ready to upload")
    return filename_new

def new_filename(filename, mrn):
    date=datetime.datetime.today().strftime('%Y-%m-%d')
    filename_new = 'PROs for '+str(mrn)+' on '+str(date)+'.pdf'
