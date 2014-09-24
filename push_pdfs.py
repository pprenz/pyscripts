import os
import time
from glob import glob

import cloudfiles

file_pattern = '/home/areingold/*.pdf'

start_time = time.time()

connection = cloudfiles.get_connection('so1cloud', '987f28e47a60e8b3c39c845facfcfac7')
container = connection['pdfs']

existing_pdfs = set([o.lower() for o in container.list_objects()])

loaded_files = []

for filename in glob(file_pattern):
    basename = os.path.basename(filename).lower()
    if basename not in existing_pdfs:
        obj = container.create_object(basename)
        obj.content_type = 'application/pdf'
        obj.load_from_filename(filename)
        loaded_files.append(basename)

duration = time.time() - start_time

print 'Loaded %s files in %s ms' % (len(loaded_files), duration)
        