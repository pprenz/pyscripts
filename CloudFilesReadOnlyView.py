import cloudfiles
from datetime import datetime
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from cloudfiles.errors import NoSuchContainer, NoSuchObject, ContainerNotPublic

def log_message(message):
    print message    

def rackspace_credentials():
    log_message( config.get('rackspace', 'user'))
    #log_message( config.get('rackspace', 'api_key'))
    log_message( config.getfloat('rackspace', 'timeout'))
    
    return (
            config.get('rackspace', 'user'),
             config.get('rackspace', 'api_key'),
              config.getfloat('rackspace', 'timeout'))


def get_connection():
    
    return cloudfiles.get_connection(*(rackspace_credentials()))
    
    
def get_container(conn, container_name):
    all_containers  = conn.get_all_containers()
    for c in all_containers:
        if c.name.lower() == container_name.lower():    
            return c
    return None

def make_public(cont, ttl_time):
    cont.make_public(ttl = ttl_time)
    return cont.public_uri()


def list_next_pdf_file(cont):
    #a = list_objects(i)
    base = ord('a')
    for alpha in range(26):
        key = base + alpha
        pdf_files = cont.list_objects_info(prefix=str(chr(key)))
        for pdf in pdf_files:
            #print pdf['name'], pdf['content_type']
            pdf_name = pdf['name']
            #print pdf['last_modified'], pdf.keys()
            yield (pdf_name, pdf['last_modified'], pdf['bytes'])           

def create_html_doc(filename, container_name, firstFilesOnly):
    log_message(".....trying to get pdf file information in a container: %s"%(container_name))
    connection = get_connection()
    container = get_container(connection, container_name)
    if not container:
        log_message("not found the container with the given name: %s"%(container_name))
        return
    ttl_in_sec = config.getint('rackspace', 'ttl')
    uri = make_public(container, ttl_in_sec)

    log_message("TTL is set to %d hours"%(ttl_in_sec / (60 * 60)))
    log_message("Container URI is %s"%(uri))
    htmlTag ="""<a href="%s">[%d]%s</a> &nbsp&nbsp&nbsp %s &nbsp&nbsp&nbsp %d<br>\r"""
    
    handle = open(filename, 'w')
    count = 0
    
    today = "%s"%(datetime.now().strftime('%Y-%m-%d %H.%M.%S'))

    header = """<h1> %s<br><br>Available cloud files on %s</h1><br>\r"""%(container_name, today)
    header2 = """<h2>File name %s Last modified %s Size</h2><br>\r"""%('&nbsp'*6, '&nbsp'*2)  
    handle.write(htmlDocBegin)
    handle.write(header)
    handle.write(header2)
    #handle.write(htmlTableHeader)
        
    for (pdf_name, modified, bytes) in list_next_pdf_file(container):
        count += 1
        file_path = uri + '/' + pdf_name
        handle.write(htmlTag%(file_path, count, pdf_name, modified[:16], bytes))
        if firstFilesOnly and count >=  firstFilesOnly:
            break
    #handle.write(htmlTableEnd)
    handle.write(htmlDocEnd)
    handle.close()
    log_message('Total number of pdf files available %d'%count)
    
htmlDocBegin ="""<html>
    <body>
"""

htmlDocEnd ="""</body>
</html>
"""

htmlTableHeader="""<TABLE BORDER="7" CELLPADDING="10">
<TR> <TH >File name</TH> <TH>Last modified</TH> <TH>Size</TH> </TR>"""
htmlTableEnd ="""</table>"""



if __name__ == '__main__':
    import sys
    import time
    from optparse import OptionParser

    parser = OptionParser()
    options, args = parser.parse_args()
    config_file = args[0]
    config = ConfigParser()
    config_search_path =  [
        config_file
    ]
    config_paths = config.read(config_search_path)
    if len(config_paths) == 0:
        raise Exception('Could not find config file in any of the following paths: %s' % repr(config_search_path))
    else:
        log_message(config_paths)
    if len(args) >= 2:
        container = args[1]
    else:
        container = config.get('rackspace', 'container')
    firstFilesCount = None
    try:
        firstFilesCount = config.getint('html', 'test_to_try_first_files')
    except NoOptionError, e:
        pass
    output_file = config.get('html', 'file_path')
    log_message('HTML document will be saved at %s'%(output_file))
    create_html_doc(output_file, container, firstFilesCount)







